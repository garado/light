Update the content of a single note. Currently, only text notes are supported.

Targets a single note by exact title or by `--id`. If TITLE matches more
than one note, use `--id` to disambiguate.

Provide new content inline as an argument, or from a file with `--file`.

Prompts for confirmation before replacing; skip with `--yes` or preview
with `--dry-run`.

**Usage:**

`light notes update TITLE CONTENT`

`light notes update TITLE --file <path>`

`light notes update --id <id> CONTENT`

`light notes update --id <id> --file <path>`

**Examples:**

`light notes update "Shopping list" "eggs, milk, bread, cheese"`

`light notes update --id abc123 --file new-notes.txt`
