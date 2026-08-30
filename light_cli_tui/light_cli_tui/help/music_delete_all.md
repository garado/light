Delete ALL tracks on the device.

Interactively, this asks for confirmation and then requires typing
`yes i am sure` before anything is deleted.

For automation: `--yes` skips both prompts, `--dry-run` reports how many tracks
would be deleted without touching anything, and `--json` emits a machine-readable
envelope (`--json` requires `--yes` or `--dry-run`).

**Examples:**

`light music delete-all`

`light music delete-all --dry-run`

`light music delete-all --yes --json`
