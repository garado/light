
## New on dev
- (perf) use a cheaper api call for auth token validity verification
- (perf) skip auth check if last authentication was within the last 15 min
- (chore:internal) rename the auth cache functions to better disambiguate btwn auth cache and data cache methods (BREAKING for api)
- (perf) add TTL (15min) cache for podcasts/notes/music/devices/tools
    - encrypted at rest, keyed off the session token
    - off by default. `light cache enable/disable/status`, `--cache`/`--no-cache`, `$LIGHT_CACHE` to control it
    - mutating commands invalidate whatever they change
    - `music reorder` updates the cache in place instead of invalidating
    - risks of data changing externally:
        - all music position-patching operations force a fresh data fetch to avoid working off stale info
        - delete/rename lookups can still theoretically act on a stale data within the TTL window, but lower risk since it fails loudly. so whatever
- (feat) expose `music capacity` api/cli methods
- (feat) contacts: list all, add one, edit one, delete one, export
- (feat) settings: developer mode get/set

## to do
- I think device tool IDs are fixed. Can hardcode them instead of needing to parse them.
- ahh fuck. there is no real support for multi-device accounts. this is a much larger lift
- add playlist info into tracks to prep for upcoming music tool changes?
- device id: add method to change the target device
