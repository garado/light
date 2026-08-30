Update metadata for one or more tracks.

Select tracks to edit by fuzzy search, regex, or by ID. Edits can be applied both interactively and non-interactively.

# Selection
- Fuzzy: `light music update "song title"`
- Regex: `light music update --title ".*substring.*"`
    - Supports `--title`, `--artist`, and `--album`. Multiple filters will be applied together (logical AND).
- ID: `light music update --id abc123,def456`
    - Use a comma-separated list to select multiple tracks.

# Editing

## Selection picker and interactive editor (default)

After inputting selection criteria, a picker opens to fine-tune the selection. From there, you have the option to batch-edit
or individually edit tracks in the selection.

## Skip selection picker and interactive editor

Use `--new-title`, `--new-artist`, and `--new-album` to skip the selection picker. This will open a confirmation screen
with preview of all tracks being edited.

`light music update --artist "The Warning" --new-artist "Las Wawas"`

### Skip confirmation screen

Use `--yes` to skip the confirmation screen and auto-apply the edit.

`light music update --artist "The Warning" --new-artist "Las Wawas" --yes`

### Preview without applying

Use `--dry-run` to print the tracks that would be edited and the changes that
would be made, without touching anything. Requires `--new-*`.

`light music update --artist "The Warning" --new-artist "Las Wawas" --dry-run`

### Machine-readable output

Pass `--json` (with `--new-*` and either `--yes` or `--dry-run`) for a JSON
envelope. `--dry-run --json` emits the plan (`{tracks, changes}`); `--yes
--json` emits the list of updated tracks.

`light music update --id abc123 --new-album "Remastered" --yes --json`
