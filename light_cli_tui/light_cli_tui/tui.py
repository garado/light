"""TUI for managing Light devices."""

import os
import queue
import subprocess
import tempfile
import threading
from concurrent.futures import Future
from dataclasses import dataclass
from typing import Any, Callable

from rich.text import Text
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, VerticalScroll
from textual.coordinate import Coordinate
from textual.screen import ModalScreen
from textual.theme import Theme
from textual.widget import Widget
from textual.widgets import Button, ContentSwitcher, DataTable, Input, Label, Static

NORD = Theme(
    name="nord",
    dark=True,
    background="#1e2127",
    surface="#282c34",
    panel="#2c313a",
    primary="#61afef",
    secondary="#56b6c2",
    accent="#61afef",
    foreground="#abb2bf",
    error="#e06c75",
    warning="#e5c07b",
    success="#98c379",
    variables={
        "text-muted": "#5c6370",
        "surface-lighten-1": "#2c313a",
        "surface-lighten-2": "#3e4451",
        "text-disabled": "#3e4451",
    },
)

from light_api.client import Light
from light_api.music import LightTrack, SortMode
from light_api.notes import LightNote

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

TABS = ["music", "notes"]


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
    ConfirmScreen { align: center middle; background: $background 80%; }
    #dialog {
        padding: 1 3;
        background: $background;
        border: solid $surface-lighten-2;
        border-title-color: $text-muted;
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

    def on_mount(self) -> None:
        self.query_one("#dialog").border_title = "confirm"

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "yes")


