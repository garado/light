Manage local response caching.

**Caching is off by default.** When enabled, read commands (e.g. `notes list`)
may return a cached response instead of always hitting the cloud API, improving
performance.

Mutative commands (e.g. `music upload`) always invalidate their relevant cache.

This is a persistent setting. `light cache enable`/`disable` change it for
every future invocation. Override it for a single call with `--cache`/`--no-cache`,
or the `LIGHT_CACHE` environment variable, which both take precedence
over this persistent setting.

Valid `LIGHT_CACHE` values are: `1`/`0`, `true`/`false`, `yes`/`no`, `on`/`off`
