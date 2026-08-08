Unfollow a podcast by title or by exact ID.

`TITLE` and `--id` are mutually exclusive.

# By title

Must be an exact match. Run `light podcasts list` to see titles.

`light podcasts delete "Some Podcast"`

# By ID
 
Uses `followed_podcast_id`. Run `light podcasts list --json` to see IDs. For bulk deletes, use comma-separated IDs.

`light podcasts delete --id abc123`

`light podcasts delete --id abc123,def456`

