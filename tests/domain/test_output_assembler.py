from __future__ import annotations

from dataclasses import replace
import hashlib
import json
from pathlib import Path

import pytest

from systems.Parasara.engine.domain import (
    DashaTimelineFactory,
    DomainBuildProduced,
    DomainIssue,
    DomainIssueSeverity,
    TransitSummaryFactory,
)
from systems.Parasara.engine.output_assembler import (
    OUTPUT_SCHEMA_VERSION,
    SNAPSHOT_COMPATIBILITY_PROFILE,
    AstroDiagnostics,
    EngineMetadata,
    ExplainabilityBundle,
    OutputAssembler,
    OutputAssemblyInput,
)
from systems.Parasara.tools.generate_snapshot import generate


ROOT = Path(__file__).resolve().parents[2]


def assembly_input(prediction):
    return OutputAssemblyInput(
        engine_metadata=EngineMetadata(
            name="jyothishyam-parashara",
            engine_version="0.1.0",
            rule_set_family="parashara",
            rule_set_version="v1",
            public_meta_engine_version="jyothishyam-parashara@0.1.0",
        ),
        astro_diagnostics=AstroDiagnostics(
            lagna_summary={}, planet_strengths={}, houses=(), aspects={}
        ),
        yogas=(),
        domains=(prediction,),
        dasha_timeline=DashaTimelineFactory.unavailable(),
        transit_summary=TransitSummaryFactory.unavailable(),
        explainability=ExplainabilityBundle(),
        warnings=(),
        errors=(),
        output_schema_version=OUTPUT_SCHEMA_VERSION,
        compatibility_profile=SNAPSHOT_COMPATIBILITY_PROFILE,
    )


def test_assembler_accepts_only_typed_input_and_is_repeat_pure(career_source):
    _, _, _, outcome = career_source
    assert isinstance(outcome, DomainBuildProduced)
    value = assembly_input(outcome.prediction)
    assembler = OutputAssembler()
    first = assembler.assemble(value)
    second = assembler.assemble(value)
    assert first == second
    assert first is not second
    assert assembler.canonical_json_bytes(value) == assembler.canonical_json_bytes(value)
    assert assembler.logical_digest(value) == hashlib.sha256(
        assembler.canonical_json_bytes(value)
    ).hexdigest()
    with pytest.raises(TypeError):
        assembler.assemble({})


def test_assembler_does_not_mutate_typed_inputs_or_alias_outputs(career_source):
    _, _, _, outcome = career_source
    value = assembly_input(outcome.prediction)
    output = OutputAssembler().assemble(value)
    output["domains"]["career"]["components"].append({"bad": True})
    fresh = OutputAssembler().assemble(value)
    assert {"bad": True} not in fresh["domains"]["career"]["components"]
    assert value.domains[0] is outcome.prediction


def test_cross_object_rule_set_version_mismatch_fails(career_source):
    _, _, _, outcome = career_source
    value = assembly_input(outcome.prediction)
    with pytest.raises(ValueError, match="rule-set"):
        replace(
            value,
            engine_metadata=replace(value.engine_metadata, rule_set_version="v2"),
        )


def test_profile_cannot_silently_suppress_warning_or_error(career_source):
    _, _, _, outcome = career_source
    value = assembly_input(outcome.prediction)
    warning = DomainIssue(
        issue_id="output.warning.test",
        code="CAPABILITY_PARTIAL",
        severity=DomainIssueSeverity.WARNING,
        phase="assembly",
        message="A typed warning cannot be dropped by this profile.",
        recoverable=True,
        details={},
    )
    with pytest.raises(ValueError, match="warning/error"):
        replace(value, warnings=(warning,))


def test_wealth_placeholder_exists_only_in_outward_compatibility(career_source):
    _, _, _, outcome = career_source
    value = assembly_input(outcome.prediction)
    output = OutputAssembler().assemble(value)
    assert tuple(item.domain.value for item in value.domains) == ("career",)
    assert output["domains"]["wealth"] == {
        "summary": "", "score": 0.5, "confidence": 0.5,
        "components": [], "indicators": [],
    }


def test_primary_snapshot_remains_byte_exact(tmp_path):
    output = tmp_path / "snapshot.json"
    generate(
        str(ROOT / "systems" / "Parasara" / "fixtures" / "golden_chart_01.json"),
        str(output),
    )
    approved = ROOT / "systems" / "Parasara" / "tests" / "snapshots" / "output_golden_chart_01.json"
    assert output.read_bytes() == approved.read_bytes()
    assert (len(output.read_bytes()), hashlib.sha256(output.read_bytes()).hexdigest()) == (
        4041,
        "da2059ba3cfb92eed267f93d1e41585dac1422d68f685022c8609cfd04ad57af",
    )
