import hashlib
import json
from pathlib import Path
from systems.Parasara.engine.adapter.surya_adapter import SuryaAdapter
from systems.Parasara.engine.normalizer import chart_to_astrostate
from tests.testing_framework.rule_coverage import run_rule_coverage_scan


EXPECTED_HITS = {
    "yoga:rajayoga_naive@1": 1,
    "yoga:dhana_naive@1": 1,
    "yoga:arishta_naive@1": 1,
    "career:strong_in_10_Sun@1.0": 1,
    "career:strong_in_10_Moon@1.0": 1,
    "career:strong_in_10_Mars@1.0": 1,
    "career:rajayoga_naive@1": 1,
}


def test_rule_coverage_reports_only_explicit_typed_records(tmp_path, monkeypatch):
    inp = 'systems/Parasara/fixtures/golden_chart_01.json'
    chart = SuryaAdapter.load(inp)
    astro = chart_to_astrostate(chart)
    output = tmp_path / "coverage.json"
    fixed = Path("tests/reports/coverage_report.json").resolve()
    fixed_before = fixed.read_bytes() if fixed.exists() else None
    first = run_rule_coverage_scan(astro, str(output))
    monkeypatch.chdir(tmp_path)
    second = run_rule_coverage_scan(astro)

    assert first == second
    assert list(first) == ["rules", "predicates"]
    assert first["rules"] == {
        "total_available": 7,
        "total_executed": 7,
        "coverage_ratio": 1.0,
        "hits": EXPECTED_HITS,
    }
    assert first["predicates"] == {
        "ASPECT_EXISTS@1.0.0": {"unmatched": 2},
        "CONDITION_BOUNDARY@1.0.0": {"error": 1},
        "HOUSE_OCCUPANT@1.0.0": {"missing_capability": 1},
        "FUNCTIONAL_ROLE@1.0.0": {"unmatched": 1},
        "PLANET_IN_HOUSE@1.0.0": {"unmatched": 3},
    }
    assert hashlib.sha256(output.read_bytes()).hexdigest() == (
        "60c9e72b2d3b0c45056242df2fcf36e2a06d6d2fc98c9b85696173bb573f33ae"
    )
    assert (fixed.read_bytes() if fixed.exists() else None) == fixed_before
