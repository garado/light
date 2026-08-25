"""Notes pane: list of notes on the left, content of the selected note on the right."""

from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widget import Widget
from textual.widgets import DataTable, Static

from .widgets import VimDataTable

if TYPE_CHECKING:
    from .worker import LightThread


class NotesPane(Widget):
    DEFAULT_CSS = """
    NotesPane {
        layout: horizontal;
        height: 1fr;
    }
    #notes-list-pane {
        width: 34;
        height: 1fr;
        border: round $accent;
        border-title-color: $accent;
        border-title-align: left;
        padding: 0 1;
    }
    #notes-list-pane VimDataTable {
        height: 1fr;
        overflow-x: hidden;
        scrollbar-size-vertical: 1;
    }
    #notes-content-pane {
        width: 1fr;
        height: 1fr;
        border: round $accent;
        border-title-color: $accent;
        border-title-align: left;
        padding: 0 1;
    }
    """

    _TITLE_WIDTH = 32

    def compose(self) -> ComposeResult:
        with Widget(id="notes-list-pane"):
            yield VimDataTable(id="notes-list")
        with VerticalScroll(id="notes-content-pane"):
            yield Static("", id="notes-content")

    def focus_default(self) -> None:
        self.query_one("#notes-list", VimDataTable).focus()

    def on_mount(self) -> None:
        self._pw: "LightThread | None" = None
        self._loaded = False
        self._notes: list = []
        self._content_cache: dict[str, bytes] = {}
        self.query_one("#notes-list-pane").border_title = "List"
        self.query_one("#notes-content-pane").border_title = "Content"
        list_pane = self.query_one("#notes-list-pane")
        list_pane.border_subtitle = "connecting..."
        table = self.query_one("#notes-list", VimDataTable)
        table.add_column("Title", width=self._TITLE_WIDTH)
        table.show_header = False
        table.cursor_type = "row"

    @staticmethod
    def _truncate(text: str, width: int) -> str:
        return text if len(text) <= width else text[: width - 1] + "…"

    def ensure_loaded(self, pw: "LightThread") -> None:
        """Fetch notes, but only the first time this pane is shown."""
        if self._loaded:
            return
        self._loaded = True
        self._pw = pw
        self.query_one("#notes-list-pane").border_subtitle = "loading..."
        self.run_worker(self._load_notes, exclusive=True, thread=True)

    def _load_notes(self) -> None:
        notes = self._pw.submit(lambda light: light.notes.get_notes())
        self.app.call_from_thread(self._populate, notes)

    def _populate(self, notes) -> None:
        self._notes = notes
        self._content_cache.clear()
        table = self.query_one("#notes-list", VimDataTable)
        table.clear()
        for n in notes:
            prefix = "♪" if n.note_type == "audio" else "✎"
            table.add_row(
                f"{prefix} {self._truncate(n.title or '(untitled)', self._TITLE_WIDTH - 2)}",
                key=n.id,
            )
        count = f"{len(notes)} note{'s' if len(notes) != 1 else ''}"
        self.query_one("#notes-list-pane").border_subtitle = count
        if notes:
            self._show_note(notes[0])

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        if event.row_key is None:
            return
        note = self._note_for_id(str(event.row_key.value))
        if note is not None:
            self._show_note(note)

    def _note_for_id(self, note_id: str):
        return next((n for n in self._notes if n.id == note_id), None)

    def _show_note(self, note) -> None:
        content_pane = self.query_one("#notes-content-pane")
        content_pane.border_title = (
            f"Content · {note.title or '(untitled)'} · {note.updated_at}"
        )

        if note.note_type == "audio":
            self.query_one("#notes-content", Static).update(
                f"♪  {note.title or '(untitled)'}\n\n(audio note - playback not yet supported)"
            )
            return

        if note.id in self._content_cache:
            self._display_content(self._content_cache[note.id])
            return

        self.query_one("#notes-content", Static).update("loading...")
        self.run_worker(lambda: self._fetch_content(note), exclusive=True, thread=True)

    def _fetch_content(self, note) -> None:
        content = self._pw.submit(lambda light: light.notes.get_note_content(note))
        self._content_cache[note.id] = content
        self.app.call_from_thread(self._display_content, content)

    def _display_content(self, content: bytes) -> None:
        self.query_one("#notes-content", Static).update(
            content.decode("utf-8", errors="replace")
        )
