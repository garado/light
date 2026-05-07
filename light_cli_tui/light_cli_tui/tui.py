"""TUI for managing Light devices."""

import queue
import threading
from concurrent.futures import Future
from dataclasses import dataclass
from typing import Any, Callable

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.screen import ModalScreen
from textual.widget import Widget
from textual.widgets import Button, ContentSwitcher, DataTable, Input, Label, Static

from light_api.client import Light
from light_api.music import LightTrack, SortMode

SORT_CYCLE: list[SortMode] = [
    SortMode.RANK,
    SortMode.ARTIST_ASC,
    SortMode.ARTIST_DESC,
    SortMode.TITLE_ASC,
    SortMode.TITLE_DESC,
    SortMode.ARTIST_ALBUM_ASC,
    SortMode.ARTIST_ALBUM_DESC,
]

SORT_LABELS: dict[SortMode, str] = {
    SortMode.RANK: "manual",
    SortMode.ARTIST_ASC: "artist a-z",
    SortMode.ARTIST_DESC: "artist z-a",
    SortMode.TITLE_ASC: "title a-z",
    SortMode.TITLE_DESC: "title z-a",
    SortMode.ARTIST_ALBUM_ASC: "artist+album a-z",
    SortMode.ARTIST_ALBUM_DESC: "artist+album z-a",
}

TABS = ["music", "notes", "podcasts"]


@dataclass
class LightConfig:
    email: str | None = None
    email_file: str | None = None
    password: str | None = None
    password_file: str | None = None
    phone: str | None = None
    phone_file: str | None = None


class LightThread:
    """Runs a Light instance in a dedicated background thread."""

    def __init__(self, config: LightConfig) -> None:
        self._config = config
        self._queue: queue.Queue[tuple[Callable[[Light], Any], Future[Any]] | None] = (
            queue.Queue()
        )
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._ready = threading.Event()
        self._error: BaseException | None = None

    def start(self) -> None:
        self._thread.start()
        self._ready.wait()
        if self._error is not None:
            raise self._error

    def _run(self) -> None:
        try:
            with Light(
                email=self._config.email,
                email_file=self._config.email_file,
                password=self._config.password,
                password_file=self._config.password_file,
                phone=self._config.phone,
                phone_file=self._config.phone_file,
            ) as light:
                self._ready.set()
                while True:
                    item = self._queue.get()
                    if item is None:
                        break
                    func, future = item
                    try:
                        future.set_result(func(light))
                    except Exception as e:
                        future.set_exception(e)
        except BaseException as e:
            self._error = e
            self._ready.set()

    def submit(self, func: Callable[[Light], Any]) -> Any:
        future: Future[Any] = Future()
        self._queue.put((func, future))
        return future.result()

    def shutdown(self) -> None:
        self._queue.put(None)
        self._thread.join()


class ConfirmScreen(ModalScreen[bool]):
    CSS = """
    ConfirmScreen { align: center middle; }
    #dialog {
        padding: 1 3;
        background: $surface;
        border: tall $primary;
        width: auto;
        height: auto;
    }
    #buttons { margin-top: 1; align: center middle; width: auto; }
    Button { margin: 0 1; }
    """

    def __init__(self, message: str) -> None:
        super().__init__()
        self._message = message

    def compose(self) -> ComposeResult:
        with Static(id="dialog"):
            yield Label(self._message)
            with Static(id="buttons"):
                yield Button("yes", variant="error", id="yes")
                yield Button("no", variant="default", id="no")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "yes")


