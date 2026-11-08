"""Pinned sparse role tables remain unavailable; heuristics cannot fill rows."""
import pytest

from systems.Parasara.engine.enrichments import functional_roles as roles
from systems.Parasara.engine.capability import CapabilityReadiness, CapabilityFactState
from tests.fwp01.test_input_contract import strict_snapshot


def test_incomplete_pinned_roles_are_malformed_without_heuristic(monkeypatch):
    monkeypatch.setattr(roles, "compute_functional_roles", lambda *_: pytest.fail("legacy fallback"))
    state = strict_snapshot()
    assert state.inspect_capability("roles.functional").readiness is CapabilityReadiness.MALFORMED
    assert state.get_functional_role("Venus").state is CapabilityFactState.MALFORMED_CAPABILITY
    audit = state.core.metadata["factual_sources"]["enrichments"]["role_audit"]
    assert "role_table_incomplete" in audit["issues"]
    assert audit["astrology_sme_approved"] is False
    assert len(audit["evidence"]["artifacts"]) == 12


def test_knowledge_uses_governed_semantic_fingerprints():
    _, evidence = roles.load_pinned_knowledge("parashara-aspects")
    assert evidence["manifest_sha256"] == "3e942f97cec7c24079faabc3db358b84177b752a8eb35a7b0d909f84a92d1220"
    assert evidence["artifacts"][0]["content_sha256"] == "fcc896cb5eb8d9d16305b01629a0f6dbe9af0effb691c6929c15fef0154af601"
