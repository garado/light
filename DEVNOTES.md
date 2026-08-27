
## New on dev
- (feat) parallelized audio conversions and uploads
- (feat) add command to get current music sort mode
- remove -v for --version, and keep -v for --verbose
- (test) live contract test: `pytest tests/test_live_contract.py --live` validates
  real API GET responses against openapi-spec.json. Desktop-only, never in CI.

## to do
- no real support for multi-device accounts. this is a much larger lift
- device id: add method to change the target device
- ffmpeg is an implicit dependency
- make sorting more efficient
- quitting w Ctrl+C sometimes makes Enter stop working ^M
- light music delete doesn't give you an interactive option
- light music delete doesn't say anything from cli
- tui redesign
    - music: show album/artist panes?
