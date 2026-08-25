"""Shared formatting helpers used by both the CLI and TUI."""


def human_size(num_bytes: int) -> str:
    """Format a byte count as a human-readable size (e.g. 1.5 GB)."""
    size = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1000 or unit == "TB":
            return f"{size:.1f} {unit}" if unit != "B" else f"{int(size)} {unit}"
        size /= 1000
    return f"{size:.1f} TB"
