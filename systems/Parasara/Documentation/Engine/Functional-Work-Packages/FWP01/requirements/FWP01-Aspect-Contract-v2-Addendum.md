# FWP01 — Aspect Contract V2 Addendum

Status: selected bounded contract extension; implementation not started

Decision / reconciliation date: 2026-11-06

Parent: [FWP01 — Core Input and Enrichment Closure](FWP01-Core-Input-and-Enrichment-Closure.md)

Authority: the user's bounded V2 documentation instruction and [root AGENTS.md](../../../../../../../AGENTS.md). Use **Python 3.11.9 only**. No second interpreter, version matrix, dependency modernization or Python upgrade is required.

## 1. Decision and reconciled baseline

The V1 prepared graph has global readiness. Exposing its classical subset makes unsupported node-source queries falsely UNMATCHED; withholding it hides supported classical facts. The selected remedy is an explicit additive V2 prepared/predicate profile. Findings 1, 3, 4 and 5 passed targeted independent confirmation and are not reopened. Finding 2 remains unresolved pending implementation and verification. Architecture remains 8/10; FWP01 is not accepted.

Starting branch: `main`; HEAD: `ec6b49a164389aada4e741561d75cb866527e6cf`; staged files: none. The parent starts this documentation session at SHA-256 `15f33b50d3449710ef13d30d49aa0c0e8b6e356294093df36e9ac248b6257456`; `c379506cccc3ba9d3ba2ea9b5af55bcd31b80dc37f4253f95e7c710cce094f70` is historical. A fresh inventory captures 628 readable repository/relevant ignored files before edits and establishes preservation only from this session onward.

Inspected policy evidence includes AGENTS.md, `.python-version`, documentation governance and CI diffs selecting one runtime. Producer/adapter/publication and predecessor implementation changes are separate inherited functional work. The earlier 93-path change list proves concurrent edits, not that every edit was policy-only. The current parent still excludes a V2 contract extension; the bounded exception here is an explicit material scope change, not an inferred consequence of Python policy.

Earlier temporary evidence directories no longer contain their original reports/inventory. The DOCX is now readable and matched its prior session-start hash; its historical preservation remains **UNVERIFIED**. Do not reconstruct missing history, treat a new hash as historical proof or claim overall validation PASS from this documentation task. Report continuing external changes and do not claim a stable baseline if they occur.

This addendum defines the selected exception to parent §§7, 10.3 and 12 only for the contracts/files below. The current instruction authorizes documentation only; a separate instruction starts implementation. No additional specification-review stage is introduced. FWP02, Prompt-09/10, production corpus migration, V2 graph activation and domain/public-output changes remain excluded.

## 2. Versions and immutable content

Explicit profile: `source_scoped_aspects_v2`. Retain exactly the existing seven prepared capability IDs. Only `aspects.whole_sign_graph` becomes `2.0.0`; the other six remain `1.0.0`. The general AstroState capability catalog/queries remain unchanged.

| Contract | V2 identity/version |
|---|---|
| Prepared schema / preparation producer | `2.0.0` / `2.0.0`, separate V2 types and canonical projection |
| Normalization compatibility | `1.0.0` |
| Registry/profile | `parashara-source-scoped-aspects`, `2.0.0` |
| Predicate library | `parashara-predicate-library`, `2.0.0` |
| Predicate / argument schema | `ASPECT_EXISTS@2.0.0` / `2.0.0`; existing argument names/kinds |
| Runtime alias | `ASPECT` binds to V2 only in this profile |
| Condition evaluator | `parashara-condition-evaluator`, `2.0.0`, source-scoped prepared compatibility |
| Compiler implementation | `parashara-rule-dsl-compiler`, `2.0.0`; DSL grammar, macro and compiled-artifact schemas remain `1.0.0` |

Keep PredicateResult fields/status enum, ConditionResult and RuleMatch contracts. Compute separate V2 fingerprints from actual canonical definitions, argument schemas, requirements, handler identities and implementations/pinned helper dependencies. Do not invent digest values or replace V1 fingerprints.

The aspect capability owns immutable `edges`, `source_support` and the pinned `config_version`. Copy validated strict edges and their factual trace, including signs/houses, offsets and artifact evidence, from the immutable general snapshot. Do not run producers, recompute facts, refreeze or add weights.

