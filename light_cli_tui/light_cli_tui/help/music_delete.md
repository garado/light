Delete tracks by fuzzy search, by regex pattern, or by exact audio ID.

Each SONGS argument is fuzzy-matched against every track's title, artist,
and album. By default, the top-scoring match(es) per query are auto-selected
(ties may select multiple); pass --interactive to pick matches by hand instead.

If more than one of --title, --artist, --album regex patterns are given, tracks
must match all of them. --interactive also works with regex selection: it opens
a checkbox menu over the matched tracks so you can narrow the set by hand.

For fuzzy and regex selection the confirm prompt offers [p] to hand-pick the
matched tracks before deleting. Selection by --id skips straight to a yes/no
confirm.

Pass --dry-run to preview which tracks would be deleted, --yes to skip the
confirmation prompt, and --json for machine-readable output (--json requires
--yes or --dry-run). --interactive cannot be combined with any of those.

**Examples:**

`light music delete "Playing God"`

`light music delete -i "Playing God"`

`light music delete --title '^Live '`

`light music delete --artist '^The '`

`light music delete --album '(Deluxe|Remastered)'`

`light music delete --title '^Live ' -i` (regex match, then hand-pick)

`light music delete --id abc123,def456 --yes`

`light music delete --title '^Live ' --dry-run --json`
