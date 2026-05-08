
# Light API/CLI/TUI

An unofficial, community-maintained API and CLI/TUI for managing music, notes, and podcasts on Light devices.

This was made by reverse-engineering the API endpoints from the official dashboard. I have obtained Light's blessing for this. You can see the resulting OpenAPI spec in `light_client/`.

## Warning

Because this is an **unofficial** set of tools created through reverse-engineering, this could break at any time if Light decides to change the structure of their API.

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

Supported features:

- Uploading songs, optionally overwriting existing tracks
- Deleting tracks
- Sorting tracks by title/artist/artist-album
- Clear all tracks

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

# Delete tracks
light music delete song

# Delete all tracks (multiple confirmation steps, don't worry)
light music delete-all

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

The TUI offers 

- Vim bindings

---

# Dev stuff

## Regenerate API from spec

```
openapi-python-client generate --path light_client/openapi-spec.json
```

## Tests

### Unit tests

Unit tests use request playback with `respx`.

```py
# This will populate `tests/fixtures/` with the response JSON to test against
python scripts/capture_fixture.py
```

### Smoke tests (TODO)

As this is an unofficial API, Light could change the format at any time. Smoke tests should be added and run regularly (homeserver nightly cronjob?) to catch any breaking API changes asap.