`source_support` is an immutable tuple of exactly nine records in CANONICAL_PLANETS order. Each record has exactly `source`, `readiness` and `issues`; `source` is the canonical planet ID. The seven classical sources have READY and empty issues; Rahu/Ketu have UNSUPPORTED and `astrology_sme_approval_required`. Node targets of supported classical edges remain valid; node-source edges are forbidden. Derive this fixed support policy only from the validated strict producer's explicit classical scope/provenance, never from counts, absent edges or legacy data. Tuples preserve source order through the existing canonical JSON codec; mapping-key insertion order is not factual identity.

Envelope READY/READY_EMPTY certifies valid scoped content, not complete support for every query. READY_EMPTY describes zero stored supported edges, not calculated absence for unsupported sources. Queries must inspect source support. Missing supply remains MISSING; malformed coverage becomes MALFORMED; version disagreement remains VERSION_MISMATCH. Unavailable capabilities carry no accepted factual envelope.

Reject missing/duplicate/unknown source records, invalid ordering, illegal readiness/issues, a node marked READY, a classical source marked unsupported, unsupported-source edges, duplicate edges and inconsistent scope/provenance/identities/placements. Produce deterministic MALFORMED issues `aspect_coverage_malformed` or `aspect_coverage_contradictory`; do not repair coverage or echo private values/raw exceptions. Validate during preparation/deserialization. Unsafe core/canonical input remains a fatal typed preparation failure.

## 3. Eligibility, filters and exact outcomes

Validate parameters first using existing canonical rules and the V2 schema identity. The only arguments are `from_planet`, `from_house`, `to_planet`, `to_house`; supplied filters are conjunctive. Keep canonical spelling, integer house ranges and invalid-argument diagnostics. Runtime alias support does not permit aliases in canonical DSL authoring.

For valid content, apply this order:

1. An explicit unsupported source returns unavailable before house filtering, even when another filter would exclude it. It never becomes a negative node-aspect assertion.
2. Otherwise the source universe is the explicit source or all nine sources. `from_house` restricts it by natal house. An explicit source needs its own placement; an any-source house filter needs all nine placements to determine eligibility exactly. Missing required source placement yields MISSING_CAPABILITY / `aspect_source_placement_unavailable`. A known empty eligible set is a supported negative.
3. `to_planet` matches that planetary endpoint. `to_house` retains V1 meaning: a planetary target whose natal house equals the filter. Sign-only edges (`target=None`) do not satisfy it, regardless of trace target house. Both target filters require the named target's placement; `to_house` alone requires all nine target placements. Missing required target placement yields MISSING_CAPABILITY / `aspect_target_placement_unavailable`. Unfiltered queries require no house placements merely to identify sources/targets. Existing general aspect-to-sign/house queries keep their separate API meaning.
4. Search matching edges only from eligible READY sources. A supported matching edge proves existence despite other unsupported eligible sources. Without a match, UNMATCHED requires every eligible source to be supported. Target-filter contradictions do not bypass unsupported-source handling for a negative result.

House filters consume `planets.house_placement@1.0.0` as the sole placement owner and honor its readiness; do not extract facts from an unavailable capability or reconstruct placement from trace, sign or array index. Available facts that contradict one another make coverage/graph malformed; a required fact that is merely unavailable retains the typed missing-placement outcome.

The V2 definition requires `aspects.whole_sign_graph@2.0.0` and declares placement version `1.0.0` conditionally for `from_house` or `to_house` (either parameter activates it). The V2 compiler includes that placement requirement in inferred/asserted bindings only when a house filter is supplied. The V2 evaluator applies these conditional checks and §3's fact prerequisites; do not reuse V1's unconditional capability inspection for them. No extra prepared capability is introduced.

| Case, with necessary filter facts available | Status / matched | Diagnostic |
|---|---|---|
| Mars Aries → Moon Cancer, approved fourth aspect | MATCHED / true | none |
| Supported source without matching edge | UNMATCHED / false | none |
| Explicit Rahu/Ketu source | MISSING_CAPABILITY / false | `aspect_source_unsupported` |
| Any-source supported match | MATCHED / true | evidence records incomplete coverage when applicable |
| No match and eligible unsupported sources | MISSING_CAPABILITY / false | `aspect_source_coverage_incomplete` |
| No match and all eligible sources READY, including known empty eligibility | UNMATCHED / false | none |
| Invalid parameters | INVALID_PARAMETERS / false | existing `invalid_parameters`, before capability evaluation |
| Required placement missing | MISSING_CAPABILITY / false | placement code above, no negative assertion |
| Missing/malformed/version-incompatible envelope | MISSING_CAPABILITY / false | existing capability diagnostic and safe coverage issues |

