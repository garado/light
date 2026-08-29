"""Notes pane: list of notes on the left, content of the selected note on the right."""

import os
import subprocess
import tempfile
from typing import TYPE_CHECKING

from mutagen._file import File as MutagenFile
from textual import on, work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.widget import Widget
from textual.widgets import DataTable, Input, Static

from .widgets import EditField, EditModal, SearchBar, VimDataTable

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
    #notes-content-pane.-audio { align: center middle; }
    #notes-content-pane.-audio Static { text-align: center; width: auto; }
    """

    BINDINGS = [
        Binding("/", "search", "search"),
        Binding("ctrl+e", "edit_note", "edit"),
        Binding("ctrl+p", "toggle_audio", "play"),
        Binding("ctrl+r", "rename_note", "rename"),
    ]

    _TITLE_WIDTH = 32

    def compose(self) -> ComposeResult:
        with Widget(id="notes-list-pane"):
            yield VimDataTable(id="notes-list")
            yield SearchBar(placeholder="search titles")
        with VerticalScroll(id="notes-content-pane"):
            yield Static("", id="notes-content")

    def focus_default(self) -> None:
        self.query_one("#notes-list", VimDataTable).focus()

    def on_mount(self) -> None:
        self._pw: "LightThread | None" = None
        self._loaded = False
        self._notes: list = []
        self._visible: list = []
        self._query = ""
        self._content_cache: dict[str, bytes] = {}
        self._audio_proc: subprocess.Popen | None = None
        self._audio_tempfile: str | None = None
        self._audio_duration: float = 0.0
        self._audio_elapsed: float = 0.0
        self._audio_timer = None
        self._durations: dict[str, float] = {}
        self._playing_note_id: str | None = None
        self.query_one("#notes-list-pane").border_title = "List"
        self.query_one("#notes-content-pane").border_title = "Content"
        list_pane = self.query_one("#notes-list-pane")
        list_pane.border_subtitle = "connecting..."
        table = self.query_one("#notes-list", VimDataTable)
        table.add_column("Title", width=self._TITLE_WIDTH, key="title")
        table.show_header = False
        table.cursor_type = "row"
        self.query_one(SearchBar).display = False

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
        self._apply_filter()
        if self._visible:
            self._show_note(self._visible[0])

    # -- search ------------------------------------------------------------

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
        # keep the filter, hand focus back to the list
        self.query_one(SearchBar).display = False
        self.query_one("#notes-list", VimDataTable).focus()

    @on(SearchBar.Cancelled)
    def _on_query_cancelled(self, event: SearchBar.Cancelled) -> None:
        self._query = ""
        event.control.value = ""
        event.control.display = False
        self._apply_filter()
        self.query_one("#notes-list", VimDataTable).focus()

    def _apply_filter(self) -> None:
        q = self._query.strip().lower()
        if q:
            self._visible = [n for n in self._notes if q in (n.title or "").lower()]
        else:
            self._visible = list(self._notes)
        self._render_rows()
        self._update_list_meta()

    def _render_rows(self) -> None:
        table = self.query_one("#notes-list", VimDataTable)
        table.clear()
        for n in self._visible:
            prefix = "♪" if n.note_type == "audio" else "✎"
            table.add_row(
                f"{prefix} {self._truncate(n.title or '(untitled)', self._TITLE_WIDTH - 2)}",
                key=n.id,
            )
        if not self._visible:
            self.query_one("#notes-content", Static).update("no matches")

    def _update_list_meta(self) -> None:
        pane = self.query_one("#notes-list-pane")
        total = len(self._notes)
        shown = len(self._visible)
        if self._query.strip():
            pane.border_title = (
                f'List · Showing {shown} result{"" if shown == 1 else "s"}'
                f' for "{self._query.strip()}"'
            )
            pane.border_subtitle = f"{shown}/{total} match{'' if shown == 1 else 'es'}"
        else:
            pane.border_title = "List"
            pane.border_subtitle = f"{total} note{'' if total == 1 else 's'}"

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        if event.row_key is None:
            return
        note = self._note_for_id(str(event.row_key.value))
        if note is not None:
            self._show_note(note)

    def _note_for_id(self, note_id: str):
        return next((n for n in self._notes if n.id == note_id), None)

    def _current_note(self):
        table = self.query_one("#notes-list", VimDataTable)
        if table.row_count == 0:
            return None
        row_key = table.coordinate_to_cell_key(table.cursor_coordinate).row_key
        return self._note_for_id(str(row_key.value))

    def _show_note(self, note) -> None:
        content_pane = self.query_one("#notes-content-pane")
        content_pane.border_title = (
            f"Content · {note.title or '(untitled)'} · {note.updated_at}"
        )

        if note.note_type == "audio":
            content_pane.add_class("-audio")
            if self._playing_note_id is not None and self._playing_note_id != note.id:
                self._cleanup_audio()
                self._playing_note_id = None

            if note.id in self._durations:
                elapsed = self._audio_elapsed if self._playing_note_id == note.id else 0.0
                self._render_playback(note, elapsed, self._durations[note.id])
            else:
                self._render_playback(note, 0.0, 0.0)
                self.run_worker(
                    lambda: self._load_duration(note), exclusive=True, thread=True
                )
            return

        content_pane.remove_class("-audio")
        if self._playing_note_id is not None:
            self._cleanup_audio()
            self._playing_note_id = None

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

    def action_edit_note(self) -> None:
        note = self._current_note()
        if note is None or note.note_type == "audio":
            return
        content = self._content_cache.get(note.id)
        if content is None:
            return

        editor = os.environ.get("EDITOR", "nano")
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode="wb") as f:
            f.write(content)
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

        if updated == content:
            return

        self._content_cache[note.id] = updated
        self._display_content(updated)
        self.run_worker(
            lambda: self._save_note(note, updated), exclusive=True, thread=True
        )

    def _save_note(self, note, content: bytes) -> None:
        self._pw.submit(lambda light: light.notes.update_note_content(note, content))

    @work
    async def action_rename_note(self) -> None:
        note = self._current_note()
        if note is None:
            return

        result = await self.app.push_screen_wait(
            EditModal("Rename Note", [EditField("title", "Title", note.title)])
        )
        if result is None or result["title"] == note.title:
            return

        note.title = result["title"]
        self._refresh_list_row(note)
        self.query_one("#notes-content-pane").border_title = (
            f"Content · {note.title or '(untitled)'} · {note.updated_at}"
        )
        self.run_worker(
            lambda: self._save_rename(note, result["title"]),
            exclusive=True,
            thread=True,
        )

    def _refresh_list_row(self, note) -> None:
        table = self.query_one("#notes-list", VimDataTable)
        prefix = "♪" if note.note_type == "audio" else "✎"
        table.update_cell(
            note.id,
            "title",
            f"{prefix} {self._truncate(note.title or '(untitled)', self._TITLE_WIDTH - 2)}",
        )

    def _save_rename(self, note, title: str) -> None:
        self._pw.submit(lambda light: light.notes.update_note_title(note, title))

    def _load_duration(self, note) -> None:
        content = self._content_cache.get(note.id)
        if content is None:
            content = self._pw.submit(lambda light: light.notes.get_note_content(note))
            self._content_cache[note.id] = content

        duration = 0.0
        with tempfile.NamedTemporaryFile(suffix=".m4a", delete=False) as f:
            f.write(content)
            tmpfile = f.name
        try:
            audio = MutagenFile(tmpfile)
            if audio is not None and audio.info is not None:
                duration = audio.info.length
        except Exception:
            pass
        finally:
            os.unlink(tmpfile)

        self._durations[note.id] = duration
        self.app.call_from_thread(self._on_duration_loaded, note, duration)

    def _on_duration_loaded(self, note, duration: float) -> None:
        current = self._current_note()
        if current is None or current.id != note.id:
            return
        elapsed = self._audio_elapsed if self._playing_note_id == note.id else 0.0
        self._render_playback(note, elapsed, duration)

    def action_toggle_audio(self) -> None:
        note = self._current_note()
        if note is None or note.note_type != "audio":
            return
        if self._audio_proc is not None and self._audio_proc.poll() is None:
            self._stop_audio()
        else:
            self.run_worker(
                lambda: self._start_audio(note), exclusive=True, thread=True
            )

    def _start_audio(self, note) -> None:
        content = self._content_cache.get(note.id)
        if content is None:
            content = self._pw.submit(lambda light: light.notes.get_note_content(note))
            self._content_cache[note.id] = content

        with tempfile.NamedTemporaryFile(suffix=".m4a", delete=False) as f:
            f.write(content)
            tmpfile = f.name

        duration = self._durations.get(note.id)
        if duration is None:
            duration = 0.0
            try:
                audio = MutagenFile(tmpfile)
                if audio is not None and audio.info is not None:
                    duration = audio.info.length
            except Exception:
                pass
            self._durations[note.id] = duration

        for cmd in (
            ["mpv", "--no-video", "--really-quiet"],
            ["ffplay", "-nodisp", "-autoexit"],
        ):
            try:
                proc = subprocess.Popen(
                    cmd + [tmpfile],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            except FileNotFoundError:
                continue
            self.app.call_from_thread(
                self._on_audio_started, note, proc, tmpfile, duration
            )
            return

        os.unlink(tmpfile)
        self.app.call_from_thread(
            self._render_playback_error, "no audio player found (install mpv or ffplay)"
        )

    def _render_playback_error(self, message: str) -> None:
        self.query_one("#notes-content", Static).update(message)

    def _on_audio_started(self, note, proc, tmpfile, duration: float) -> None:
        self._audio_proc = proc
        self._audio_tempfile = tmpfile
        self._audio_duration = duration
        self._audio_elapsed = 0.0
        self._playing_note_id = note.id
        self._render_playback(note, 0.0, duration)
        self._audio_timer = self.set_interval(1.0, lambda: self._tick_playback(note))

    def _tick_playback(self, note) -> None:
        if self._audio_proc is None or self._audio_proc.poll() is not None:
            self._stop_audio()
            return
        self._audio_elapsed += 1.0
        self._render_playback(note, self._audio_elapsed, self._audio_duration)

    def _render_playback(self, note, elapsed: float, duration: float) -> None:
        icon = "⏸" if self._playing_note_id == note.id else "▶"
        self.query_one("#notes-content", Static).update(
            f"♪ {note.title or '(untitled)'}\n\n"
            f"{icon} {self._format_duration(elapsed)} / {self._format_duration(duration)}"
        )

    @staticmethod
    def _format_duration(seconds: float) -> str:
        seconds = int(seconds)
        return f"{seconds // 60}:{seconds % 60:02d}"

    def _cleanup_audio(self) -> None:
        """Stop the player process/timer and remove the temp file. No UI updates."""
        if self._audio_timer is not None:
            self._audio_timer.stop()
            self._audio_timer = None
        if self._audio_proc is not None and self._audio_proc.poll() is None:
            self._audio_proc.terminate()
        self._audio_proc = None
        if self._audio_tempfile is not None:
            try:
                os.unlink(self._audio_tempfile)
            except OSError:
                pass
            self._audio_tempfile = None

    def _stop_audio(self) -> None:
        self._cleanup_audio()
        self._playing_note_id = None
        note = self._current_note()
        if note is not None and note.note_type == "audio":
            self._render_playback(note, 0.0, self._durations.get(note.id, 0.0))

    def on_unmount(self) -> None:
        self._cleanup_audio()
