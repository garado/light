
# Light API/CLI/TUI

An unofficial, community-maintained API and CLI/TUI for managing music, notes, podcasts, and tools on Light devices.

This was made by reverse-engineering the API endpoints from the official dashboard. (I have obtained Light's blessing for this.)

> [!CAUTION]
> This software is **unreleased and actively in development.** It is public because I need to test package publishing and installation.
>
> The README is being actively updated to prep for the initial beta release. Tests and examples still being written.
> 
> Usage is not yet recommended!

> [!WARNING]
> Because this is an **unofficial** set of tools created through reverse-engineering, this could break at any time if Light decides to change the structure of their API.

## Installation

This repo bundles two separate packages `light-api` and `light-cli-tui`. Install whichever suits your needs.

From PyPI:

```
pip install light-api
pip install light-cli-tui
```

Nix users:

```
{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    light.url = "github:garado/light";
  };

  outputs = { nixpkgs, light, ... }: {
    nixosConfigurations.YOURHOST = nixpkgs.lib.nixosSystem {
      system = "x86_64-linux";
      modules = [
        ({ pkgs, ... }: {
          environment.systemPackages = [
            light.packages.x86_64-linux.light-cli-tui
            light.packages.x86_64-linux.light-api
          ]
        }
      ];
    };
  };
}
```

## Authentication

This needs your Light email, password, and phone number to authenticate into the Light dashboard and operate on the correct device.

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

After the first login, your auth token will be cached. Tokens are good for 30 days.

## Getting started: CLI/TUI

**Note:** As is the case with the official Light dashboard, any changes made through these tools may take a few moments to propagate to the device.

### Music

#### Upload

```sh
# Upload tracks
# Overwrite existing matching tracks (match on file title metadata)
light music upload song1 song2 song3 --match-title-by metadata

# Upload tracks
# Overwrite existing matching tracks (match on filename)
light music upload song1 song2 song3 --match-title-by filename

# Upload tracks
# Don't overwrite existing tracks
light music upload --allow-duplicates song1 song2 song3
```

#### Delete

```sh
# Delete tracks
light music delete song

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
```

### Notes

```sh
```

### Podcasts

```sh
```

### Tools

Available tools: `alarm album calculator calendar camera directions directory hotspot music notes podcasts timer`

```sh
light tools list

light tools add <tool>

light tools remove <tool>
```

### TUI

The TUI offers an easier way of managing music and notes.

```sh
# Launch
light tui
```

TUI-specific features:
- First-class support for Vim bindings
- Music
   - Reorder tracks individually or in visual block mode
- Notes
   - Content preview for both text and audio notes
   - Press `e` to edit text note content in `$EDITOR`

#### Screenshots

<img height="600" alt="image" src="https://github.com/user-attachments/assets/6a98a91c-63e7-4673-8e37-91c280774ef8" />

<img height="600" alt="image" src="https://github.com/user-attachments/assets/10612e61-1dc3-4e4f-95d3-302d95f15bad" />


## Getting started: API

Examples coming soon!

## Tests

### Unit tests

Unit tests use request playback with `respx`.

```py
# This will populate `tests/fixtures/` with the response JSON to test against
python scripts/capture_fixture.py

# Run tests
uv run pytest
```

### Smoke tests (TODO)

As this is an **unofficial** tool, it could break at any time if Light changes the API format. Smoke tests should be added and run regularly (home server nightly cronjob?) to catch any breaking API changes asap.

# Developer stuff

## Regenerate API from spec

The source of truth is the OpenAPI JSON. Python API bindings are automatically generated from that JSON using `openapi-python-client`.

```
cd light_api
openapi-python-client generate --path openapi-spec.json
# this will generate open-api-specification-client (kebab case)
# delete the existing open_api_specification_client contents and copy the kebab-case dir contents to the snake-case dir
```