New source/placement errors are recoverable PredicateError values. Details identify capability/version, normalized filters, canonical candidate/eligible and supported/unavailable sources, safe reasons and completeness for the query. MATCHED/UNMATCHED have no capability error; immutable evidence/trace still record support, matched edges and coverage completeness. Never interpret `matched=False` alone as a negative when status is MISSING_CAPABILITY. NOT preserves that status; existing AND/OR precedence and RuleMatch error translation remain unchanged.

## 4. Authority, implementation seams, caching and replay

V1 stays default. Prompt-06 alone resolves once; recognize V2 from an exact, consistent selected manifest component tuple. Do not repurpose EngineConfig's output compatibility profile or infer selection from input/readiness/environment/CWD. Reject mixed V1/V2 components. Current production catalog, v1 manifest, corpus/revisions and knowledge artifacts remain immutable. The new synthetic catalog/manifest/rules authorize non-production evaluation through the existing test-resolver facility only.

Add `prepare_predicate_snapshot_v2(snapshot, *, resolved_versions)`. It consumes the already selected V2 ResolvedEvaluationVersions object, authorizes the snapshot and returns a typed V2 preparation outcome; it never resolves a rule set. Preserve the old projection signature/behavior. Private run bindings retain the exact authority, outside factual canonical bytes; equal strings/fingerprints or copied objects cannot replace it.

Retain the six unchanged capability values and core factual view. Existing non-aspect handlers receive an unchanged V1-compatible projection, with its V1 whole-sign graph unavailable. The V2 dispatcher must not route aspect calls through this view or promote legacy roles/strengths/vargas/node behavior/placeholder flags.

In `evaluator_v2.py`, PredicateEvaluatorV2 and ConditionEvaluatorV2 must be compatible subclasses of the existing evaluator facades. Override the V2 state/registry boundary and evaluation path; do not relabel V1 results or mutate V1 globals. Reuse canonical result/logical semantics and enforce exact authority. Keep V2 key/cache handling in this allowed module; the V1 cache's key-type checks remain unchanged. Cache only definitive results under the existing policy.

Cache identity includes profile/component identities and fingerprints, selected manifest fingerprint, predicate definition/version, normalized arguments, context digest and V2 state digest. The state digest includes schema/preparation/normalization and capability versions, edges and every support record. Exclude opaque tokens, paths and telemetry. Changed coverage changes identity; private same-run checks still reject copied authorities.

RuleDslCompilerV2 owns V2 binding and semantic fingerprints, issuing the existing sealed CompiledRule/CompiledRuleSet shapes through Prompt-07's factories. Preserve parser/AST/macro/resource-limit ownership. Do not call the V1 analyzer and relabel its bindings, registry fingerprint or semantic products. Pin the V2 implementation/dependency fingerprint; leave V1 compiler bytes/digest unchanged. Existing non-graph `RuleEngine.evaluate_compiled_rule` consumes the sealed rule, V2 condition-evaluator subclass, state and context. RuleEngine alone creates RuleMatch.

Replay requires the exact recorded manifest/profile/components. Preserve V1 resolution/replay and prepared bytes/digests. Unavailable historical V2 content or incompatible components fails explicitly with existing typed versioning errors; no V1 fallback, new replay/result hierarchy or public output field is introduced.

Reject a V2 manifest with `dependency_graph != None` during component validation, before graph compilation/plan issuance, with INCOMPATIBLE_COMPONENT_VERSION. Never feed V2 bindings into V1 graph plans. Prompt-08 V1 execution, lineage/evidence separation and complete-ledger atomicity remain unchanged. Production V2 graph support is excluded.

## 5. Exact future implementation scope and dependency check

Only these remaining V2 changes are in scope; the parent lists are not an additional blanket V2 edit allowance.

MODIFY:

```text
systems/Parasara/engine/rules/registry.py
systems/Parasara/engine/rules/snapshot_adapter.py
systems/Parasara/engine/versioning.py
tools/validate_fwp01.py
tests/fwp01/test_snapshot_capabilities.py
tests/fwp01/test_aspects_and_conjunctions.py
tests/fwp01/test_compatibility_and_boundaries.py
tests/fwp01/scenario_manifest.py
tests/fwp01/test_determinism.py
```

ADD:

