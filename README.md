
# Unofficial Light Phone API

Unofficial API for interfacing with Light devices. This uses browser automation (Playwright) to automate things.

## Installation

TODO

## Usage

The script needs your Light email, password, and phone number to authenticate into the Light dashboard and do its thing.

Three options:

```sh
1. Environment variable
# Assuming LIGHT_EMAIL, LIGHT_PASSWORD, LIGHT_DEVICE_ID
light music upload song.mp3

2. Secrets file
light --email=/run/secrets/light_email --password=/run/secrets/light_password \
--device-id=/run/secrets/light_device_id music upload song.mp3

3. Command line plaintext (not recommended!)
TODO implement this
light --email=your@email.com --password=password --device-id=1234567890  music upload song.mp3
```

### Music

Supported features:

- Uploading songs, optionally overwriting existing tracks
- Deleting tracks

```sh
# Upload tracks (overwriting existing matching tracks)
light music upload song1.mp3 song2.mp3 song3.mp3

# Upload tracks (don't overwrite)
light music upload --allow-duplicates song1.mp3 song2.mp3 song3.mp3

# Delete tracks
light music delete song.mp3

# Clear all tracks
light music clear
```

### Notes

```sh
```

### Podcasts

```sh
```

## Sample use cases

