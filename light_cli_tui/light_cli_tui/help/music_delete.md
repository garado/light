Delete tracks by fuzzy search or by regex pattern.

Each SONGS argument is fuzzy-matched against every track's title, artist,
and album. By default, the top-scoring match(es) per query are auto-selected
(ties may select multiple); pass --interactive to pick matches by hand instead.

If more than one of --title, --artist, --album regex patterns are given, tracks must match all of them.

**Examples:**

`light music delete "Playing God"`

`light music delete -i "Playing God"`

`light music delete --title '^Live '`

`light music delete --artist '^The '`

`light music delete --album '(Deluxe|Remastered)'`
