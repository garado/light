
## New on dev
- (perf) use a cheaper api call for auth token validity verification
- (perf) skip auth check if last authentication was within the last 20 min
- (chore) rename the auth cache functions to better disambiguate btwn auth cache and data cache methods (BREAKING for api)
- (perf) add TTL (15min) cache for podcasts/notes/music/devices/tools
    - encrypted at rest, keyed off the session token
    - off by default. `light cache enable/disable/status`, `--cache`/`--no-cache`, `$LIGHT_CACHE` to control it
    - mutating commands invalidate whatever they change
    - `music reorder` updates the cache in place instead of invalidating

## To do
- I think device tool IDs are fixed. Can hardcode them instead of needing to parse them.
- Include the associated playlist in LightTracks
- theres some new stuff in developer tools ?
