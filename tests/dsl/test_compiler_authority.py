"""Prompt-06 authority sealing and RuleEngine integration."""

from __future__ import annotations

import copy
from dataclasses import replace
import hashlib
from types import SimpleNamespace

import pytest

from systems.Parasara.engine.rules.conditions import ConditionEvaluator
from systems.Parasara.engine.rules.canonical import canonical_json_bytes, canonical_json_data
from systems.Parasara.engine.rules.dsl import CompilationFailed, CompilationSucceeded, RuleDslCompiler
from systems.Parasara.engine.rules.evaluator import PredicateEvaluator
from systems.Parasara.engine.rules.models import PredicateError, PredicateResult, PredicateStatus
from systems.Parasara.engine.rules.prepared_state import PredicateEvaluationContext, prepare_predicate_state
from systems.Parasara.engine.rules.rule_engine import RuleEngine
from systems.Parasara.engine.rules.rule_match import RuleMatchStatus
from systems.Parasara.engine.versioning import VersioningError, manifest_from_data, manifest_to_data


def prepared(house: int = 10):
    source = SimpleNamespace(
        planets=[SimpleNamespace(name="Mars", house=house, sign="Aries", degree=12.0)],
        lagna_sign="Aries", enrichments={}, derived=None, metadata={}, diagnostics={},
    )
    outcome = prepare_predicate_state(source)
    assert outcome.succeeded and outcome.state is not None
    return outcome.state


def test_authorized_compilation_returns_one_deeply_immutable_sealed_rule(resolved_dsl_pack):
    result = resolved_dsl_pack.compilation
    assert isinstance(result, CompilationSucceeded)
    compiled_set = result.compiled_rule_set
    assert compiled_set.resolved_versions is resolved_dsl_pack.resolved
    assert len(compiled_set.rules) == 1
    compiled = compiled_set.rules[0]
    assert compiled.resolved_rule.rule_set_version == "fixture-v1"
    with pytest.raises((AttributeError, TypeError, ValueError)):
        replace(compiled, compiled_semantic_sha256="0" * 64)


def test_rule_engine_uses_condition_evaluator_and_remains_sole_rulematch_owner(resolved_dsl_pack):
    authority = resolved_dsl_pack.resolved
    compiled = resolved_dsl_pack.compilation.compiled_rule_set.rules[0]
    engine = RuleEngine(resolved_versions=authority)
    evaluator = ConditionEvaluator(PredicateEvaluator(resolved_versions=authority))
    match = engine.evaluate_compiled_rule(
        compiled,
        condition_evaluator=evaluator,
        state=prepared(),
        context=PredicateEvaluationContext(),
        evaluation_snapshot_digest="0" * 64,
        evaluation_context={"mode": "synthetic"},
    )
    assert match.status is RuleMatchStatus.MATCHED and match.matched is True

    with pytest.raises(VersioningError):
        engine.build_match(
            compiled.resolved_rule,
            None,
            status_override=RuleMatchStatus.UNMATCHED,
            evaluation_snapshot_digest="0" * 64,
            evaluation_context={},
        )


def test_copied_compiled_rule_and_other_authority_are_rejected(resolved_dsl_pack, synthetic_catalog, minimal_payload):
    original_set = resolved_dsl_pack.compilation.compiled_rule_set
    original = original_set.rules[0]
    with pytest.raises(TypeError):
        copy.copy(original)
    with pytest.raises(TypeError):
        copy.copy(original_set)

    other_source = "synthetic/prompt07_fixture/fixture-v2/rules.yaml"
    other = synthetic_catalog.add_dsl(source_id=other_source, payload=minimal_payload.replace(b"fixture-v1", b"fixture-v2"))
    other_authority = other.resolver.resolve(other.config)
    with pytest.raises(VersioningError):
        RuleEngine(resolved_versions=other_authority).evaluate_compiled_rule(
            original,
            condition_evaluator=ConditionEvaluator(PredicateEvaluator(resolved_versions=other_authority)),
            state=prepared(), context=PredicateEvaluationContext(),
            evaluation_snapshot_digest="0" * 64, evaluation_context={},
        )


