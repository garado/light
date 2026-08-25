"""Main TUI application: ncmpcpp-style header + number-key navigation between panes."""

from importlib.metadata import version

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.widgets import ContentSwitcher, Static

from .worker import LightConfig

PANES = ["music", "notes", "contacts", "tools"]
PANE_TITLES = {
    "music": "Music",
    "notes": "Notes",
    "contacts": "Contacts",
    "tools": "Tools",
}


class LightApp(App):
    CSS = """
    Screen { background: $background; }
    LightApp { layout: vertical; background: $background; }

    #nav-header {
        height: 1;
        padding: 0 1;
        background: $surface;
    }
    #nav-title { width: 1fr; text-style: bold; }
    #nav-version { width: auto; color: $text-muted; }

    ContentSwitcher { height: 1fr; }
    """

    BINDINGS = [
        Binding("q", "quit", "quit"),
        Binding("ctrl+c", "quit", "quit", show=False),
        Binding("1", "switch_pane('music')", "music", show=False),
        Binding("2", "switch_pane('notes')", "notes", show=False),
        Binding("3", "switch_pane('contacts')", "contacts", show=False),
        Binding("4", "switch_pane('tools')", "tools", show=False),
    ]

    def __init__(self, config: LightConfig) -> None:
        super().__init__()
        self._config = config
        self._active_pane = "music"

    def compose(self) -> ComposeResult:
        with Horizontal(id="nav-header"):
            yield Static(PANE_TITLES[self._active_pane], id="nav-title")
            yield Static(f"light tui v{version('light-phone-cli-tui')}", id="nav-version")
        with ContentSwitcher(initial="music"):
            for pane in PANES:
                yield Static(id=pane)

    def on_mount(self) -> None:
        self.theme = "ansi-dark"

    def action_switch_pane(self, pane: str) -> None:
        if pane == self._active_pane:
            return
        self._active_pane = pane
        self.query_one("#nav-title", Static).update(PANE_TITLES[pane])
        self.query_one(ContentSwitcher).current = pane


def run_tui(config: LightConfig) -> None:
    LightApp(config).run()
