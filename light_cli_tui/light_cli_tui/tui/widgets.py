"""Shared widgets reused across panes."""

from textual.binding import Binding
from textual.widgets import DataTable


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
