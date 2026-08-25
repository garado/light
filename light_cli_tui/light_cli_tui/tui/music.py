from typing import TYPE_CHECKING

from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.widget import Widget

from ..format import human_size
from .widgets import EditField, EditModal, VimDataTable

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

    BINDINGS = [Binding("ctrl+e", "edit_track", "edit")]

    _TITLE_WIDTH = 40
    _ARTIST_WIDTH = 25
    _ALBUM_WIDTH = 25

    def compose(self) -> ComposeResult:
        yield VimDataTable()

    def on_mount(self) -> None:
        self._pw: "LightThread | None" = None
        self._loaded = False
        self._tracks: list = []
        self.border_title = "Tracks"
        self.border_subtitle = "connecting..."
        table = self.query_one(VimDataTable)
        table.add_column("Title", width=self._TITLE_WIDTH)
        table.add_column("Artist", width=self._ARTIST_WIDTH)
        table.add_column("Album", width=self._ALBUM_WIDTH)
        table.cursor_type = "row"

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
        table = self.query_one(VimDataTable)
        table.clear()
        for t in tracks:
            table.add_row(
                self._truncate(t.title, self._TITLE_WIDTH),
                self._truncate(t.artist, self._ARTIST_WIDTH),
                self._truncate(t.album, self._ALBUM_WIDTH),
            )
        count = f"{len(tracks)} track{'s' if len(tracks) != 1 else ''}"
        used = f"{human_size(capacity.used_capacity)} / {human_size(capacity.total_capacity)}"
        self.border_subtitle = f"{count} · {used} · sort: {sort_mode.value}"

    @work
    async def action_edit_track(self) -> None:
        table = self.query_one(VimDataTable)
        if not self._tracks or table.row_count == 0:
            return
        track = self._tracks[table.cursor_row]

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
