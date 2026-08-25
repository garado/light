"""Main TUI application: ncmpcpp-style header + number-key navigation between panes."""

from importlib.metadata import version

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.widgets import ContentSwitcher, Footer, Static

from .music import MusicPane
from .worker import LightConfig, LightThread

PANES = ["music", "notes", "contacts", "tools"]
PANE_TITLES = {
    "music": "Music",
    "notes": "Notes",
    "contacts": "Contacts",
    "tools": "Tools",
}


class LightApp(App):
    ENABLE_COMMAND_PALETTE = False

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

    Footer {
        background: $surface;
    }
    FooterKey {
        background: $surface;
    }
    FooterKey .footer-key--key {
        color: $accent;
        background: $surface;
        text-style: bold;
    }
    FooterKey .footer-key--description {
        color: $text-muted;
        background: $surface;
    }
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
        self._pw: LightThread | None = None

    def compose(self) -> ComposeResult:
        with Horizontal(id="nav-header"):
            yield Static(PANE_TITLES[self._active_pane], id="nav-title")
            yield Static(f"light tui v{version('light-phone-cli-tui')}", id="nav-version")
        with ContentSwitcher(initial="music"):
            yield MusicPane(id="music")
            for pane in PANES[1:]:
                yield Static(id=pane)
        yield Footer()

    def on_mount(self) -> None:
        self.theme = "ansi-dark"
        self.run_worker(self._init_light, exclusive=True, thread=True)

    def _init_light(self) -> None:
        pw = LightThread(self._config)
        pw.start()
        self._pw = pw
        self.call_from_thread(self._on_light_ready)

    def _on_light_ready(self) -> None:
        self._load_active_pane()

    def _load_active_pane(self) -> None:
        """Lazily load the currently active pane's data, if it hasn't been already."""
        if self._pw is None:
            return
        pane = self.query_one(f"#{self._active_pane}")
        if hasattr(pane, "ensure_loaded"):
            pane.ensure_loaded(self._pw)

    def on_unmount(self) -> None:
        if self._pw is not None:
            self.run_worker(self._pw.shutdown, thread=True)

    def action_switch_pane(self, pane: str) -> None:
        if pane == self._active_pane:
            return
        self._active_pane = pane
        self.query_one("#nav-title", Static).update(PANE_TITLES[pane])
        self.query_one(ContentSwitcher).current = pane
        self._load_active_pane()


def run_tui(config: LightConfig) -> None:
    LightApp(config).run()
