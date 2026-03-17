
# Unofficial Light Phone CLI/API

Unofficial API for interfacing with Light devices.

This uses a combination of browser automation (Playwright) and reverse-engineered Light API endpoints.

## Installation

TODO

## CLI usage

The CLI needs your Light email, password, and phone number to authenticate into the Light dashboard and do its thing.

Three options:

```sh
# 1. Environment variable
# Assuming LIGHT_EMAIL, LIGHT_PASSWORD, LIGHT_DEVICE_ID are set (see .env.example)
light <command>

# 2. Secrets file
light --email=/run/secrets/light_email --password=/run/secrets/light_password \
--device-id=/run/secrets/light_device_id <command>

# 3. Command line (not recommended)
# TODO implement this
light --email=your@email.com --password=password --device-id=1234567890 <command>
```

### Music

Supported features:

- Uploading songs, optionally overwriting existing tracks
- Deleting tracks

```sh
# Upload tracks (overwrite existing matching tracks; match on file title metadata)
light music upload song1.mp3 song2.mp3 song3.mp3 --match-by-title metadata
light music upload song1.mp3 song2.mp3 song3.mp3 -m metadata
light music upload song1.mp3 song2.mp3 song3.mp3 # it's the default if --match-by-title isn't specified

# Upload tracks (overwrite existing matching tracks; match on filename)
light music upload song1.mp3 song2.mp3 song3.mp3 --match-by-title filename
light music upload song1.mp3 song2.mp3 song3.mp3 -m filename

# Upload tracks (don't overwrite)
light music upload --allow-duplicates song1.mp3 song2.mp3 song3.mp3

# Delete tracks
light music delete song.mp3

# Clear all tracks
light music clear

# Sort tracks by title!
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