def test_label_identical_separately_resolved_authority_is_rejected(synthetic_catalog, minimal_payload):
    source_id = "synthetic/prompt07_fixture/fixture-v1/rules.yaml"
    first_pack = synthetic_catalog.add_dsl(source_id=source_id, payload=minimal_payload)
    first_authority = first_pack.resolver.resolve(first_pack.config)
    first = RuleDslCompiler(resolved_versions=first_authority).compile_authorized(source_id=source_id)
    assert isinstance(first, CompilationSucceeded)

    second_pack = synthetic_catalog.add_dsl(source_id=source_id, payload=minimal_payload)
    second_authority = second_pack.resolver.resolve(second_pack.config)
    assert second_authority is not first_authority
    assert second_authority.manifest_fingerprint_sha256 == first_authority.manifest_fingerprint_sha256

    with pytest.raises(VersioningError):
        RuleEngine(resolved_versions=second_authority).evaluate_compiled_rule(
            first.compiled_rule_set.rules[0],
            condition_evaluator=ConditionEvaluator(PredicateEvaluator(resolved_versions=second_authority)),
            state=prepared(), context=PredicateEvaluationContext(),
            evaluation_snapshot_digest="0" * 64, evaluation_context={},
        )


def test_coordinated_compiled_data_and_digest_replacement_cannot_mint_authority(resolved_dsl_pack):
    compiled_set = resolved_dsl_pack.compilation.compiled_rule_set
    compiled = compiled_set.rules[0]
    replacement_rule = replace(compiled.resolved_rule, priority=compiled.resolved_rule.priority + 1)
    replacement_contract = canonical_json_data(
        resolved_dsl_pack.resolved.manifest.ordered_rule_revisions[0].semantic_contract
    )
    replacement_contract["projections"][0]["priority"] += 1
    replacement_contract["dsl_compiled"]["resolved_rule"]["priority"] += 1
    replacement_digest = hashlib.sha256(canonical_json_bytes(replacement_contract)).hexdigest()
    assert replacement_digest != compiled.compiled_semantic_sha256
    with pytest.raises((TypeError, ValueError)):
        replace(
            compiled,
            resolved_rule=replacement_rule,
            compiled_semantic_sha256=replacement_digest,
        )
    with pytest.raises((TypeError, ValueError)):
        replace(
            compiled_set,
            rules=(compiled,),
            compiled_rule_set_sha256=replacement_digest,
        )


def test_dsl_manifest_accepts_exactly_one_source_artifact(resolved_dsl_pack):
    data = manifest_to_data(resolved_dsl_pack.resolved.manifest)
    artifacts = data["rule_set"]["ordered_source_artifacts"]
    assert len(artifacts) == 1
    without_artifact = manifest_to_data(resolved_dsl_pack.resolved.manifest)
    without_artifact["rule_set"]["ordered_source_artifacts"].clear()
    with pytest.raises(ValueError, match="exactly one rule-dsl-yaml"):
        manifest_from_data(without_artifact)
    artifacts.append(dict(artifacts[0], artifact_id="dsl.duplicate"))
    with pytest.raises(ValueError, match="exactly one rule-dsl-yaml"):
        manifest_from_data(data)


def test_wrong_source_and_post_resolution_source_change_fail_without_partial_rules(resolved_dsl_pack):
    compiler = resolved_dsl_pack.compiler
    wrong = compiler.compile_authorized(source_id="synthetic/not-authorized.yaml")
    assert isinstance(wrong, CompilationFailed) and wrong.compiled_rule_set is None
    assert wrong.diagnostics[0].code == "P07E402_MANIFEST_AUTHORIZATION_FAILURE"

    source_path = resolved_dsl_pack.pack.dsl_source_path
    assert source_path is not None
    source_path.write_bytes(source_path.read_bytes().replace(b"house: 10", b"house: 9"))
    changed = compiler.compile_authorized(source_id=resolved_dsl_pack.pack.dsl_source_id)
    assert isinstance(changed, CompilationFailed) and changed.compiled_rule_set is None
    assert "P07E403_SOURCE_DIGEST_MISMATCH" in tuple(item.code for item in changed.diagnostics)


