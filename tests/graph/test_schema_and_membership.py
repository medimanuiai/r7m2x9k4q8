import pytest
from systems.Parasara.engine.rules.graph import GraphAnalysisSucceeded
from tests.graph.conftest import analyze, codes, document, dsl_payload


def test_valid_edgeless_graph_has_exact_membership():
    result = analyze()
    assert isinstance(result, GraphAnalysisSucceeded)
    assert tuple(n.source_order for n in result.analysis.nodes) == (0, 1, 2, 3)
    assert result.analysis.execution_order == (0, 1, 2, 3)


def test_node_boundaries_and_membership_have_exact_distinct_diagnostics():
    empty = analyze(document(0))
    assert codes(empty) == ("P08E107_MEMBERSHIP_MISMATCH", "P08E401_LIMIT_VIOLATION")
    assert empty.diagnostics[1].details == {
        "resource": "nodes", "limit": 1, "observed": 0,
    }

    assert isinstance(analyze(document(1), dsl=dsl_payload(1)), GraphAnalysisSucceeded)
    assert isinstance(analyze(document(256), dsl=dsl_payload(256)), GraphAnalysisSucceeded)

    above = analyze(document(257), dsl=dsl_payload(256))
    assert codes(above) == ("P08E401_LIMIT_VIOLATION",)
    assert above.diagnostics[0].details == {
        "resource": "array_elements", "limit": 256, "observed": 257,
    }

    incomplete = analyze(document(3))
    assert codes(incomplete) == ("P08E107_MEMBERSHIP_MISMATCH",)
    assert incomplete.diagnostics[0].details == {}


@pytest.mark.parametrize("kind", ["requires_matches", "requires_absence", "optional_supports"])
def test_unknown_revision_duplicate_self(kind):
    data = document(edges=[(0, 1, kind)])
    data["rules"][1][kind][0]["rule_id"] = "synthetic.missing"
    assert codes(analyze(data)) == ("P08E101_UNKNOWN_DEPENDENCY",)
    data = document(edges=[(0, 1, kind)])
    data["rules"][1][kind][0]["revision"] = "2.0.0"
    assert codes(analyze(data)) == ("P08E102_REVISION_MISMATCH",)
    assert codes(analyze(document(edges=[(0, 1, kind), (0, 1, kind)]))) == ("P08E104_DUPLICATE_DEPENDENCY",)
    assert codes(analyze(document(edges=[(0, 0, kind)]))) == ("P08E106_SELF_DEPENDENCY",)
import json


@pytest.mark.parametrize("payload", [b'{} {}', b'{} #comment', b'\xef\xbb\xbf{}', b'\xff',
    b'{"x":NaN}', b'{"x":Infinity}', b'{"x":null}', b'{"x":false}', b'{"x":1}',
    b'{"x":1.0}', b'{"x":"\\ud800"}', b'{"x":"e\\u0301"}', b'{"x":[],}', b'[]'])
def test_strict_source_rejects_noncontract_json(payload):
    assert codes(analyze(payload=payload))


@pytest.mark.parametrize("payload", [b'{"a":"x","a":"y"}', b'{"x":{"a":[],"a":[]}}'])
def test_duplicate_keys_at_every_depth(payload):
    assert codes(analyze(payload=payload)) == ("P08E002_DUPLICATE_KEY",)


@pytest.mark.parametrize("source", ["/a.json", "../a.json", "a/../b.json", "a//b.json", "a\\b.json", "C:/a.json", "a.yaml", "a/./b.json"])
def test_unsafe_source_ids(source):
    assert codes(analyze(source_id=source)) == ("P08E001_INVALID_SOURCE",)


@pytest.mark.parametrize("field", ["graph_schema_version", "system", "rule_set_family", "rule_set_version", "rules"])
def test_all_document_fields_required(field):
    data = document()
    del data[field]
    assert "P08E003_SCHEMA_MISMATCH" in codes(analyze(data))


@pytest.mark.parametrize("mutation", ["empty", "missing", "duplicate", "revision", "unknown", "extra", "conflict"])
def test_membership_and_closed_schema(mutation):
    data = document()
    expected = "P08E107_MEMBERSHIP_MISMATCH"
    if mutation == "empty": data["rules"] = []
    if mutation == "missing": data["rules"].pop()
    if mutation == "duplicate": data["rules"][1] = dict(data["rules"][0])
    if mutation == "revision":
        data["rules"][0]["revision"] = "2.0.0"
        expected = "P08E102_REVISION_MISMATCH"
    if mutation == "unknown": data["rules"][0]["rule_id"] = "unknown"
    if mutation == "extra":
        data["rules"][0]["excluded"] = "yes"
        expected = "P08E003_SCHEMA_MISMATCH"
    if mutation == "conflict":
        ref = {"rule_id": "synthetic.a", "revision": "1.0.0"}
        data["rules"][1]["requires_matches"] = [ref]
        data["rules"][1]["optional_supports"] = [ref]
        expected = "P08E105_CONFLICTING_DEPENDENCY"
    assert expected in codes(analyze(data))


@pytest.mark.parametrize("field", ["system", "rule_set_family", "rule_set_version"])
def test_cross_selector_rejected(field):
    data = document()
    data[field] = "other"
    assert "P08E103_VERSION_MISMATCH" in codes(analyze(data))


def test_cross_domain_is_rejected():
    from tests.graph.conftest import dsl_payload
    payload = dsl_payload().replace(b"domains: [synthetic]", b"domains: [other]", 1)
    assert "P08E108_CROSS_DOMAIN_DEPENDENCY" in codes(analyze(document(edges=[(0, 1, "optional_supports")]), dsl=payload))


def test_schema_diagnostics_use_numeric_manifest_positions():
    from tests.graph.conftest import dsl_payload
    data = document(12)
    for row in data["rules"]: row["unsupported"] = "x"
    result = analyze(data, dsl=dsl_payload(12))
    assert tuple(d.node_source_order for d in result.diagnostics) == tuple(range(12))
    data["rules"].reverse()
    assert analyze(data, dsl=dsl_payload(12)).diagnostics == result.diagnostics


def test_unmatched_schema_rows_have_canonical_diagnostic_locations():
    data = document()
    for row, name in zip(data["rules"], ("foreign.z", "foreign.a", "foreign.c", "foreign.b")):
        row["rule_id"], row["unsupported_" + name[-1]] = name, name
    before = analyze(data)
    data["rules"].reverse()
    assert analyze(data).diagnostics == before.diagnostics


def test_identifier_limit_reports_typed_bound():
    data = document()
    data["system"] = "x" * 129
    issue = analyze(data).diagnostics[0]
    assert issue.code == "P08E401_LIMIT_VIOLATION" and issue.details["resource"] == "identifier_code_points"
    issue = analyze(source_id="x" * 252 + ".json").diagnostics[0]
    assert issue.code == "P08E401_LIMIT_VIOLATION" and issue.details["resource"] == "source_id_code_points"