```text
systems/Parasara/engine/rules/aspect_contract_v2.py
systems/Parasara/engine/rules/evaluator_v2.py
systems/Parasara/engine/rules/dsl/compiler_v2.py
tests/fwp01/test_aspect_contract_v2.py
tests/fwp01/fixtures/aspect-contract-v2.rules.yaml
tests/fwp01/fixtures/aspect-contract-v2-manifest.json
tests/fwp01/fixtures/aspect-contract-v2-catalog.json
```

`aspect_contract_v2.py` owns V2 prepared/envelope types, canonical serialization, profile/catalog/registry factory, argument schema and aspect handler. Registry construction/finalization accepts an explicit catalog while preserving the no-argument V1 default/singleton. The adapter owns the new projection entry; versioning owns finite component verification/compiler dispatch. The two new implementation modules retain evaluator and compiler ownership. Use direct imports; no package-export edit is needed.

Actual signatures were checked. RuleEngine accepts existing CompiledRule and ConditionEvaluator instances, invokes `.predicate_evaluator.require_authority(...)`, then `.evaluate(...)`; the required subclasses satisfy this without editing `rule_engine.py` or `conditions.py`. CompiledRule factories accept explicit fields and retain existing sealing/issuance. Registry currently validates the V1 catalog, requiring the listed explicit-catalog change. V1 prepared serializers enforce V1 type/catalog, requiring separate V2 serializers in the new module. Under these constraints the scope is sufficient; no additional direct dependency is currently identified. Report an exact missing file/reason before extending it if implementation proves otherwise.

Keep `prepared_state.py`, `canonical_predicates.py`, V1 evaluator/condition/DSL implementation files, graph files, general capability contracts, current v1 catalog/manifest, corpus, knowledge artifacts, public producers/consumers, CI and AGENTS.md unchanged. Governance permits only the specified versioned prepared/aspect/library/condition/compiler extension and listed integration files, not rewriting historical artifacts/oracles.

## 6. Finite selected-runtime validation

Use only `jyothishyam_env/prompt01-py311/Scripts/python.exe` (3.11.9). Run one implementation-validation campaign, reusing valid successful checks and running the full repository suite once. Do not duplicate compatibility runs or require second-version evidence.

1. Exercise the complete outcome table through real V2 predicates/conditions: house intersections, unsupported-source precedence, node targets, empty eligibility, missing placement, invalid parameters, malformed/contradictory support, version mismatch, aliases and NOT/AND/OR propagation.
2. Verify mutation isolation, immutable edges/support, serialization/deserialization, canonical digests, cold/warm cache behavior and separation by coverage/components.
3. Compile a synthetic Prompt-06-authorized V2 binding and execute it through existing RuleEngine.evaluate_compiled_rule. Verify RuleMatch status/diagnostics/evidence and same-object authority. Reject copied/mixed authority, compiler/profile mismatch, V1/V2 replay substitution and V2 graph manifests before plan issuance.
4. Prove exact V1 default/catalog/fingerprint/prepared bytes/digests and original predicate/DSL behavior, including after V2 use. Preserve Career/Yoga ordering and the public snapshot: 4,041 bytes, SHA-256 `da2059ba3cfb92eed267f93d1e41585dac1422d68f685022c8609cfd04ad57af`. Preserve `prepared_state.py` SHA-256 `a2fca2dd17edd7092e8bee1cc8431891400d09f979a90f4f44d17b71c9466970`.
5. Preserve existing FWP01 scenario bytes/hash `7a647689108173e5ef3a7344439506a4d65dabb26a24d5ef2b23eb9d2fe117da`; add a separate V2 function/oracle in the allowed files. Test seeds 0/1/42/random, repository/safe alternate CWDs, fresh processes and cold/warm repetitions on the selected runtime. Preserve Prompt-07/08 hashes `248bfabc5cc143ab4d64d5b297e5a3449b2573459f2bd22428708ec1c745beee` / `045d41542a85f2b8b0c327425ac889250b0cf2162c8406f117b8ea4cc8e472b3`.
6. In the authorized implementation task, update validator parent/addendum integrity pins and exact scope interpretation, compose predecessor gates without duplicate compatibility runs, and verify session inventories/protected files/exports/Git state. Never replace missing historical inventory with a current baseline or convert incomplete historical preservation to PASS.

This documentation task runs only integrity, links/scope/signatures, whitespace and before/after checks. Update the ignored private tracker with verified documentation results, preserving independent confirmations and unresolved implementation status. Stop after the report: no automatic implementation, acceptance or extra specification-review stage.
