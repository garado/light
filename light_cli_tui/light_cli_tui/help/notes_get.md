Fetch a single note and its content by ID.

Text notes will print inline by default. Audio notes must be saved to a file with `--output`/`-o`.
Text notes can also be saved to a file with the same flag.

Run `light notes list --id` to find note IDs.

**Examples:**

`light notes get abc123`

`light notes get abc123 --output note.txt`

`light notes get def456 --output voice-memo.m4a`
