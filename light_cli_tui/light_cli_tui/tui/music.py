from typing import TYPE_CHECKING

from textual import on, work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.widget import Widget
from textual.widgets import Input

from ..format import human_size
from .widgets import EditField, EditModal, SearchBar, VimDataTable

if TYPE_CHECKING:
    from .worker import LightThread


class MusicPane(Widget):
    DEFAULT_CSS = """
    MusicPane {
        border: round $accent;
        border-title-color: $accent;
        border-title-align: left;
        height: 1fr;
        padding: 0 1;
    }
    MusicPane VimDataTable {
        height: 1fr;
        overflow-x: hidden;
        scrollbar-size-vertical: 1;
    }
    """

    BINDINGS = [
        Binding("/", "search", "search"),
        Binding("ctrl+e", "edit_track", "edit"),
    ]

    _TITLE_WIDTH = 40
    _ARTIST_WIDTH = 25
    _ALBUM_WIDTH = 25

    def compose(self) -> ComposeResult:
        yield VimDataTable()
        yield SearchBar(placeholder="search title / artist / album")

    def focus_default(self) -> None:
        self.query_one(VimDataTable).focus()

    def on_mount(self) -> None:
        self._pw: "LightThread | None" = None
        self._loaded = False
        self._tracks: list = []
        self._visible: list = []
        self._query = ""
        self._capacity = None
        self._sort_mode = None
        self.border_title = "Tracks"
        self.border_subtitle = "connecting..."
        table = self.query_one(VimDataTable)
        table.add_column("Title", width=self._TITLE_WIDTH)
        table.add_column("Artist", width=self._ARTIST_WIDTH)
        table.add_column("Album", width=self._ALBUM_WIDTH)
        table.cursor_type = "row"
        self.query_one(SearchBar).display = False

    @staticmethod
    def _truncate(text: str, width: int) -> str:
        return text if len(text) <= width else text[: width - 1] + "…"

    def ensure_loaded(self, pw: "LightThread") -> None:
        """Fetch tracks, but only the first time this pane is shown."""
        if self._loaded:
            return
        self._loaded = True
        self._pw = pw
        self.border_subtitle = "loading..."
        self.run_worker(self._load_tracks, exclusive=True, thread=True)

    def _load_tracks(self) -> None:
        tracks = self._pw.submit(lambda light: light.music.get_tracks())
        capacity = self._pw.submit(lambda light: light.music.get_capacity())
        sort_mode = self._pw.submit(lambda light: light.music.get_sort_mode())
        self.app.call_from_thread(self._populate, tracks, capacity, sort_mode)

    def _populate(self, tracks, capacity, sort_mode) -> None:
        self._tracks = tracks
        self._capacity = capacity
        self._sort_mode = sort_mode
        self._apply_filter()

    # -- search ---------------------------------------------------------------

    def action_search(self) -> None:
        search = self.query_one(SearchBar)
        search.display = True
        search.value = self._query
        search.focus()

    @on(Input.Changed, "SearchBar")
    def _on_query_changed(self, event: Input.Changed) -> None:
        self._query = event.value
        self._apply_filter()

    @on(Input.Submitted, "SearchBar")
    def _on_query_submitted(self, event: Input.Submitted) -> None:
        # keep the filter, hand focus back to the table
        self.query_one(SearchBar).display = False
        self.query_one(VimDataTable).focus()

    @on(SearchBar.Cancelled)
    def _on_query_cancelled(self, event: SearchBar.Cancelled) -> None:
        self._query = ""
        event.control.value = ""
        event.control.display = False
        self._apply_filter()
        self.query_one(VimDataTable).focus()

    def _apply_filter(self) -> None:
        q = self._query.strip().lower()
        if q:
            self._visible = [
                t
                for t in self._tracks
                if q in f"{t.title} {t.artist} {t.album}".lower()
            ]
        else:
            self._visible = list(self._tracks)
        self._render_rows()
        self._update_title()
        self._update_subtitle()

    def _update_title(self) -> None:
        q = self._query.strip()
        if q:
            shown = len(self._visible)
            self.border_title = (
                f'Tracks · Showing {shown} result{"" if shown == 1 else "s"} for "{q}"'
            )
        else:
            self.border_title = "Tracks"

    def _render_rows(self) -> None:
        table = self.query_one(VimDataTable)
        table.clear()
        for t in self._visible:
            table.add_row(
                self._truncate(t.title, self._TITLE_WIDTH),
                self._truncate(t.artist, self._ARTIST_WIDTH),
                self._truncate(t.album, self._ALBUM_WIDTH),
            )

    def _update_subtitle(self) -> None:
        if self._capacity is None:
            return
        total = len(self._tracks)
        shown = len(self._visible)
        if self._query.strip():
            count = f"{shown}/{total} match{'' if shown == 1 else 'es'}"
        else:
            count = f"{total} track{'' if total == 1 else 's'}"
        used = (
            f"{human_size(self._capacity.used_capacity)}"
            f" / {human_size(self._capacity.total_capacity)}"
        )
        sort = self._sort_mode.value if self._sort_mode is not None else "?"
        self.border_subtitle = f"{count} · {used} · sort: {sort}"

    # -- edit ---------------------------------------------------------------

    @work
    async def action_edit_track(self) -> None:
        table = self.query_one(VimDataTable)
        if not self._visible or table.row_count == 0:
            return
        track = self._visible[table.cursor_row]

        result = await self.app.push_screen_wait(
            EditModal(
                "Edit Track",
                [
                    EditField("title", "Title", track.title),
                    EditField("artist", "Artist", track.artist),
                    EditField("album", "Album", track.album),
                ],
            )
        )
        if result is None:
            return
        if (
            result["title"] == track.title
            and result["artist"] == track.artist
            and result["album"] == track.album
        ):
            return

        self.border_subtitle = "saving..."
        self.run_worker(
            lambda: self._save_edit(track.audio_id, result), exclusive=True, thread=True
        )

    def _save_edit(self, audio_id: str, values: dict) -> None:
        self._pw.submit(
            lambda light: light.music.update_track_metadata(
                audio_id,
                title=values["title"],
                artist=values["artist"],
                album=values["album"],
            )
        )
        self.app.call_from_thread(self._reload)

    def _reload(self) -> None:
        self._loaded = False
        self.ensure_loaded(self._pw)
