
# light

A collection of community-maintained tools for managing your Light Phone - a Python API, a CLI, and a TUI.

## Highlights
- **Music**
    - **Upload FLACs __without__ losing your metadata!**
    - Bulk upload support: `light music upload ~/Music --recursive`
    - Delete tracks (with regex filter support)
    - Bulk-edit track metadata (with regex filter support)
- **Notes**
    - Create, rename, and update notes from the CLI
    - Bulk download every note - text as `.txt`, audio as `.m4a`
- **Podcasts**
    - Subscribe to any podcast by RSS feed URL
- **Contacts**
    - Add, edit, and delete contacts, or bulk import/export as vCard (`.vcf`)
- **Tools**
    - Discover installable tools live from the API, then enable/disable them per device
- **Scriptable**
    - `--json`, `--yes`, and `--dry-run` on every mutating command
- **TUI**
    - Full-screen terminal UI with Vim binds for music and notes: `light tui`

## Installation

> [!CAUTION]
> This is beta software and is **actively in development.** Bugs are expected, and bug reports are welcome!
> 
> This is also an **unofficial** set of tools created through reverse-engineering, so this could break at any time if Light decides to change the structure of their API.

This repo bundles two separate packages `light-phone-api` and `light-phone-cli-tui`. Install whichever suits your needs.

From PyPI:

```
pip install light-phone-api
pip install light-phone-cli-tui
```

## Authentication

This needs your Light email and password to authenticate into the Light dashboard. If your account has more than one device registered, you'll also need to specify which one to operate on via phone number or device ID (mutually exclusive). Please enter your phone number **without** the country code.

```sh
# 1. Pass credentials from file
light --email-file=... --password-file=... --phone-number-file=... <command>

# 2. Pass credentials through environment variables
# Assumes LIGHT_EMAIL and LIGHT_PASSWORD are set, plus LIGHT_PHONE_NUMBER/LIGHT_DEVICE_ID if necessary. (See .env.example)
light <command>

# 3. Pass credentials through user prompt
light --email=... --phone-number=... --ask <command>
```

After the first login, your auth token will be cached. Tokens are good for 30 days. Log out with `light logout`.

