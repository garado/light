Delete a note by title or by ID.

Uses exact title matching; run `light notes list --id` to find note IDs for
bulk or ambiguous-title deletes. Prompts for confirmation before deleting;
skip with `--yes` or preview with `--dry-run`.

**Examples:**

`light notes delete "Shopping list"`

`light notes delete --id abc123`

`light notes delete --id abc123,def456`
