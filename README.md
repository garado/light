
# Unofficial Light Phone CLI/API

Unofficial tools and utilities for interfacing with Light devices.

## Installation

TODO

## CLI usage

The CLI needs your Light email, password, and phone number to authenticate into the Light dashboard and do its thing.

Three options:

```sh
# 1. Environment variable
# Assuming LIGHT_EMAIL, LIGHT_PASSWORD, LIGHT_PHONE_NUMBER are set (see .env.example)
light <command>

# 2. Command line
light --email=... --password=... --phone-number=... <command>

# 3. File
light --email-file=... --password-file=... --phone-number-file=... <command>
```

### Music

Supported features:

- Uploading songs, optionally overwriting existing tracks
- Deleting tracks
- Sorting tracks by title/artist
- Clear all tracks

```sh
# Upload tracks
# Overwrite existing matching tracks; match on file title metadata
light music upload song1 song2 song3 --match-title-by metadata

# Upload tracks
# Overwrite existing matching tracks; match on filename
light music upload song1 song2 song3 --match-title-by filename

# Upload tracks
# Don't overwrite existing tracks
light music upload --allow-duplicates song1 song2 song3

# Delete tracks
light music delete song

# Clear all tracks
light music clear

# Sort tracks by title (!!!)
light music sort title --asc
light music sort title --desc

# Sort tracks by artist
light music sort artist --asc
light music sort artist --desc
```

### Notes

```sh
```

### Podcasts

```sh
```

## Sample use cases

