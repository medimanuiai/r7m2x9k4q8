"""Canonical positive/negative graph, runtime outcome, and trusted replay scenarios."""
from pathlib import Path
import json
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from systems.Parasara.engine.rules.canonical import canonical_json_bytes
from systems.Parasara.engine.rules.graph.runtime_contract import digest, GRAPH_CONTRACT_DATA
from systems.Parasara.engine.rules.models import PredicateStatus
from systems.Parasara.engine.versioning import SelectionPurpose
from tests.graph.conftest import analyze, document, dsl_payload
from tests.graph.test_cache_replay import compile_pack
from tests.graph.test_runtime_outcomes import execute
from tests.versioning.conftest import SyntheticCatalogBuilder


def scenario_data():
    rows = []
    for name, edges in (("edgeless", []), ("kahn", [(2, 0, "requires_matches"), (1, 3, "optional_supports")]),
        ("cycle_tail", [(0, 1, "requires_matches"), (1, 0, "optional_supports"), (1, 2, "requires_absence")])):
        result = analyze(document(edges=edges))
        rows.append(dict(name=name, data=result.analysis.to_logical_data() if result.analysis is not None else
            tuple(d.to_logical_data() for d in result.diagnostics)))
    with tempfile.TemporaryDirectory(prefix="prompt08-scenarios-") as temporary:
        for kind in ("requires_matches", "requires_absence", "optional_supports"):
            builder = SyntheticCatalogBuilder(Path(temporary) / kind)
            pack = builder.add_graph(source_id="synthetic/rules.yaml", payload=dsl_payload(3),
                graph_source_id="synthetic/dependencies.json", graph_payload=json.dumps(document(3,
                    [(0, 1, kind), (1, 2, "requires_absence")])).encode(), allowed_purposes=("NEW_EVALUATION", "REPLAY"))
            authority, plan = compile_pack(pack)
            replay_authority, replay_plan = compile_pack(pack, SelectionPurpose.REPLAY)
            for status in PredicateStatus:
                result, calls = execute(authority, plan, {0: status})
                replay, _ = execute(replay_authority, replay_plan, {0: status})
                data = result.record.to_logical_data()
                assert data == replay.record.to_logical_data()
                rows.append(dict(name=kind + ":" + status.value, calls=calls, record=data, replay_equal=True))
    return dict(scenario_schema_version="1.0.0", contract=GRAPH_CONTRACT_DATA, rows=rows)


def main():
    sys.stdout.buffer.write(canonical_json_bytes(scenario_data()) + b"\n")


if __name__ == "__main__":
    main()
