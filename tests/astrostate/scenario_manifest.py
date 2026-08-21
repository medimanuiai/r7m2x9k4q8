"""Emit deterministic Prompt-04 snapshot/query identities."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from systems.Parasara.engine.adapter.surya_adapter import SuryaAdapter
from systems.Parasara.engine.astrostate_api import (
    astro_query_result_json_bytes,
    freeze_astrostate,
    require_snapshot,
    snapshot_logical_bytes,
)
from systems.Parasara.engine.normalizer import chart_to_astrostate
from systems.Parasara.engine.rules.prepared_state import prepared_state_json_bytes
from systems.Parasara.engine.rules.snapshot_adapter import prepare_predicate_snapshot


def digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def main() -> None:
    rows = {}
    fixtures = ROOT / "systems" / "Parasara" / "fixtures"
    for name in ("golden_chart_01.json", "surya_test_chart.json", "surya_generated_chart.json"):
        source = chart_to_astrostate(SuryaAdapter.load(str(fixtures / name)))
        state = require_snapshot(freeze_astrostate(source))
        logical = snapshot_logical_bytes(state)
        prepared = prepare_predicate_snapshot(state)
        query_rows = tuple(
            astro_query_result_json_bytes(result)
            for result in (
                state.get_planets(), state.get_houses(), state.get_lagna(),
                state.get_planet_house("Mars"), state.get_planet_dignity("Mars"),
                state.get_house_lord(10), state.get_occupants(10),
                state.get_aspects_from("Mars", "basic_conjunction_list"),
                state.get_varga("D9"), state.get_functional_role("Mars"),
                state.get_planet_strength("Mars"), state.get_shadbala("Mars"),
                state.get_current_dasha(), state.get_current_transits(),
            )
        )
        combined_queries = b"\n".join(query_rows)
        rows[name] = {
            "snapshot_bytes": len(logical),
            "snapshot_sha256": digest(logical),
            "logical_digest": state.logical_digest,
            "query_bytes": len(combined_queries),
            "query_sha256": digest(combined_queries),
            "prepared_bytes": len(prepared_state_json_bytes(prepared.state)),
            "prepared_sha256": digest(prepared_state_json_bytes(prepared.state)),
        }
    print(json.dumps(rows, ensure_ascii=False, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
