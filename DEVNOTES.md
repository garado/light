
## New on dev
- (perf) use a cheaper api call for auth token validity verification
- (perf) skip auth check if last authentication was within the last 20 min
- (chore) rename the auth cache functions to better disambiguate btwn auth cache and data cache methods (BREAKING for api)
- (perf) add TTL cache for data