class _StatusEvaluator(PredicateEvaluator):
    __slots__ = ("_forced_status",)

    def __init__(self, authority, status: PredicateStatus):
        super().__init__(resolved_versions=authority)
        self._forced_status = status

    def evaluate(self, predicate_id, parameters, state, context, *, use_cache=True):
        error = ()
        if self._forced_status is PredicateStatus.ERROR:
            error = (PredicateError(
                code="synthetic_error",
                message="Synthetic evaluator error.",
                predicate_id=predicate_id,
                details={},
                recoverable=False,
            ),)
        return PredicateResult(
            matched=self._forced_status is PredicateStatus.MATCHED,
            predicate_id=predicate_id,
            predicate_version="1.0.0",
            inputs=parameters,
            evidence={},
            trace_steps=(),
            errors=error,
            cache_hit=False,
            evaluation_time_ms=None,
            status=self._forced_status,
        )


@pytest.mark.parametrize(
    ("predicate_status", "rule_status"),
    [
        (PredicateStatus.MATCHED, RuleMatchStatus.MATCHED),
        (PredicateStatus.UNMATCHED, RuleMatchStatus.UNMATCHED),
        (PredicateStatus.MISSING_CAPABILITY, RuleMatchStatus.MISSING_CAPABILITY),
        (PredicateStatus.INVALID_PARAMETERS, RuleMatchStatus.INVALID),
        (PredicateStatus.ERROR, RuleMatchStatus.ERROR),
        (PredicateStatus.TIMEOUT, RuleMatchStatus.ERROR),
        (PredicateStatus.SKIPPED, RuleMatchStatus.SKIPPED),
    ],
)
def test_compiled_entry_preserves_every_existing_runtime_status(
    resolved_dsl_pack,
    predicate_status,
    rule_status,
):
    authority = resolved_dsl_pack.resolved
    compiled = resolved_dsl_pack.compilation.compiled_rule_set.rules[0]
    match = RuleEngine(resolved_versions=authority).evaluate_compiled_rule(
        compiled,
        condition_evaluator=ConditionEvaluator(_StatusEvaluator(authority, predicate_status)),
        state=prepared(),
        context=PredicateEvaluationContext(),
        evaluation_snapshot_digest="0" * 64,
        evaluation_context={"mode": "synthetic-status"},
    )
    assert match.status is rule_status
    assert match.matched is (rule_status is RuleMatchStatus.MATCHED)


@pytest.mark.parametrize(
    ("operator", "expected_status"),
    [("any", RuleMatchStatus.MATCHED), ("all", RuleMatchStatus.UNMATCHED)],
)
def test_compiled_all_any_not_use_existing_short_circuit_runtime(
    synthetic_catalog,
    minimal_payload,
    operator,
    expected_status,
):
    leaf = "{predicate: {id: PLANET_IN_HOUSE, version: \"1.0.0\", arguments: {planet: Mars, house: 10}}}"
    first = leaf if operator == "any" else "{not: " + leaf + "}"
    expression = "{" + operator + ": [" + first + ", " + leaf + "]}"
    payload = minimal_payload.decode().replace(
        "version: fixture-v1",
        f"version: fixture-{operator}",
        1,
    ).replace(
        "    when:\n      predicate:\n        id: PLANET_IN_HOUSE\n        version: \"1.0.0\"\n        arguments:\n          planet: Mars\n          house: 10",
        "    when: " + expression,
    ).encode()
    source_id = f"synthetic/prompt07_fixture/fixture-{operator}/rules.yaml"
    pack = synthetic_catalog.add_dsl(source_id=source_id, payload=payload)
    authority = pack.resolver.resolve(pack.config)
    compilation = RuleDslCompiler(resolved_versions=authority).compile_authorized(source_id=source_id)
    assert isinstance(compilation, CompilationSucceeded)
    match = RuleEngine(resolved_versions=authority).evaluate_compiled_rule(
        compilation.compiled_rule_set.rules[0],
        condition_evaluator=ConditionEvaluator(PredicateEvaluator(resolved_versions=authority)),
        state=prepared(),
        context=PredicateEvaluationContext(),
        evaluation_snapshot_digest="0" * 64,
        evaluation_context={"operator": operator},
    )
    assert match.status is expected_status
    assert len(match.predicate_results) == 1
