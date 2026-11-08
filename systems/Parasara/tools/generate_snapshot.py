"""Generate a minimal Parāśara output JSON from `fixtures/golden_chart_01.json`.

This is a lightweight assembler used for snapshot verification in tests/SME review.
"""
from dataclasses import replace
import hashlib
from pathlib import Path

from systems.Parasara.engine.adapter.surya_adapter import SuryaAdapter
from systems.Parasara.engine.astrostate import AstroState
from systems.Parasara.engine.astrostate_api import (
    AstroStateBuildFailure,
    AstroStateSnapshot,
    freeze_astrostate,
    snapshot_logical_sha256,
    thaw_value,
)
from systems.Parasara.engine.capability import CapabilityReadiness
from systems.Parasara.engine.domain import (
    DashaTimelineFactory,
    DomainBuildRejected,
    TransitSummaryFactory,
)
from systems.Parasara.engine.normalizer import chart_to_astrostate
from systems.Parasara.engine.interpreters.career import (
    interpret_career_domain_snapshot,
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
from systems.Parasara.engine.versioning import (
    EngineConfig,
    EvaluationRecord,
    ResolvedEvaluationVersions,
    RuleVersionResolver,
    SelectionPurpose,
    VersioningError,
    VersioningErrorCode,
    compatibility_v1_config,
    evaluation_instant_from_snapshot,
)
from systems.Parasara.engine.rules.canonical import canonical_json_bytes, canonical_json_data


def _resolve_snapshot_versions(
    snapshot: AstroStateSnapshot | None = None,
    *,
    engine_config: EngineConfig | None = None,
    resolved_versions: ResolvedEvaluationVersions | None = None,
    resolver: RuleVersionResolver | None = None,
) -> ResolvedEvaluationVersions:
    if engine_config is not None and resolved_versions is not None:
        raise ValueError("provide EngineConfig or resolved_versions, not both")
    if resolved_versions is not None:
        if not isinstance(resolved_versions, ResolvedEvaluationVersions):
            raise TypeError("resolved_versions must be ResolvedEvaluationVersions")
        if snapshot is not None:
            resolved_versions.authorize_snapshot(snapshot)
        return resolved_versions
    config = engine_config or compatibility_v1_config(
        evaluation_instant_from_snapshot(snapshot)
        if snapshot is not None else compatibility_v1_config().evaluation_instant
    )
    active_resolver = RuleVersionResolver() if resolver is None else resolver
    return active_resolver.resolve(config, snapshot=snapshot)


def _snapshot_assembly_input(
    snapshot: AstroStateSnapshot,
    *,
    resolved_versions: ResolvedEvaluationVersions | None = None,
) -> OutputAssemblyInput:
    """Orchestrate the validated typed input for the sole OutputAssembler."""

    if resolved_versions is None:
        resolved_versions = _resolve_snapshot_versions()
    planet_strengths = {}
    planets = snapshot.get_planets()
    if planets.value_present:
        for planet in planets.value:
            result = snapshot.get_planet_strength(planet.planet_id)
            if result.value_present:
                detail = result.value.value.get("detail")
                planet_strengths[planet.planet_id] = (
                    thaw_value(detail)
                    if detail else result.value.value.get("value")
                )
    public_planet_strengths = {
        name: ({key: value for key, value in row.items() if key != 'shadbala'} if isinstance(row, dict) else row)
        for name, row in planet_strengths.items()
    }
    career = interpret_career_domain_snapshot(snapshot, resolved_versions=resolved_versions)
    if isinstance(career, DomainBuildRejected):
        raise ValueError("Career DomainPrediction construction was rejected")
    return OutputAssemblyInput(
        engine_metadata=EngineMetadata(
            name=resolved_versions.manifest.engine.identity,
            engine_version=resolved_versions.manifest.engine.version,
            rule_set_family=resolved_versions.manifest.rule_set_family,
            rule_set_version=resolved_versions.manifest.rule_set_version,
            public_meta_engine_version=(
                f"{resolved_versions.manifest.engine.identity}"
                f"@{resolved_versions.manifest.engine.version}"
            ),
            generated_at=None,
            resolved_versions=resolved_versions,
        ),
        astro_diagnostics=AstroDiagnostics(
            lagna_summary=(
                thaw_value(snapshot.get_lagna_summary().value)
                if snapshot.get_lagna_summary().value_present else {}
            ),
            planet_strengths=public_planet_strengths,
            houses=tuple(_snapshot_houses(snapshot)),
            aspects=_snapshot_aspects(snapshot),
        ),
        yogas=(),
        domains=(career.prediction,),
        dasha_timeline=DashaTimelineFactory.unavailable(),
        transit_summary=TransitSummaryFactory.unavailable(),
        explainability=ExplainabilityBundle(),
        warnings=(),
        errors=(),
        output_schema_version=OUTPUT_SCHEMA_VERSION,
        compatibility_profile=SNAPSHOT_COMPATIBILITY_PROFILE,
    )


def _evaluate_snapshot_run(
    snapshot: AstroStateSnapshot,
    *,
    authority: ResolvedEvaluationVersions,
    replay_of_manifest_sha256: str | None = None,
) -> tuple[EvaluationRecord, OutputAssemblyInput]:
    assembly_input = _snapshot_assembly_input(snapshot, resolved_versions=authority)
    assembler = OutputAssembler()
    public_output = assembler.assemble(assembly_input, resolved_versions=authority)
    output_sha256 = hashlib.sha256(canonical_json_bytes(public_output)).hexdigest()
    trace_ids = tuple(
        match.trace_id
        for prediction in assembly_input.domains
        if prediction.source_authority is not None
        for match in prediction.source_authority.ledger.rule_matches
    ) + tuple(item.trace_id for item in assembly_input.yogas)
    record = authority.create_evaluation_record(
        snapshot=snapshot,
        snapshot_sha256=snapshot_logical_sha256(snapshot),
        normalized_input_sha256=snapshot_logical_sha256(snapshot),
        domain_results=assembly_input.domains,
        yoga_results=assembly_input.yogas,
        public_output=public_output,
        rule_match_trace_ids=trace_ids,
        output_sha256=output_sha256,
        replay_of_manifest_sha256=replay_of_manifest_sha256,
        trace={"rule_match_trace_ids": trace_ids},
    )
    return record, assembly_input


def evaluate_snapshot_record(
    snapshot: AstroStateSnapshot,
    *,
    engine_config: EngineConfig | None = None,
    resolved_versions: ResolvedEvaluationVersions | None = None,
    replay_of_manifest_sha256: str | None = None,
) -> EvaluationRecord:
    """Perform one canonical local evaluation and retain exact replay authority."""

    authority = _resolve_snapshot_versions(
        snapshot,
        engine_config=engine_config,
        resolved_versions=resolved_versions,
    )
    record, _ = _evaluate_snapshot_run(
        snapshot,
        authority=authority,
        replay_of_manifest_sha256=replay_of_manifest_sha256,
    )
    return record


def replay_evaluation(
    record: EvaluationRecord,
    *,
    resolver: RuleVersionResolver | None = None,
) -> EvaluationRecord:
    """Freshly evaluate the recorded immutable input under its exact selection."""

    if not isinstance(record, EvaluationRecord):
        raise TypeError("record must be EvaluationRecord")
    replay_config = replace(
        record.resolved_versions.config,
        purpose=SelectionPurpose.REPLAY,
        evaluation_instant=record.evaluation_instant,
    )
    fresh_authority = _resolve_snapshot_versions(
        record.snapshot,
        engine_config=replay_config,
        resolver=resolver,
    )
    if (
        fresh_authority.manifest_fingerprint_sha256
        != record.resolved_versions.manifest_fingerprint_sha256
    ):
        raise VersioningError(
            VersioningErrorCode.INCOMPATIBLE_REPLAY_ENVIRONMENT,
            "Replay resolved a different historical manifest.",
        )
    replayed = evaluate_snapshot_record(
        record.snapshot,
        resolved_versions=fresh_authority,
        replay_of_manifest_sha256=record.resolved_versions.manifest_fingerprint_sha256,
    )
    if replayed.output_sha256 != record.output_sha256:
        raise VersioningError(
            VersioningErrorCode.CONTENT_DIGEST_MISMATCH,
            "Fresh replay output does not match the recorded output digest.",
        )
    return replayed


def assemble_snapshot_output(snapshot: AstroStateSnapshot):
    """Invoke the canonical recorded evaluation for a public dictionary."""

    return canonical_json_data(evaluate_snapshot_record(snapshot).public_output)


def _snapshot_houses(snapshot: AstroStateSnapshot):
    summaries = snapshot.get_house_summaries()
    if summaries.value_present:
        return [thaw_value(item) for item in summaries.value]
    houses = snapshot.get_houses()
    if not houses.value_present:
        return []
    return [
        {"number": item.house_number, "sign": item.sign}
        for item in houses.value
    ]


def _snapshot_aspects(snapshot: AstroStateSnapshot):
    whole = snapshot.inspect_capability("aspects.whole_sign_graph")
    representation = (
        "whole_sign_graph"
        if whole.readiness in (CapabilityReadiness.READY, CapabilityReadiness.READY_EMPTY)
        else "basic_conjunction_list"
    )
    result = snapshot.get_aspect_representation(representation)
    return thaw_value(result.value) if result.value_present else {}


def assemble_output(astro: AstroState | AstroStateSnapshot):
    """Narrow mutable-AstroState compatibility wrapper through freeze."""

    if isinstance(astro, AstroStateSnapshot):
        return assemble_snapshot_output(astro)
    build = freeze_astrostate(astro)
    if isinstance(build, AstroStateBuildFailure):
        raise ValueError("AstroState snapshot construction failed")
    return assemble_snapshot_output(build.snapshot)


def generate(input_path: str, out_path: str):
    chart = SuryaAdapter.load(input_path)
    astro = chart_to_astrostate(chart)
    build = freeze_astrostate(astro)
    if isinstance(build, AstroStateBuildFailure):
        raise ValueError("AstroState snapshot construction failed")
    resolved_versions = _resolve_snapshot_versions(build.snapshot)
    record, assembly_input = _evaluate_snapshot_run(
        build.snapshot, authority=resolved_versions
    )
    assembler = OutputAssembler()
    output = canonical_json_data(record.public_output)
    Path(out_path).write_bytes(
        assembler.snapshot_json_bytes(
            assembly_input, resolved_versions=resolved_versions
        )
    )
    return output


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('input')
    p.add_argument('out')
    args = p.parse_args()
    generate(args.input, args.out)


if __name__ == '__main__':
    main()