class EditScreen(ModalScreen[tuple[str, str, str] | None]):
    CSS = """
    EditScreen { align: center middle; background: $background 80%; }
    #dialog {
        padding: 1 3;
        background: $background;
        border: solid $surface-lighten-2;
        border-title-color: $text-muted;
        width: 50;
        height: auto;
    }
    EditScreen Label {
        color: $text-muted;
        margin-top: 1;
    }
    EditScreen Input {
        border: solid $surface-lighten-2;
        background: $background;
    }
    EditScreen Input:focus {
        border: solid $accent;
        background: $background;
    }
    EditScreen Input.-valid { background: $background; }
    EditScreen Input.-invalid { background: $background; }
    #buttons { margin-top: 1; align: center middle; width: 100%; height: auto; }
    Button { margin: 0 1; }
    """

    def __init__(self, title: str = "", artist: str = "", album: str = "", border_title: str = "edit track") -> None:
        super().__init__()
        self._title = title
        self._artist = artist
        self._album = album
        self._border_title = border_title

    def compose(self) -> ComposeResult:
        with Static(id="dialog"):
            yield Label("title")
            yield Input(value=self._title, id="title")
            yield Label("artist")
            yield Input(value=self._artist, id="artist")
            yield Label("album")
            yield Input(value=self._album, id="album")
            with Horizontal(id="buttons"):
                yield Button("save", variant="primary", id="save")
                yield Button("cancel", variant="default", id="cancel")

    def on_mount(self) -> None:
        self.query_one("#dialog").border_title = self._border_title
        self.query_one("#title", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(self._get_values() if event.button.id == "save" else None)

    def on_key(self, event) -> None:
        if event.key == "enter":
            focused = self.focused
            if isinstance(focused, Button):
                if focused.id == "cancel":
                    self.dismiss(None)
                else:
                    self.dismiss(self._get_values())
            else:
                self.dismiss(self._get_values())
        elif event.key == "escape":
            self.dismiss(None)

    def _get_values(self) -> tuple[str, str, str]:
        return (
            self.query_one("#title", Input).value,
            self.query_one("#artist", Input).value,
            self.query_one("#album", Input).value,
        )


class RenameNoteScreen(ModalScreen[str | None]):
    CSS = """
    RenameNoteScreen { align: center middle; background: $background 80%; }
    #dialog {
        padding: 1 3;
        background: $background;
        border: solid $surface-lighten-2;
        border-title-color: $text-muted;
        width: 50;
        height: auto;
    }
    RenameNoteScreen Label { color: $text-muted; margin-top: 1; }
    RenameNoteScreen Input {
        border: solid $surface-lighten-2;
        background: $background;
    }
    RenameNoteScreen Input:focus { border: solid $accent; background: $background; }
    #buttons { margin-top: 1; align: center middle; width: 100%; height: auto; }
    Button { margin: 0 1; }
    """

    def __init__(self, current_title: str) -> None:
        super().__init__()
        self._current_title = current_title

    def compose(self) -> ComposeResult:
        with Static(id="dialog"):
            yield Label("title")
            yield Input(value=self._current_title, id="title")
            with Horizontal(id="buttons"):
                yield Button("save", variant="primary", id="save")
                yield Button("cancel", variant="default", id="cancel")

    def on_mount(self) -> None:
        inp = self.query_one("#title", Input)
        self.query_one("#dialog").border_title = "rename note"
        inp.focus()
        inp.action_end()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(self.query_one("#title", Input).value if event.button.id == "save" else None)

    def on_key(self, event) -> None:
        if event.key == "enter":
            focused = self.focused
            if isinstance(focused, Button) and focused.id == "cancel":
                self.dismiss(None)
            else:
                self.dismiss(self.query_one("#title", Input).value)
        elif event.key == "escape":
            self.dismiss(None)


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
        self._visual_mode: bool = False
        self._visual_anchor: int = 0
        self._cursor_row: int = 0

    @property
    def _pw(self) -> LightThread | None:
        return self.app._pw  # type: ignore[attr-defined]

    def compose(self) -> ComposeResult:
        yield DataTable()
        yield Input(placeholder="  search...", id="search-bar")

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.cursor_type = "row"
        table.show_header = True
        table.add_column("", width=4)
        table.add_columns("title", "artist", "album")
        self.border_title = "Music"
        self.query_one("#search-bar", Input).display = False
        table.focus()

    def _set_status(self, text: str) -> None:
        if self.app._active_pane == "music":  # type: ignore[attr-defined]
            self.app.query_one("#status", Static).update(text)

    def _set_header(self, track: LightTrack | None) -> None:
        if track is None:
            self.border_subtitle = ""
            return
        parts = [track.title, track.artist]
        if track.album:
            parts.append(track.album)
        self.border_subtitle = "  ·  ".join(parts)

    def _populate_table(self, tracks: list[LightTrack]) -> None:
        positions = {t.audio_id: i for i, t in enumerate(self._tracks, 1)}
        table = self.query_one(DataTable)
        table.clear()
        for track in tracks:
            pos = str(positions.get(track.audio_id, ""))
            table.add_row(pos, track.title, track.artist, track.album, key=track.audio_id)

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
            self._search_mode = False
            self.query_one("#search-bar", Input).display = False
            self.query_one(DataTable).focus()

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

        if key == "escape":
            if self._visual_mode:
                self._visual_mode = False
                self._clear_visual_highlight()
                self._update_status()
            event.stop()
        elif key == "v":
            if self._visual_mode:
                self._visual_mode = False
                self._clear_visual_highlight()
            else:
                self._visual_mode = True
                self._visual_anchor = self._cursor_row
                self._refresh_visual(self._cursor_row)
            self._update_status()
            event.stop()
        elif key == "j":
            new_row = min(self._cursor_row + count, table.row_count - 1)
            self._cursor_row = new_row
            if self._visual_mode:
                self._refresh_visual(new_row)
            else:
                table.move_cursor(row=new_row)
            event.stop()
        elif key == "k":
            new_row = max(self._cursor_row - count, 0)
            self._cursor_row = new_row
            if self._visual_mode:
                self._refresh_visual(new_row)
            else:
                table.move_cursor(row=new_row)
            event.stop()
        elif key == "g":
            if self._last_key == "g":
                if self._visual_mode:
                    lo, hi = self._get_visual_range()
                    self._move_block(-1, lo)
                else:
                    self._cursor_row = 0
                    table.move_cursor(row=0)
                self._last_key = ""
            else:
                self._last_key = key
            event.stop()
            return
        elif key == "G":
            if self._visual_mode:
                lo, hi = self._get_visual_range()
                self._move_block(1, len(self._tracks) - 1 - hi)
            else:
                new_row = table.row_count - 1
                self._cursor_row = new_row
                table.move_cursor(row=new_row)
            event.stop()
        elif key in ("ctrl+d", "ctrl+f"):
            table.action_scroll_page_down()
            event.stop()
        elif key in ("ctrl+u", "ctrl+b"):
            table.action_scroll_page_up()
            event.stop()
        elif key == "J":
            if self._visual_mode:
                self._move_block(1, count)
            else:
                self._move_track(1)
            event.stop()
        elif key == "K":
            if self._visual_mode:
                self._move_block(-1, count)
            else:
                self._move_track(-1)
            event.stop()
        elif key == "r":
            self._visual_mode = False
            self.action_refresh()
            event.stop()
        elif key == "s":
            if not self._visual_mode:
                self._cycle_sort()
            event.stop()
        elif key == "d":
            if self._visual_mode:
                self.action_bulk_delete()
            else:
                self.action_delete()
            event.stop()
        elif key == "e":
            if self._visual_mode:
                self.action_bulk_edit()
            else:
                self.action_edit()
            event.stop()
        elif key == "slash":
            if not self._visual_mode:
                self._start_search()
            event.stop()
        elif key == "h":
            self._visual_mode = False
            self.app.action_prev_tab()  # type: ignore[attr-defined]
            event.stop()
        elif key == "l":
            self._visual_mode = False
            self.app.action_next_tab()  # type: ignore[attr-defined]
            event.stop()

        self._last_key = key

    def _can_rearrange(self) -> bool:
        return SORT_CYCLE[self._sort_index] not in (SortMode.ARTIST_ASC, SortMode.ARTIST_DESC)

    def _move_track(self, direction: int) -> None:
        if self._pw is None:
            return
        if not self._can_rearrange():
            self._set_status("rearranging not available in artist sort mode  |  switch to manual/title/artist+album first")
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
        self._cursor_row = j
        self._populate_table(self._tracks)
        table.move_cursor(row=j)
        self.app.run_worker(lambda: self._do_move(track, j), exclusive=True, thread=True)

    def _get_visual_range(self, cursor: int | None = None) -> tuple[int, int]:
        if cursor is None:
            cursor = self._cursor_row
        lo = min(self._visual_anchor, cursor)
        hi = max(self._visual_anchor, cursor)
        return lo, hi

    def _refresh_visual(self, cursor: int) -> None:
        lo, hi = self._get_visual_range(cursor)
        selected = set(range(lo, hi + 1))
        positions = {t.audio_id: i for i, t in enumerate(self._tracks, 1)}
        table = self.query_one(DataTable)
        for row_idx, track in enumerate(self._filtered_tracks):
            pos = str(positions.get(track.audio_id, ""))
            vals = [pos, track.title, track.artist, track.album]
            style = "bold reverse" if row_idx in selected else ""
            for col_idx, val in enumerate(vals):
                table.update_cell_at(
                    Coordinate(row_idx, col_idx),
                    Text(val, style=style) if style else val,
                )
        table.move_cursor(row=cursor)

    def _clear_visual_highlight(self) -> None:
        positions = {t.audio_id: i for i, t in enumerate(self._tracks, 1)}
        table = self.query_one(DataTable)
        for row_idx, track in enumerate(self._filtered_tracks):
            pos = str(positions.get(track.audio_id, ""))
            for col_idx, val in enumerate([pos, track.title, track.artist, track.album]):
                table.update_cell_at(Coordinate(row_idx, col_idx), val)

    def _move_block(self, direction: int, count: int) -> None:
        if self._pw is None:
            return
        if not self._can_rearrange():
            self._set_status("rearranging not available in artist sort mode  |  switch to manual/title/artist+album first")
            return
        if len(self._filtered_tracks) != len(self._tracks):
            return
        lo, hi = self._get_visual_range()
        block_size = hi - lo + 1
        new_lo = max(0, min(lo + direction * count, len(self._tracks) - block_size))
        if new_lo == lo:
            return
        block = self._tracks[lo:hi + 1]
        rest = self._tracks[:lo] + self._tracks[hi + 1:]
        self._tracks = rest[:new_lo] + block + rest[new_lo:]
        self._filtered_tracks = list(self._tracks)
        cursor_offset = self._cursor_row - lo
        self._visual_anchor = new_lo + (self._visual_anchor - lo)
        new_cursor = new_lo + cursor_offset
        self._cursor_row = new_cursor
        self._populate_table(self._filtered_tracks)
        self._refresh_visual(new_cursor)
        self.app.run_worker(
            lambda: self._do_move_block(block, new_lo, direction),
            exclusive=True,
            thread=True,
        )

    def _do_move_block(self, block: list[LightTrack], new_lo: int, direction: int) -> None:
        from open_api_specification_client.api.default import patch_api_playlist_items_playlist_item_id
        from open_api_specification_client.models import (
            PatchApiPlaylistItemsPlaylistItemIdBody,
            PatchApiPlaylistItemsPlaylistItemIdBodyData,
            PatchApiPlaylistItemsPlaylistItemIdBodyDataAttributes,
            PatchApiPlaylistItemsPlaylistItemIdBodyDataType,
        )
        assert self._pw is not None
        # Move from the outside in to avoid position conflicts:
        # moving down → patch last track first; moving up → patch first track first
        ordered = reversed(list(enumerate(block))) if direction > 0 else enumerate(block)
        for i, track in ordered:
            pos = new_lo + i
            def _patch(light, t=track, p=pos):
                resp = patch_api_playlist_items_playlist_item_id.sync_detailed(
                    playlist_item_id=t.playlist_item_id,
                    client=light._api_client,
                    body=PatchApiPlaylistItemsPlaylistItemIdBody(
                        data=PatchApiPlaylistItemsPlaylistItemIdBodyData(
                            id=t.playlist_item_id,
                            type_=PatchApiPlaylistItemsPlaylistItemIdBodyDataType.PLAYLIST_ITEMS,
                            attributes=PatchApiPlaylistItemsPlaylistItemIdBodyDataAttributes(position=p),
                        )
                    ),
                )
                if not (200 <= resp.status_code < 300):
                    raise RuntimeError(f"move track: {resp.status_code}")
            self._pw.submit(_patch)

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
        self._visual_mode = False
        if sort_mode is not None and sort_mode in SORT_CYCLE:
            self._sort_index = SORT_CYCLE.index(sort_mode)
        self._populate_table(tracks)
        self._update_status()
        self._set_header(tracks[0] if tracks else None)

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        if event.row_key is None:
            return
        self._cursor_row = self.query_one(DataTable).cursor_row
        audio_id = str(event.row_key.value)
        track = next((t for t in self._tracks if t.audio_id == audio_id), None)
        self._set_header(track)

    def update_status(self) -> None:
        self._update_status()

    def refresh_header(self) -> None:
        table = self.query_one(DataTable)
        if table.row_count == 0:
            return
        try:
            row_key = table.coordinate_to_cell_key(table.cursor_coordinate).row_key
            audio_id = str(row_key.value)
            track = next((t for t in self._tracks if t.audio_id == audio_id), None)
            self._set_header(track)
        except Exception:
            pass

    def _update_status(self) -> None:
        if self._visual_mode:
            lo, hi = self._get_visual_range()
            self._set_status(
                f"-- VISUAL --  {hi - lo + 1} selected  |  j/k select  J/K move  v/esc exit"
            )
            return
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

        self.app.push_screen(EditScreen(title=track.title, artist=track.artist, album=track.album), on_edit)

    def _do_edit(self, track: LightTrack, title: str, artist: str, album: str) -> None:
        assert self._pw is not None
        self._pw.submit(
            lambda light: light.music.update_track_metadata(
                track.audio_id, title=title, artist=artist, album=album or None
            )
        )
        tracks = self._pw.submit(lambda light: light.music.get_tracks())
        self.app.call_from_thread(self._on_tracks_loaded, tracks)

    def _selected_tracks(self) -> list[LightTrack]:
        lo, hi = self._get_visual_range()
        return [self._filtered_tracks[i] for i in range(lo, hi + 1)]

    def action_bulk_delete(self) -> None:
        tracks = self._selected_tracks()
        if not tracks:
            return

        def on_confirm(confirmed: bool) -> None:
            if not confirmed:
                return
            self._visual_mode = False
            self._clear_visual_highlight()
            self._set_status(f"deleting {len(tracks)} tracks...")
            ids = {t.audio_id for t in tracks}
            self.app.run_worker(
                lambda: self._do_bulk_delete(ids), exclusive=True, thread=True
            )

        self.app.push_screen(ConfirmScreen(f"delete {len(tracks)} tracks?"), on_confirm)

    def _do_bulk_delete(self, ids: set[str]) -> None:
        assert self._pw is not None
        self._pw.submit(
            lambda light: light.music.delete_tracks_predicate(lambda t: t.audio_id in ids)
        )
        tracks = self._pw.submit(lambda light: light.music.get_tracks())
        self.app.call_from_thread(self._on_tracks_loaded, tracks)

    def action_bulk_edit(self) -> None:
        tracks = self._selected_tracks()
        if not tracks:
            return

        def common(values: list[str]) -> str:
            return values[0] if len(set(values)) == 1 else ""

        pre_title = common([t.title for t in tracks])
        pre_artist = common([t.artist for t in tracks])
        pre_album = common([t.album for t in tracks])

        def on_edit(result: tuple[str, str, str] | None) -> None:
            if result is None:
                return
            new_title, new_artist, new_album = result
            self._visual_mode = False
            self._clear_visual_highlight()
            self._set_status(f"updating {len(tracks)} tracks...")
            self.app.run_worker(
                lambda: self._do_bulk_edit(tracks, new_title, new_artist, new_album),
                exclusive=True,
                thread=True,
            )

        self.app.push_screen(
            EditScreen(
                title=pre_title,
                artist=pre_artist,
                album=pre_album,
                border_title=f"edit {len(tracks)} tracks",
            ),
            on_edit,
        )

    def _do_bulk_edit(self, tracks: list[LightTrack], title: str, artist: str, album: str) -> None:
        assert self._pw is not None
        for track in tracks:
            self._pw.submit(
                lambda light, t=track: light.music.update_track_metadata(
                    t.audio_id,
                    title=title or None,
                    artist=artist or None,
                    album=album or None,
                )
            )
        updated = self._pw.submit(lambda light: light.music.get_tracks())
        self.app.call_from_thread(self._on_tracks_loaded, updated)


class NotesPane(Widget):
    def __init__(self) -> None:
        super().__init__(id="notes")
        self._notes: list[LightNote] = []
        self._content_cache: dict[str, bytes] = {}
        self._audio_proc: subprocess.Popen | None = None
        self._audio_tempfile: str | None = None
        self._last_key: str = ""
        self._count_str: str = ""

    @property
    def _pw(self) -> LightThread | None:
        return self.app._pw  # type: ignore[attr-defined]

    def compose(self) -> ComposeResult:
        with Widget(id="notes-sidebar"):
            yield DataTable(id="notes-list")
        with VerticalScroll(id="note-content"):
            yield Static("", id="note-text")

    def on_mount(self) -> None:
        table = self.query_one("#notes-list", DataTable)
        table.cursor_type = "row"
        table.show_header = False
        table.add_column("note", width=28, key="note")
        sidebar = self.query_one("#notes-sidebar")
        sidebar.border_title = "Notes"
        self.query_one("#note-content").border_title = "Content"

    def action_refresh(self) -> None:
        if self._pw is None:
            return
        self._set_status("loading notes...")
        self.app.run_worker(self._load_notes, exclusive=True, thread=True)

    def _load_notes(self) -> None:
        assert self._pw is not None
        notes = self._pw.submit(lambda light: light.notes.get_notes())
        self.app.call_from_thread(self._on_notes_loaded, notes)

    def _on_notes_loaded(self, notes: list[LightNote]) -> None:
        self._notes = notes
        self._content_cache.clear()
        table = self.query_one("#notes-list", DataTable)
        table.clear()
        for note in notes:
            prefix = "♪" if note.note_type == "audio" else "✎"
            table.add_row(f"{prefix} {note.title or '(untitled)'}", key=note.id)
        self.update_status()

    def update_status(self) -> None:
        self._set_status(
            f"{len(self._notes)} notes  |  j/k nav  enter load  n new  y copy  e editor  R rename  dd delete  p play/stop  r refresh  h/l tabs  q quit"
        )

    def refresh_header(self) -> None:
        note = self._current_note()
        sidebar = self.query_one("#notes-sidebar")
        if note is None:
            sidebar.border_subtitle = ""
            return
        prefix = "♪" if note.note_type == "audio" else "✎"
        sidebar.border_subtitle = f"{prefix} {note.title or '(untitled)'}"

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        if event.row_key is None:
            return
        note = self._note_for_key(str(event.row_key.value))
        if note is None:
            return
        prefix = "♪" if note.note_type == "audio" else "✎"
        self.query_one("#notes-sidebar").border_subtitle = f"{prefix} {note.title or '(untitled)'}"

    def _open_current_note(self) -> None:
        note = self._current_note()
        if note is None:
            return
        self._stop_audio_proc()
        prefix = "♪" if note.note_type == "audio" else "✎"
        self.query_one("#note-content").border_title = f"Content  ·  {prefix} {note.title or '(untitled)'}  ({note.updated_at})"
        if note.note_type == "audio":
            self.query_one("#note-text", Static).update(
                f"♪  {note.title or '(untitled)'}\n\n[audio note]  press p to play"
            )
        elif note.id in self._content_cache:
            self._show_text(self._content_cache[note.id])
        else:
            self.query_one("#note-text", Static).update("loading...")
            self.app.run_worker(lambda: self._fetch_text(note), thread=True)

    def _fetch_text(self, note: LightNote) -> None:
        assert self._pw is not None
        content = self._pw.submit(lambda light: light.notes.get_note_content(note))
        self._content_cache[note.id] = content
        self.app.call_from_thread(self._show_text, content)

    def _show_text(self, content: bytes) -> None:
        self.query_one("#note-text", Static).update(
            Text(content.decode("utf-8", errors="replace"))
        )

    def _note_for_key(self, note_id: str) -> LightNote | None:
        return next((n for n in self._notes if n.id == note_id), None)

    def _current_note(self) -> LightNote | None:
        table = self.query_one("#notes-list", DataTable)
        if table.row_count == 0:
            return None
        row_key = table.coordinate_to_cell_key(table.cursor_coordinate).row_key
        return self._note_for_key(str(row_key.value))

    def _toggle_audio(self) -> None:
        note = self._current_note()
        if note is None or note.note_type != "audio":
            return
        if self._audio_proc and self._audio_proc.poll() is None:
            self._stop_audio_proc()
            self.query_one("#note-text", Static).update(
                f"♪  {note.title or '(untitled)'}\n\n[audio note]  press p to play"
            )
        else:
            self.query_one("#note-text", Static).update("fetching audio...")
            self.app.run_worker(lambda: self._start_audio(note), thread=True)

    def _start_audio(self, note: LightNote) -> None:
        assert self._pw is not None
        if note.id not in self._content_cache:
            content = self._pw.submit(lambda light: light.notes.get_note_content(note))
            self._content_cache[note.id] = content
        content = self._content_cache[note.id]

        with tempfile.NamedTemporaryFile(suffix=".m4a", delete=False) as f:
            f.write(content)
            self._audio_tempfile = f.name

        for cmd in (["mpv", "--no-video", "--really-quiet"], ["ffplay", "-nodisp", "-autoexit"]):
            try:
                self._audio_proc = subprocess.Popen(
                    cmd + [self._audio_tempfile],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                self.app.call_from_thread(
                    self.query_one("#note-text", Static).update,
                    f"▶  {note.title or '(untitled)'}\n\n[playing]  press p to stop",
                )
                return
            except FileNotFoundError:
                continue

        self.app.call_from_thread(
            self.query_one("#note-text", Static).update,
            "no audio player found (install mpv or ffplay)",
        )

    def _stop_audio_proc(self) -> None:
        if self._audio_proc and self._audio_proc.poll() is None:
            self._audio_proc.terminate()
        self._audio_proc = None
        if self._audio_tempfile:
            try:
                os.unlink(self._audio_tempfile)
            except OSError:
                pass
            self._audio_tempfile = None

    def on_unmount(self) -> None:
        self._stop_audio_proc()

    def on_key(self, event) -> None:
        key = event.key
        table = self.query_one("#notes-list", DataTable)

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
        elif key == "enter":
            self._open_current_note()
            event.stop()
        elif key == "p":
            self._toggle_audio()
            event.stop()
        elif key == "y":
            self._copy_to_clipboard()
            event.stop()
        elif key == "e":
            self._open_in_editor()
            event.stop()
        elif key == "r":
            self.action_refresh()
            event.stop()
        elif key == "R":
            self._rename_note()
            event.stop()
        elif key == "n":
            self._new_note()
            event.stop()
        elif key == "d":
            if self._last_key == "d":
                self._confirm_delete_note()
                self._last_key = ""
            else:
                self._last_key = key
            event.stop()
            return
        elif key == "h":
            self._stop_audio_proc()
            self.app.action_prev_tab()  # type: ignore[attr-defined]
            event.stop()
        elif key == "l":
            self._stop_audio_proc()
            self.app.action_next_tab()  # type: ignore[attr-defined]
            event.stop()

        self._last_key = key

    def _new_note(self) -> None:
        def on_title(title: str | None) -> None:
            if not title:
                return
            self._set_status("creating...")
            self.app.run_worker(lambda: self._do_create_note(title), thread=True)

        self.app.push_screen(RenameNoteScreen(""), on_title)

    def _do_create_note(self, title: str) -> None:
        assert self._pw is not None
        note = self._pw.submit(lambda light: light.notes.create_text_note(title, ""))
        self.app.call_from_thread(self._on_note_created, note)

    def _on_note_created(self, note: LightNote) -> None:
        self._notes.insert(0, note)
        self._content_cache[note.id] = b""
        table = self.query_one("#notes-list", DataTable)
        prefix = "✎"
        label = f"{prefix} {note.title or '(untitled)'}"
        table.add_row(label, key=note.id)
        table.move_cursor(row=table.row_count - 1)
        self._set_status("created — opening editor...")
        self._open_in_editor()

    def _confirm_delete_note(self) -> None:
        note = self._current_note()
        if note is None:
            return

        def on_result(confirmed: bool) -> None:
            if confirmed:
                self._set_status("deleting...")
                self.app.run_worker(lambda: self._do_delete_note(note), thread=True)

        self.app.push_screen(ConfirmScreen(f"delete '{note.title or note.id}'?"), on_result)

    def _do_delete_note(self, note: LightNote) -> None:
        assert self._pw is not None
        self._pw.submit(lambda light: light.notes.delete_note(note.id))
        self.app.call_from_thread(self._on_note_deleted, note)

    def _on_note_deleted(self, note: LightNote) -> None:
        self._notes = [n for n in self._notes if n.id != note.id]
        self._content_cache.pop(note.id, None)
        table = self.query_one("#notes-list", DataTable)
        table.remove_row(note.id)
        self.query_one("#notes-sidebar").border_subtitle = ""
        self.query_one("#note-content").border_title = "Content"
        self.query_one("#note-text", Static).update("")
        self._set_status("deleted")
        self.set_timer(2, self.update_status)

    def _copy_to_clipboard(self) -> None:
        import pyperclip
        note = self._current_note()
        if note is None or note.note_type == "audio":
            self._set_status("clipboard: no text content")
            return
        content = self._content_cache.get(note.id)
        if content is None:
            self._set_status("load note first with enter")
            self.set_timer(2, self.update_status)
            return
        pyperclip.copy(content.decode("utf-8", errors="replace"))
        self._set_status("copied to clipboard")
        self.set_timer(2, self.update_status)

    def _open_in_editor(self) -> None:
        note = self._current_note()
        if note is None or note.note_type == "audio":
            self._set_status("editor: no text content")
            return
        original = self._content_cache.get(note.id)
        if original is None:
            self._set_status("load note first with enter")
            self.set_timer(2, self.update_status)
            return
        editor = os.environ.get("EDITOR", "nano")
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode="wb") as f:
            f.write(original)
            tmpfile = f.name
        try:
            with self.app.suspend():
                subprocess.run([editor, tmpfile])
            with open(tmpfile, "rb") as f:
                updated = f.read()
        finally:
            try:
                os.unlink(tmpfile)
            except OSError:
                pass
        if updated == original:
            return
        self._set_status("saving...")
        self.app.run_worker(lambda: self._save_note(note, updated), thread=True)

    def _rename_note(self) -> None:
        note = self._current_note()
        if note is None:
            return

        def on_result(new_title: str | None) -> None:
            if new_title is None or new_title == note.title:
                return
            self._set_status("renaming...")
            self.app.run_worker(lambda: self._do_rename(note, new_title), thread=True)

        self.app.push_screen(RenameNoteScreen(note.title or ""), on_result)

    def _do_rename(self, note: LightNote, title: str) -> None:
        assert self._pw is not None
        self._pw.submit(lambda light: light.notes.update_note_title(note, title))
        self.app.call_from_thread(self._on_renamed, note)

    def _on_renamed(self, note: LightNote) -> None:
        table = self.query_one("#notes-list", DataTable)
        prefix = "♪" if note.note_type == "audio" else "✎"
        label = f"{prefix} {note.title or '(untitled)'}"
        table.update_cell(note.id, "note", label)
        self.query_one("#notes-sidebar").border_subtitle = label
        if note.id in self._content_cache:
            self.query_one("#note-content").border_title = (
                f"Content  ·  {label}  ({note.updated_at})"
            )
        self._set_status("renamed")
        self.set_timer(2, self.update_status)

    def _save_note(self, note: LightNote, content: bytes) -> None:
        assert self._pw is not None
        self._pw.submit(lambda light: light.notes.update_note_content(note, content))
        self._content_cache[note.id] = content
        self.app.call_from_thread(self._show_text, content)
        self.app.call_from_thread(self._set_status, "saved")
        self.app.call_from_thread(self.set_timer, 2, self.update_status)

    def _set_status(self, text: str) -> None:
        if self.app._active_pane == "notes":  # type: ignore[attr-defined]
            self.app.query_one("#status", Static).update(text)



class LightApp(App):
    CSS = """
    Screen { background: $background; }
    LightApp { layout: vertical; background: $background; }

    ContentSwitcher { height: 1fr; margin: 0; padding: 0; background: $background; }

    DataTable { background: $background; }
    DataTable > .datatable--header { background: $surface; color: $text-muted; }
    DataTable > .datatable--cursor { background: $accent 25%; }
    DataTable > .datatable--hover { background: $surface; }

    ScrollBar { background: $background; }
    ScrollBar > .scrollbar--bar { background: $background; }
    ScrollBar > .scrollbar--slider { background: $surface-lighten-2; }

    Input { background: $surface; border: solid $surface-lighten-2; }
    Input:focus { background: $surface; border: solid $accent; }

    Button { background: $panel; }
    Button:hover { background: $panel-lighten-1; }
    Button.-primary { background: $primary; }
    Button.-error { background: $error; }

    MusicPane {
        layout: vertical;
        height: 1fr;
        border: solid $surface-lighten-2;
        border-title-color: $text-muted;
        border-subtitle-color: $text-muted;
        border-subtitle-align: right;
        padding: 0;
    }
    MusicPane DataTable { height: 1fr; }
    #search-bar {
        height: 1;
        border: none;
        padding: 0 1;
    }

    NotesPane { layout: horizontal; height: 1fr; }
    #notes-sidebar {
        width: 34;
        height: 1fr;
        border: solid $surface-lighten-2;
        border-title-color: $text-muted;
        border-subtitle-color: $text-muted;
    }
    #notes-list { height: 1fr; }
    #note-content {
        width: 1fr;
        height: 1fr;
        border: solid $surface-lighten-2;
        border-title-color: $text-muted;
        padding: 1 2;
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
        self._active_pane: str = "music"

    def compose(self) -> ComposeResult:
        with ContentSwitcher(initial="music"):
            yield MusicPane()
            yield NotesPane()
        yield Static("connecting...", id="status")

    def on_mount(self) -> None:
        self.register_theme(NORD)
        self.theme = "nord"
        self.query_one(MusicPane).query_one(DataTable).focus()
        self.run_worker(self._init_light, exclusive=True, thread=True)

    def _init_light(self) -> None:
        pw = LightThread(self._config)
        pw.start()
        self._pw = pw
        self.call_from_thread(self._on_light_ready)

    def _on_light_ready(self) -> None:
        self.query_one(MusicPane).action_refresh()
        self.query_one(NotesPane).action_refresh()

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
        tab = TABS[self._tab_index]
        self._active_pane = tab
        if tab == "music":
            pane = self.query_one(MusicPane)
            pane.query_one(DataTable).focus()
            pane.update_status()
            pane.refresh_header()
        elif tab == "notes":
            pane = self.query_one(NotesPane)
            pane.query_one("#notes-list", DataTable).focus()
            pane.update_status()
            pane.refresh_header()


def run_tui(config: LightConfig) -> None:
    LightApp(config).run()
