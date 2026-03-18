"""TUI for managing Light devices."""

import queue
import threading
from concurrent.futures import Future
from dataclasses import dataclass
from typing import Any, Callable

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.screen import ModalScreen
from textual.widgets import Button, DataTable, Input, Label, Static

from core import Light
from music import LightTrack, SortMode

SORT_CYCLE: list[SortMode] = [
    SortMode.RANK,
    SortMode.ARTIST_ASC,
    SortMode.ARTIST_DESC,
    SortMode.TITLE_ASC,
    SortMode.TITLE_DESC,
]

SORT_LABELS: dict[SortMode, str] = {
    SortMode.RANK: "manual",
    SortMode.ARTIST_ASC: "artist a-z",
    SortMode.ARTIST_DESC: "artist z-a",
    SortMode.TITLE_ASC: "title a-z",
    SortMode.TITLE_DESC: "title z-a",
}


@dataclass
class LightConfig:
    email_file: str | None = None
    password_file: str | None = None
    phone_file: str | None = None
    headless: bool = True


class PlaywrightThread:
    """Runs a Light instance in a dedicated thread.

    Playwright's sync API uses greenlets tied to the thread they were created on.
    All Light/Playwright calls must be submitted to this thread via submit().
    """

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
                email_file=self._config.email_file,
                password_file=self._config.password_file,
                phone_file=self._config.phone_file,
                headless=self._config.headless,
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
        """Submit a function to run on the Playwright thread. Blocks until done."""
        future: Future[Any] = Future()
        self._queue.put((func, future))
        return future.result()

    def shutdown(self) -> None:
        self._queue.put(None)
        self._thread.join()


