Sync the device's music library to match a local directory.

Tracks found in DIRECTORY but not on the device are uploaded; tracks on the
device but not found in DIRECTORY are deleted. Matching is by (title, artist),
same as `music upload`'s duplicate detection.

Pass --recursive to also walk DIRECTORY's subdirectories, --dry-run to preview
the changes without making them, --yes to skip the confirmation prompt, and
--json for machine-readable output (--json requires --yes or --dry-run).

**Examples:**

`light music mirror ~/Music`

`light music mirror ~/Music --recursive`

`light music mirror ~/Music --dry-run`
