Show whether local response caching is persistently enabled.

Note this reflects the persistent setting only — it doesn't account for a
`--cache`/`--no-cache` flag or `LIGHT_CACHE` env var that might override it
for a given invocation.

**Example:**

`light cache status`
