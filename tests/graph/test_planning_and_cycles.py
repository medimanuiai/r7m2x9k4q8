from tests.graph.conftest import analyze, codes, document


def test_locked_kahn_example():
    result = analyze(document(edges=[(2, 0, "requires_matches"), (1, 3, "optional_supports")]))
    assert result.analysis.execution_order == (1, 2, 0, 3)


def test_cycle_witness_excludes_blocked_tail():
    result = analyze(document(edges=[(0, 1, "requires_matches"), (1, 0, "requires_absence"), (1, 2, "optional_supports")]))
    assert codes(result) == ("P08E201_CYCLE",)
    assert result.diagnostics[0].details["members"] == (0, 1)
    assert result.diagnostics[0].details["witness"] == (0, 1, 0)
import pytest
from tests.graph.conftest import dsl_payload


@pytest.mark.parametrize("kind", ["requires_matches", "requires_absence", "optional_supports"])
def test_each_kind_orders_and_participates_in_cycles(kind):
    assert analyze(document(edges=[(3, 0, kind)])).analysis.execution_order == (1, 2, 3, 0)
    cycle = analyze(document(edges=[(3, 0, kind), (0, 3, kind)]))
    assert cycle.plan is None and cycle.analysis is None
    assert cycle.diagnostics[0].details["witness"] == (0, 3, 0)


def test_priority_is_not_a_topology_tiebreaker():
    payload = dsl_payload().replace(b"priority: 0", b"priority: 99", 1)
    assert analyze(document(edges=[(2, 0, "requires_matches"), (1, 3, "requires_absence")]), dsl=payload).analysis.execution_order == (1, 2, 0, 3)


def test_multiple_scc_witnesses_are_stable_under_declaration_permutations():
    data = document(6, [(0, 1, "requires_matches"), (1, 0, "optional_supports"),
        (2, 3, "requires_absence"), (3, 2, "optional_supports"), (1, 4, "requires_matches"), (3, 5, "requires_matches")])
    before = analyze(data, dsl=dsl_payload(6))
    data["rules"].reverse()
    after = analyze(data, dsl=dsl_payload(6))
    assert before.diagnostics == after.diagnostics
    assert [d.details["members"] for d in before.diagnostics] == [(0, 1), (2, 3)]