class ConfirmScreen(ModalScreen[bool]):
    CSS = """
    ConfirmScreen {
        align: center middle;
    }
    #dialog {
        padding: 1 3;
        background: $surface;
        border: tall $primary;
        width: auto;
        height: auto;
    }
    #buttons {
        margin-top: 1;
        align: center middle;
        width: auto;
    }
    Button {
        margin: 0 1;
    }
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


class EditScreen(ModalScreen[tuple[str, str] | None]):
    CSS = """
    EditScreen {
        align: center middle;
    }
    #dialog {
        padding: 1 3;
        background: $surface;
        border: tall $primary;
        width: 50;
        height: auto;
    }
    Input {
        margin-top: 1;
    }
    #buttons {
        margin-top: 1;
        align: center middle;
        width: auto;
    }
    Button {
        margin: 0 1;
    }
    """

    def __init__(self, track: LightTrack) -> None:
        super().__init__()
        self._track = track

    def compose(self) -> ComposeResult:
        with Static(id="dialog"):
            yield Label("edit track")
            yield Input(value=self._track.title, placeholder="title", id="title")
            yield Input(value=self._track.artist, placeholder="artist", id="artist")
            with Static(id="buttons"):
                yield Button("save", variant="primary", id="save")
                yield Button("cancel", variant="default", id="cancel")

    def on_mount(self) -> None:
        self.query_one("#title", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save":
            title = self.query_one("#title", Input).value
            artist = self.query_one("#artist", Input).value
            self.dismiss((title, artist))
        else:
            self.dismiss(None)

    def on_key(self, event) -> None:
        if event.key == "enter":
            title = self.query_one("#title", Input).value
            artist = self.query_one("#artist", Input).value
            self.dismiss((title, artist))
        elif event.key == "escape":
            self.dismiss(None)


class LightApp(App):
    CSS = """
    DataTable {
        height: 1fr;
    }
    #status {
        height: 1;
        padding: 0 1;
        color: $text-muted;
    }
    """

    BINDINGS = [
        Binding("r", "refresh", "refresh"),
        Binding("s", "sort", "sort"),
        Binding("d", "delete", "delete"),
        Binding("e", "edit", "edit"),
        Binding("q", "quit", "quit"),
        Binding("j", "cursor_down", show=False),
        Binding("k", "cursor_up", show=False),
        Binding("g", "scroll_home", show=False),
        Binding("G", "scroll_end", show=False),
        Binding("ctrl+d", "scroll_page_down", show=False),
        Binding("ctrl+u", "scroll_page_up", show=False),
        Binding("ctrl+f", "scroll_page_down", show=False),
        Binding("ctrl+b", "scroll_page_up", show=False),
        Binding("J", "move_down", show=False),
        Binding("K", "move_up", show=False),
    ]

    def __init__(self, config: LightConfig) -> None:
        super().__init__()
        self._config = config
        self._pw: PlaywrightThread | None = None
        self._tracks: list[LightTrack] = []
        self._sort_index: int = 0
        self._pending_sort_index: int | None = None  # set while cycling, not yet applied

    def compose(self) -> ComposeResult:
        yield DataTable()
        yield Static("connecting...", id="status")

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.cursor_type = "row"
        table.show_header = False
        table.add_columns("title", "artist")
        self.run_worker(self._init_playwright, exclusive=True, thread=True)

    def _set_status(self, text: str) -> None:
        self.query_one("#status", Static).update(text)

    def _populate_table(self, tracks: list[LightTrack]) -> None:
        table = self.query_one(DataTable)
        table.clear()
        for track in tracks:
            table.add_row(track.title, track.artist, key=track.audio_id)

    # --- playwright init ---

    def _init_playwright(self) -> None:
        pw = PlaywrightThread(self._config)
        pw.start()
        self._pw = pw
        self.call_from_thread(self.action_refresh)

    def on_unmount(self) -> None:
        if self._pw is not None:
            self.run_worker(self._pw.shutdown, thread=True)

    # --- vim navigation ---

    def action_cursor_down(self) -> None:
        self.query_one(DataTable).action_cursor_down()

    def action_cursor_up(self) -> None:
        self.query_one(DataTable).action_cursor_up()

    def action_scroll_home(self) -> None:
        self.query_one(DataTable).action_scroll_home()

    def action_scroll_end(self) -> None:
        self.query_one(DataTable).action_scroll_end()

    def action_scroll_page_down(self) -> None:
        self.query_one(DataTable).action_scroll_page_down()

    def action_scroll_page_up(self) -> None:
        self.query_one(DataTable).action_scroll_page_up()

    def action_move_down(self) -> None:
        self._move_track(1)

    def action_move_up(self) -> None:
        self._move_track(-1)

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

        self.run_worker(lambda: self._do_move(track, j), exclusive=True, thread=True)

    def _do_move(self, track: LightTrack, new_position: int) -> None:
        assert self._pw is not None
        self._pw.submit(lambda light: light._check_response(
            light._request(
                f"https://production.lightphonecloud.com/api/playlist_items/{track.playlist_item_id}",
                method="PATCH",
                data={"data": {"id": track.playlist_item_id, "type": "playlist_items", "attributes": {"position": new_position}}},
            ),
            "move track",
        ))

    # --- actions ---

    def action_refresh(self) -> None:
        if self._pw is None:
            return
        self._set_status("loading...")
        self.run_worker(self._load_tracks, exclusive=True, thread=True)

    def _load_tracks(self) -> None:
        assert self._pw is not None
        tracks = self._pw.submit(lambda light: light.music.get_tracks())
        self.call_from_thread(self._on_tracks_loaded, tracks)

    def _on_tracks_loaded(self, tracks: list[LightTrack]) -> None:
        self._tracks = tracks
        self._pending_sort_index = None
        self._populate_table(tracks)
        self._update_status()

    def _update_status(self) -> None:
        sort_label = SORT_LABELS[SORT_CYCLE[self._sort_index]]
        if self._pending_sort_index is not None:
            pending_label = SORT_LABELS[SORT_CYCLE[self._pending_sort_index]]
            self._set_status(f"{len(self._tracks)} tracks  |  sort: {sort_label} → {pending_label}  |  s cycle  enter apply  esc cancel")
        else:
            self._set_status(f"{len(self._tracks)} tracks  |  sort: {sort_label}  |  r refresh  s sort  d delete  e edit  q quit")

    def action_sort(self) -> None:
        if self._pw is None:
            return
        base = self._pending_sort_index if self._pending_sort_index is not None else self._sort_index
        self._pending_sort_index = (base + 1) % len(SORT_CYCLE)
        self._update_status()

    def on_key(self, event) -> None:
        if self._pending_sort_index is not None:
            if event.key == "enter":
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
                    self.run_worker(lambda: self._do_sort(sort_mode), exclusive=True, thread=True)

                self.push_screen(ConfirmScreen(f"apply sort: {label}?"), on_confirm)
            elif event.key == "escape":
                event.stop()
                self._pending_sort_index = None
                self._update_status()

    def _do_sort(self, sort_mode: SortMode) -> None:
        assert self._pw is not None
        self._pw.submit(lambda light: light.music.set_sort_mode(sort_mode))
        tracks = self._pw.submit(lambda light: light.music.get_tracks())
        self.call_from_thread(self._on_tracks_loaded, tracks)

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
        self.run_worker(lambda: self._do_delete(track), exclusive=True, thread=True)

    def _do_delete(self, track: LightTrack) -> None:
        assert self._pw is not None
        self._pw.submit(
            lambda light: light.music.delete_tracks_predicate(
                lambda t: t.audio_id == track.audio_id, confirm=False
            )
        )
        tracks = self._pw.submit(lambda light: light.music.get_tracks())
        self.call_from_thread(self._on_tracks_loaded, tracks)

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

        def on_edit(result: tuple[str, str] | None) -> None:
            if result is None:
                return
            new_title, new_artist = result
            self._set_status(f"saving: {new_title}...")
            self.run_worker(
                lambda: self._do_edit(track, new_title, new_artist),
                exclusive=True,
                thread=True,
            )

        self.push_screen(EditScreen(track), on_edit)

    def _do_edit(self, track: LightTrack, title: str, artist: str) -> None:
        assert self._pw is not None
        self._pw.submit(
            lambda light: light.music.update_track_metadata(
                track.audio_id, title=title, artist=artist
            )
        )
        tracks = self._pw.submit(lambda light: light.music.get_tracks())
        self.call_from_thread(self._on_tracks_loaded, tracks)


def run_tui(config: LightConfig) -> None:
    LightApp(config).run()
