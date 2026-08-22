Rename a single note.

Targets a single note by exact title or by `--id`. If TITLE matches more
than one note, use `--id` to disambiguate.

Prompts for confirmation before renaming; skip with `--yes` or preview
with `--dry-run`.

**Usage:**

`light notes rename TITLE NEW_TITLE`

`light notes rename --id <id> NEW_TITLE`

**Examples:**

`light notes rename "Shoping list" "Shopping list"`

`light notes rename --id abc123 "Renamed note"`
