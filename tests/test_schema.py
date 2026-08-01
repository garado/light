import json
from pathlib import Path

from light_cli_tui.schema import schema_hash

REPO_ROOT = Path(__file__).parent.parent
CHECKED_IN_SCHEMA = REPO_ROOT / "schema.json"


def test_checked_in_schema_matches_generated_hash():
    # schema.json is committed for consumers who grab it straight from the repo.
    checked_in = json.loads(CHECKED_IN_SCHEMA.read_text())
    assert (
        checked_in.get("$hash") == schema_hash()
    ), "schema.json is out of date - regenerate with `light schema > schema.json`"