class EditScreen(ModalScreen[tuple[str, str, str] | None]):
    CSS = """
    EditScreen { align: center middle; }
    #dialog {
        padding: 1 3;
        background: $surface;
        border: tall $primary;
        width: 50;
        height: auto;
    }
    Input { margin-top: 1; }
    #buttons { margin-top: 1; align: center middle; width: auto; }
    Button { margin: 0 1; }
    """

    def __init__(self, track: LightTrack) -> None:
        super().__init__()
        self._track = track

    def compose(self) -> ComposeResult:
        with Static(id="dialog"):
            yield Label("edit track")
            yield Input(value=self._track.title, placeholder="title", id="title")
            yield Input(value=self._track.artist, placeholder="artist", id="artist")
            yield Input(value=self._track.album, placeholder="album", id="album")
            with Static(id="buttons"):
                yield Button("save", variant="primary", id="save")
                yield Button("cancel", variant="default", id="cancel")

    def on_mount(self) -> None:
        self.query_one("#title", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(self._get_values() if event.button.id == "save" else None)

    def on_key(self, event) -> None:
        if event.key == "enter":
            self.dismiss(self._get_values())
        elif event.key == "escape":
            self.dismiss(None)

    def _get_values(self) -> tuple[str, str, str]:
        return (
            self.query_one("#title", Input).value,
            self.query_one("#artist", Input).value,
            self.query_one("#album", Input).value,
        )


class MusicPane(Widget):
    def __init__(self) -> None:
        super().__init__(id="music")
        self._tracks: list[LightTrack] = []
        self._filtered_tracks: list[LightTrack] = []
        self._sort_index: int = 0
        self._pending_sort_index: int | None = None
        self._last_key: str = ""
        self._count_str: str = ""
        self._search_mode: bool = False

    @property
    def _pw(self) -> LightThread | None:
        return self.app._pw  # type: ignore[attr-defined]

    def compose(self) -> ComposeResult:
        yield Static("", id="music-header")
        yield DataTable()
        yield Input(placeholder="/  search...", id="search-bar")

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.cursor_type = "row"
        table.show_header = True
        table.add_columns("title", "artist", "album")
        self.query_one("#search-bar", Input).display = False
        table.focus()

    def _set_status(self, text: str) -> None:
        self.app.query_one("#status", Static).update(text)

    def _set_header(self, track: LightTrack | None) -> None:
        if track is None:
            self.query_one("#music-header", Static).update("")
            return
        parts = [track.title, track.artist]
        if track.album:
            parts.append(track.album)
        self.query_one("#music-header", Static).update("  ·  ".join(parts))

    def _populate_table(self, tracks: list[LightTrack]) -> None:
        table = self.query_one(DataTable)
        table.clear()
        for track in tracks:
            table.add_row(track.title, track.artist, track.album, key=track.audio_id)

    # --- search ---

    def _start_search(self) -> None:
        self._search_mode = True
        search = self.query_one("#search-bar", Input)
        search.display = True
        search.value = ""
        search.focus()

    def _stop_search(self) -> None:
        self._search_mode = False
        search = self.query_one("#search-bar", Input)
        search.display = False
        search.value = ""
        self._filtered_tracks = list(self._tracks)
        self._populate_table(self._filtered_tracks)
        self.query_one(DataTable).focus()

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id != "search-bar":
            return
        q = event.value.lower()
        self._filtered_tracks = (
            [
                t for t in self._tracks
                if q in t.title.lower() or q in t.artist.lower() or q in t.album.lower()
            ]
            if q else list(self._tracks)
        )
        self._populate_table(self._filtered_tracks)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "search-bar":
            self._stop_search()

    # --- key handling ---

    def on_key(self, event) -> None:
        if self._search_mode:
            if event.key == "escape":
                self._stop_search()
                event.stop()
            return

        key = event.key
        table = self.query_one(DataTable)

        if self._pending_sort_index is not None:
            if key == "enter":
                event.stop()
                pending = self._pending_sort_index
                sort_mode = SORT_CYCLE[pending]
                label = SORT_LABELS[sort_mode]

                def on_confirm(confirmed: bool) -> None:
                    if not confirmed:
                        self._pending_sort_index = None
                        self._update_status()
                        return
                    self._sort_index = pending
                    self._pending_sort_index = None
                    self._set_status(f"sorting by {label}...")
                    self.app.run_worker(
                        lambda: self._do_sort(sort_mode), exclusive=True, thread=True
                    )

                self.app.push_screen(ConfirmScreen(f"apply sort: {label}?"), on_confirm)
                self._last_key = key
                return
            elif key == "escape":
                event.stop()
                self._pending_sort_index = None
                self._update_status()
                self._last_key = key
                return

        if key.isdigit():
            self._count_str += key
            event.stop()
            return

        count = int(self._count_str) if self._count_str else 1
        self._count_str = ""

        if key == "j":
            for _ in range(count):
                table.action_cursor_down()
            event.stop()
        elif key == "k":
            for _ in range(count):
                table.action_cursor_up()
            event.stop()
        elif key == "g":
            if self._last_key == "g":
                table.move_cursor(row=0)
                self._last_key = ""
            else:
                self._last_key = key
            event.stop()
            return
        elif key == "G":
            table.move_cursor(row=table.row_count - 1)
            event.stop()
        elif key in ("ctrl+d", "ctrl+f"):
            table.action_scroll_page_down()
            event.stop()
        elif key in ("ctrl+u", "ctrl+b"):
            table.action_scroll_page_up()
            event.stop()
        elif key == "J":
            self._move_track(1)
            event.stop()
        elif key == "K":
            self._move_track(-1)
            event.stop()
        elif key == "r":
            self.action_refresh()
            event.stop()
        elif key == "s":
            self._cycle_sort()
            event.stop()
        elif key == "d":
            self.action_delete()
            event.stop()
        elif key == "e":
            self.action_edit()
            event.stop()
        elif key == "slash":
            self._start_search()
            event.stop()
        elif key == "h":
            self.app.action_prev_tab()  # type: ignore[attr-defined]
            event.stop()
        elif key == "l":
            self.app.action_next_tab()  # type: ignore[attr-defined]
            event.stop()

        self._last_key = key

    def _move_track(self, direction: int) -> None:
        if self._pw is None:
            return
        table = self.query_one(DataTable)
        row_key = table.coordinate_to_cell_key(table.cursor_coordinate).row_key
        audio_id = str(row_key.value)
        i = next((idx for idx, t in enumerate(self._tracks) if t.audio_id == audio_id), None)
        if i is None:
            return
        j = i + direction
        if j < 0 or j >= len(self._tracks):
            return
        track = self._tracks[i]
        self._tracks[i], self._tracks[j] = self._tracks[j], self._tracks[i]
        self._populate_table(self._tracks)
        table.move_cursor(row=j)
        self.app.run_worker(lambda: self._do_move(track, j), exclusive=True, thread=True)

    def _do_move(self, track: LightTrack, new_position: int) -> None:
        from open_api_specification_client.api.default import patch_api_playlist_items_playlist_item_id
        from open_api_specification_client.models import (
            PatchApiPlaylistItemsPlaylistItemIdBody,
            PatchApiPlaylistItemsPlaylistItemIdBodyData,
            PatchApiPlaylistItemsPlaylistItemIdBodyDataAttributes,
            PatchApiPlaylistItemsPlaylistItemIdBodyDataType,
        )
        assert self._pw is not None

        def _move(light):
            resp = patch_api_playlist_items_playlist_item_id.sync_detailed(
                playlist_item_id=track.playlist_item_id,
                client=light._api_client,
                body=PatchApiPlaylistItemsPlaylistItemIdBody(
                    data=PatchApiPlaylistItemsPlaylistItemIdBodyData(
                        id=track.playlist_item_id,
                        type_=PatchApiPlaylistItemsPlaylistItemIdBodyDataType.PLAYLIST_ITEMS,
                        attributes=PatchApiPlaylistItemsPlaylistItemIdBodyDataAttributes(
                            position=new_position,
                        ),
                    )
                ),
            )
            if not (200 <= resp.status_code < 300):
                raise RuntimeError(f"move track: {resp.status_code}")

        self._pw.submit(_move)

    def action_refresh(self) -> None:
        if self._pw is None:
            return
        self._set_status("loading...")
        self.app.run_worker(self._load_tracks, exclusive=True, thread=True)

    def _load_tracks(self) -> None:
        assert self._pw is not None
        tracks = self._pw.submit(lambda light: light.music.get_tracks())
        sort_mode = self._pw.submit(lambda light: light.music.get_sort_mode())
        self.app.call_from_thread(self._on_tracks_loaded, tracks, sort_mode)

    def _on_tracks_loaded(self, tracks: list[LightTrack], sort_mode: SortMode | None = None) -> None:
        self._tracks = tracks
        self._filtered_tracks = list(tracks)
        self._pending_sort_index = None
        if sort_mode is not None and sort_mode in SORT_CYCLE:
            self._sort_index = SORT_CYCLE.index(sort_mode)
        self._populate_table(tracks)
        self._update_status()
        self._set_header(tracks[0] if tracks else None)

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        if event.row_key is None:
            return
        audio_id = str(event.row_key.value)
        track = next((t for t in self._tracks if t.audio_id == audio_id), None)
        self._set_header(track)

    def _update_status(self) -> None:
        sort_label = SORT_LABELS[SORT_CYCLE[self._sort_index]]
        if self._pending_sort_index is not None:
            pending_label = SORT_LABELS[SORT_CYCLE[self._pending_sort_index]]
            self._set_status(
                f"{len(self._tracks)} tracks  |  sort: {sort_label} → {pending_label}  |  s cycle  enter apply  esc cancel"
            )
        else:
            self._set_status(
                f"{len(self._tracks)} tracks  |  sort: {sort_label}  |  r refresh  s sort  d delete  e edit  / search  h/l tabs  q quit"
            )

    def _cycle_sort(self) -> None:
        if self._pw is None:
            return
        base = self._pending_sort_index if self._pending_sort_index is not None else self._sort_index
        self._pending_sort_index = (base + 1) % len(SORT_CYCLE)
        self._update_status()

    def _do_sort(self, sort_mode: SortMode) -> None:
        assert self._pw is not None
        self._pw.submit(lambda light: light.music.set_sort_mode(sort_mode))
        tracks = self._pw.submit(lambda light: light.music.get_tracks())
        self.app.call_from_thread(self._on_tracks_loaded, tracks)

    def action_delete(self) -> None:
        if self._pw is None:
            return
        table = self.query_one(DataTable)
        if table.row_count == 0:
            return
        row_key = table.coordinate_to_cell_key(table.cursor_coordinate).row_key
        audio_id = str(row_key.value)
        track = next((t for t in self._tracks if t.audio_id == audio_id), None)
        if track is None:
            return
        self._set_status(f"deleting: {track.title}...")
        self.app.run_worker(lambda: self._do_delete(track), exclusive=True, thread=True)

    def _do_delete(self, track: LightTrack) -> None:
        assert self._pw is not None
        self._pw.submit(
            lambda light: light.music.delete_tracks_predicate(
                lambda t: t.audio_id == track.audio_id
            )
        )
        tracks = self._pw.submit(lambda light: light.music.get_tracks())
        self.app.call_from_thread(self._on_tracks_loaded, tracks)

    def action_edit(self) -> None:
        if self._pw is None:
            return
        table = self.query_one(DataTable)
        if table.row_count == 0:
            return
        row_key = table.coordinate_to_cell_key(table.cursor_coordinate).row_key
        audio_id = str(row_key.value)
        track = next((t for t in self._tracks if t.audio_id == audio_id), None)
        if track is None:
            return

        def on_edit(result: tuple[str, str, str] | None) -> None:
            if result is None:
                return
            new_title, new_artist, new_album = result
            self._set_status(f"saving: {new_title}...")
            self.app.run_worker(
                lambda: self._do_edit(track, new_title, new_artist, new_album),
                exclusive=True,
                thread=True,
            )

        self.app.push_screen(EditScreen(track), on_edit)

    def _do_edit(self, track: LightTrack, title: str, artist: str, album: str) -> None:
        assert self._pw is not None
        self._pw.submit(
            lambda light: light.music.update_track_metadata(
                track.audio_id, title=title, artist=artist, album=album or None
            )
        )
        tracks = self._pw.submit(lambda light: light.music.get_tracks())
        self.app.call_from_thread(self._on_tracks_loaded, tracks)


class NotesPane(Widget):
    def __init__(self) -> None:
        super().__init__(id="notes")

    def compose(self) -> ComposeResult:
        yield Static("notes coming soon")


class PodcastsPane(Widget):
    def __init__(self) -> None:
        super().__init__(id="podcasts")

    def compose(self) -> ComposeResult:
        yield Static("podcasts coming soon")


class LightApp(App):
    CSS = """
    LightApp { layout: vertical; }

    #tab-bar {
        height: 1;
        background: $surface;
    }
    .tab-label {
        padding: 0 2;
        color: $text-muted;
    }
    .tab-label.active {
        color: $text;
        background: $boost;
    }

    #music-header {
        height: 2;
        padding: 0 1;
        background: $boost;
        color: $text;
    }
    ContentSwitcher { height: 1fr; margin: 0; padding: 0; }
    MusicPane { layout: vertical; height: 1fr; margin: 0; padding: 0; overflow: hidden hidden; }
    DataTable { height: 1fr; }
    #search-bar {
        height: 1;
        border: none;
        padding: 0 1;
    }

    #status {
        height: 1;
        padding: 0 1;
        color: $text-muted;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "quit"),
        Binding("ctrl+c", "quit", "quit", show=False),
        Binding("h", "prev_tab", show=False),
        Binding("l", "next_tab", show=False),
    ]

    def __init__(self, config: LightConfig) -> None:
        super().__init__()
        self._config = config
        self._pw: LightThread | None = None
        self._tab_index: int = 0

    def compose(self) -> ComposeResult:
        with Horizontal(id="tab-bar"):
            for tab in TABS:
                yield Static(tab, id=f"tab-{tab}", classes="tab-label")
        with ContentSwitcher(initial="music"):
            yield MusicPane()
            yield NotesPane()
            yield PodcastsPane()
        yield Static("connecting...", id="status")

    def on_mount(self) -> None:
        self._update_tab_bar()
        self.run_worker(self._init_light, exclusive=True, thread=True)

    def _update_tab_bar(self) -> None:
        for i, tab in enumerate(TABS):
            label = self.query_one(f"#tab-{tab}", Static)
            if i == self._tab_index:
                label.add_class("active")
            else:
                label.remove_class("active")

    def _init_light(self) -> None:
        pw = LightThread(self._config)
        pw.start()
        self._pw = pw
        self.call_from_thread(self._on_light_ready)

    def _on_light_ready(self) -> None:
        self.query_one(MusicPane).action_refresh()

    def on_unmount(self) -> None:
        if self._pw is not None:
            self.run_worker(self._pw.shutdown, thread=True)

    def action_prev_tab(self) -> None:
        self._tab_index = (self._tab_index - 1) % len(TABS)
        self._switch_tab()

    def action_next_tab(self) -> None:
        self._tab_index = (self._tab_index + 1) % len(TABS)
        self._switch_tab()

    def _switch_tab(self) -> None:
        self.query_one(ContentSwitcher).current = TABS[self._tab_index]
        self._update_tab_bar()
        if TABS[self._tab_index] == "music":
            self.query_one(MusicPane).query_one(DataTable).focus()


def run_tui(config: LightConfig) -> None:
    LightApp(config).run()