Local response caching is also available (off by default) to speed up repeated commands - see [Caching](#caching).

## Getting started: CLI/TUI

Everything is under the `light` command, grouped by area:

| Group | What it does |
|---|---|
| `light music` | upload, list, delete, sort, edit metadata, capacity, playlists |
| `light notes` | list, get, add, update, rename, delete, download-all |
| `light podcasts` | add (by RSS), list, delete |
| `light contacts` | list, add, update, delete, import/export vCard |
| `light tools` | catalog, list, add, remove device tools |
| `light devices` | list registered devices |
| `light settings` | device settings (e.g. developer mode) |
| `light cache` | control the local response cache |
| `light tui` | launch the full-screen terminal UI |

Run `light`, `light <group>`, or `light <group> <command> --help` for full, always-current docs.

Most mutating commands accept `--dry-run` (preview), `--yes` (skip confirmation), and `--json` (machine-readable output).

**Note:** as with the official Light dashboard, changes may take a few moments to propagate to the device.

### Music

#### Upload

```sh
# Upload a whole folder (recurse into subfolders)
light music upload ~/Music/Library --recursive

# Upload individual files. Tracks matching an existing one (title+artist) are skipped
light music upload song1 song2 song3

# Replace matching tracks instead of skipping them
light music upload song1 song2 song3 --overwrite

# Keep duplicates instead of skipping
light music upload song1 song2 song3 --allow-duplicates
```

#### Delete

```sh
# Delete by fuzzy title match
light music delete song

# Delete by regex on title / artist / album (-t / -a / -b)
light music delete --artist "^The Warning$"
light music delete -t "remix" -a "boards of canada"

# Delete specific tracks by ID (comma-separated for bulk)
light music delete --id abc123,def456

# Hand-pick from the matches before deleting
light music delete --artist ".*" --interactive

# Delete all tracks (multiple confirmation steps, don't worry)
light music delete-all
```

#### Sort

```sh
# Sort tracks by title (!!!)
light music sort title --asc
light music sort title --desc

# Sort tracks by artist
light music sort artist --asc
light music sort artist --desc

# Sort tracks by artist and album (!!!)
# (Track numbers not supported)
light music sort artist-album --asc
light music sort artist-album --desc

# Show the device's current sort mode (no field given)
light music sort
```

#### Edit metadata

```sh
# Select tracks by fuzzy search, regex, or ID, then edit interactively
light music update "song title"
light music update --artist ".*warning.*"
light music update --id abc123,def456

# Non-interactive: set new values directly with --new-*
light music update --artist "The Warning" --new-artist "Las Wawas"
light music update --artist "The Warning" --new-artist "Las Wawas" --yes      # skip confirmation
light music update --artist "The Warning" --new-artist "Las Wawas" --dry-run  # preview only
```

#### Other

```sh
# Show audio storage capacity and usage on the device
light music capacity
```

### Notes

```sh
# List all notes (with optional content preview)
light notes list
light notes list --content-preview

# Create a new text note
light notes add "Shopping list" "eggs, milk, bread"
light notes add "Meeting notes" --file notes.txt  # copy contents from notes.txt

# Download all notes to a directory
# Text notes saved as .txt, audio notes as .m4a
light notes download-all ~/my-notes
```

### Podcasts

```sh
# Subscribe to a podcast by RSS feed URL
light podcasts add https://feeds.simplecast.com/FO6kxYGj

# List followed podcasts
light podcasts list

# Unfollow a podcast by title
light podcasts delete "My Podcast"
```

### Contacts

```sh
# List contacts (add --id to also show each contact's UUID)
light contacts list
light contacts list --id

# Add a contact
light contacts add --first "John" --last "Doe" --num "+1 210 555 0100"

# Update a contact by ID (only the fields you pass are changed)
light contacts update 8e97022d-4cfb-44f3-9a40-2159ef4161da --num "+1 210 555 0199"

# Delete one or more contacts by ID
light contacts delete <id1> <id2>

# Import/export as vCard (.vcf)
light contacts import contacts.vcf
light contacts export contacts.vcf
```

### Devices

```sh
# List all devices registered on this account
light devices list
```

### Settings

```sh
# Show or toggle developer mode on the device
light settings developer-mode
light settings developer-mode on
light settings developer-mode off
```

### Tools

Tools are discovered live from the API. See what's available with `light tools catalog`.

```sh
# List every installable tool (live from the API)
light tools catalog

# List tools currently enabled on the device
light tools list

light tools add <tool>

light tools remove <tool>
```

### Scripting

Mutating commands take `--json`, `--yes`, and `--dry-run` for safe automation. To emit JSON Schema for every `--json`-enabled command's output:

```sh
light schema
```

### TUI

<img width="2572" height="1011" alt="tui(1)" src="https://github.com/user-attachments/assets/8a36d6a2-8d0c-45ca-ad27-5ee5f15fb459" />

The TUI offers an easy way of managing music and notes.

```sh
# Launch
light tui
```

TUI-specific features:
- First-class support for Vim bindings
- Music
    - Reorder tracks individually or in visual block mode
    - Bulk edit track metadata
    - Bulk delete tracks
- Notes
    - Content preview for both text and audio notes
    - Press `e` to edit in `$EDITOR`

#### Music

| Key | Action |
|-----|--------|
| `j` / `k` | Navigate |
| `gg` / `G` | Jump to top / bottom |
| `J` / `K` | Move track up / down |
| `5J` / `5K` | Move track up / down by 5 |
| `v` | Enter visual mode (select a block) |
| `J` / `K` in visual | Move selected block up / down |
| `gg` / `G` in visual | Move selected block to top / bottom |
| `d` in visual | Delete selected tracks |
| `e` | Edit track metadata |
| `e` in visual | Bulk edit metadata (shared fields pre-filled) |
| `s` | Cycle sort mode |
| `/` | Search |
| `r` | Refresh |

#### Notes

| Key | Action |
|-----|--------|
| `j` / `k` | Navigate |
| `gg` / `G` | Jump to top / bottom |
| `Enter` | Load note content |
| `n` | New note (opens in `$EDITOR`) |
| `e` | Edit note content in `$EDITOR` |
| `R` | Rename note |
| `dd` | Delete note (with confirmation) |
| `y` | Copy content to clipboard |
| `p` | Play / stop audio note |
| `r` | Refresh |

## Getting started: API

Minimal API usage examples are in [`examples/`](https://github.com/garado/light/tree/main/examples). Happy hacking!

---

# Technical notes

## Caching

Local response caching is **off by default**. When enabled, read commands (`podcasts list`, `notes list`, `music list`, `devices list`, `tools list`, and note content fetched via `notes get`) may return a cached response instead of always hitting the API to improve performance. Mutating commands always invalidate the cache for whatever they change.

Cached data expires after 15 minutes regardless. Each cache file is encrypted with a key derived (scrypt + per-file salt) from your current session token. This protects cache copies that get separated from your OS keyring - backups, synced folders - and means a cache written by an old session becomes unreadable once the token rotates. It is **not** a defense against a process running as your user, which can read the session token directly.

Turn it on persistently:

```sh
light cache enable  # persists until you disable it
light cache disable
light cache status
light cache clear   # drop all cached responses now
```

Override the persistent setting for a single invocation with a flag, or for a shell session with an environment variable. Both take precedence over the persistent setting:

```sh
light --cache podcasts list     # force on for this call
light --no-cache podcasts list  # force off for this call

LIGHT_CACHE=1 light podcasts list  # 1/0, true/false, yes/no, on/off all accepted
```

## Tests

### Unit tests

Unit tests use request playback with `respx`.

```py
# This will populate `tests/fixtures/` with the response JSON to test against
python scripts/capture_fixture.py

# Run tests
uv run pytest
```

### Live contract test

`tests/test_live_contract.py` tests if the cloud API's response format changes. It validates each GET response against `light_api/openapi-spec.json`, failing if anything is missing from the expected response (and with `--strict-extra`, it fails if anything is added in the expected response). 
It needs real credentials and a registered device, so it is skipped unless you pass `--live` (or set `LIGHT_LIVE_CONTRACT=1`). It currently never runs in CI.

```sh
nix develop
LIGHT_EMAIL=you@example.com LIGHT_PASSWORD=... \
    uv run pytest tests/test_live_contract.py --live -v

# multi-device account: also set LIGHT_PHONE_NUMBER or LIGHT_DEVICE_ID
```

A failure means the API drifted from the spec.
