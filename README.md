
# Light API

An unofficial, community-maintained API for interacting with Light devices.

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

# Sample use cases

Here's a few of my custom integrations which I think are pretty neat:

## Auto-import Light notes into personal knowledge management system

I use a [Markdown-based note-taking app](https://github.com/silverbulletmd/silverbullet) which is hosted on my home server.

## Auto update music on device

I use a custom music player. In my player, I have added the ability to designate a specific playlist for syncing to the Light Phone. Whenever I make a change to that playlist, the player uses this Light API to didff what's on-device and what's in the playlist and upload/delete songs accordingly.

## Automated music management

# Technical stuff

This uses browser automation to grab the bearer token, then uses Light's API endpoints (spec generated with [OpenAPI devtools](https://github.com/AndrewWalsh/openapi-devtools)) to perform dashboard functions.

## How your credentials stay safe

### 1. Entering your credentials

As mentioned above in the quickstart, this tool offers three ways to enter your credentials. From best to worst, they are: password file, environment variables, plaintext in the command line.

I leave it up to the user to be as secure as you want. I will always recommend using an encrypted password file.

### 2. Using your credentials

This uses [Playwright](https://github.com/microsoft/playwright) for the browser automation to log in to the dashboard with your user/pass to get an auth token. It's open-source, industry standard, and widely trusted.

### 3. Storing your credentials

The bearer token is cached in the system keyring, which is the system's native password manager that you are probably already using - Keychain on MacOS, Credential Manager on Windows, whatever-you-installed on Linux.
