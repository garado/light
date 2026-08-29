"""Shared widgets reused across panes."""

from dataclasses import dataclass

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.screen import ModalScreen
from textual.widgets import Button, DataTable, Input, Label


class VimDataTable(DataTable):
    """A DataTable with basic vim-style navigation binds layered onto its existing actions."""

    BINDINGS = [
        Binding("j", "cursor_down", show=False),
        Binding("k", "cursor_up", show=False),
        Binding("h", "cursor_left", show=False),
        Binding("l", "cursor_right", show=False),
        Binding("g", "scroll_top", show=False),
        Binding("G", "scroll_bottom", show=False),
        Binding("ctrl+d", "page_down", show=False),
        Binding("ctrl+u", "page_up", show=False),
    ]


class SearchBar(Input):
    """A `/`-style incremental search field docked at the bottom of a pane.

    Emits `Input.Changed` (as you type) and `Input.Submitted` (Enter).
    Escape emits `SearchBar.Cancelled` so the pane can drop the filter.
    Hidden until a pane shows it with `.display = True` and focuses it.
    """

    DEFAULT_CSS = """
    SearchBar {
        dock: bottom;
        height: 1;
        border: none;
        padding: 0;
        background: $surface;
        color: $text;
    }
    SearchBar:focus { border: none; background: $surface; }
    """

    BINDINGS = [Binding("escape", "cancel", show=False)]

    class Cancelled(Message):
        """Posted when the user presses Escape in the search bar."""

        def __init__(self, search_bar: "SearchBar") -> None:
            self.search_bar = search_bar
            super().__init__()

        @property
        def control(self) -> "SearchBar":
            return self.search_bar

    def action_cancel(self) -> None:
        self.post_message(self.Cancelled(self))


@dataclass
class EditField:
    key: str
    label: str
    initial: str = ""


class EditModal(ModalScreen[dict[str, str] | None]):
    """Generic pop-up edit form: a title and a list of labeled text fields.

    Dismisses with a {field.key: value} dict on save, or None on cancel/escape.
    """

    CSS = """
    EditModal { align: center middle; background: $background 80%; }
    #dialog {
        padding: 1 3;
        background: $background;
        border: round $accent;
        border-title-color: $accent;
        width: 50;
        height: auto;
    }
    EditModal Label { color: $text-muted; margin-top: 1; }
    EditModal Input { border: solid $surface-lighten-2; background: $background; }
    EditModal Input:focus { border: solid $accent; background: $background; }
    #buttons { margin-top: 1; align: center middle; width: 100%; height: auto; }
    #buttons Button { margin: 0 1; }
    """

    BINDINGS = [Binding("escape", "cancel", show=False)]

    def __init__(self, modal_title: str, fields: list[EditField]) -> None:
        super().__init__()
        self.modal_title = modal_title
        self.fields = fields

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            for f in self.fields:
                yield Label(f.label)
                yield Input(value=f.initial, id=f"field-{f.key}")
            with Horizontal(id="buttons"):
                yield Button("Save", variant="primary", id="save")
                yield Button("Cancel", id="cancel")

    def on_mount(self) -> None:
        self.query_one("#dialog").border_title = self.modal_title
        if self.fields:
            self.query_one(f"#field-{self.fields[0].key}", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save":
            self._save()
        else:
            self.dismiss(None)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self._save()

    def action_cancel(self) -> None:
        self.dismiss(None)

    def _save(self) -> None:
        result = {
            f.key: self.query_one(f"#field-{f.key}", Input).value for f in self.fields
        }
        self.dismiss(result)
