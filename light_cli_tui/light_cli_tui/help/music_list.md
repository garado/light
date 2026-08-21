List all tracks on your device.

If more than one of --title, --artist, --album regex patterns are given,
tracks must match all of them.

Use --head/-H or --tail/-T to limit output to the first or last N tracks.

**Examples:**

`light music list --head 10`

`light music list --tail 5`

`light music list --title '^Live '`

`light music list --artist '.*substring.*'`

`light music list --album '(Deluxe|Remastered)'`
