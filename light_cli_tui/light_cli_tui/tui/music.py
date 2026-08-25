from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.widget import Widget

from .widgets import VimDataTable

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

    _TITLE_WIDTH = 40
    _ARTIST_WIDTH = 25
    _ALBUM_WIDTH = 25

    def compose(self) -> ComposeResult:
        yield VimDataTable()

    def on_mount(self) -> None:
        self._pw: "LightThread | None" = None
        self._loaded = False
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
        self.app.call_from_thread(self._populate, tracks)

    def _populate(self, tracks) -> None:
        table = self.query_one(VimDataTable)
        table.clear()
        for t in tracks:
            table.add_row(
                self._truncate(t.title, self._TITLE_WIDTH),
                self._truncate(t.artist, self._ARTIST_WIDTH),
                self._truncate(t.album, self._ALBUM_WIDTH),
            )
        self.border_subtitle = f"{len(tracks)} track{'s' if len(tracks) != 1 else ''}"
