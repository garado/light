from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import DataTable

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
    MusicPane DataTable { height: 1fr; }
    """

    def compose(self) -> ComposeResult:
        yield DataTable()

    def on_mount(self) -> None:
        self._pw: "LightThread | None" = None
        self._loaded = False
        self.border_title = "Tracks"
        self.border_subtitle = "connecting..."
        table = self.query_one(DataTable)
        table.add_columns("Title", "Artist", "Album")
        table.cursor_type = "row"

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
        table = self.query_one(DataTable)
        table.clear()
        for t in tracks:
            table.add_row(t.title, t.artist, t.album)
        self.border_subtitle = f"{len(tracks)} track{'s' if len(tracks) != 1 else ''}"
