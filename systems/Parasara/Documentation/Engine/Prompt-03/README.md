# Prompt-03 — InferenceEngine

Status: IMPLEMENTED — PENDING COMMIT REVIEW  
Authority: Prompt-03 requirements and Master Architecture Specification  
Last verified: 2026-08-17

## Boundary

Prompt-03 adds exactly one shared generic `InferenceEngine`:

```text
universal RuleMatch[]
  -> InferenceEngine.aggregate(...)
  -> immutable InferenceResult
  -> narrow Career compatibility projection
  -> unchanged MVP-01 Career JSON
```

The engine consumes only RuleMatch values, optional immutable TimingContext,
explicit DataCompleteness, and immutable InferenceConfig. It does not access
AstroState, raw Surya input, predicates, condition trees, rule YAML, output
assembly, or the system clock.

## Contracts and serialization

`engine/inference/models.py` defines the required enums and frozen contracts:
InferenceError, EvidenceReference, Contribution, ConflictRecord,
InferenceComponent, ExplanationFactor, DataCompleteness, TimingContext, and
InferenceResult. Nested mappings are defensively frozen. Canonical logical
JSON uses finite values, enum strings, arrays for tuples, sorted mapping keys,
and stable SHA-256-derived identities. Strict deserialization rejects unknown
fields, duplicate JSON keys, malformed UTF-8, non-finite numbers, and invalid
model invariants.

Only MATCHED RuleMatches create contributions. Unmatched, excluded, skipped,
unavailable, invalid, and error states remain visible through excluded IDs,
unavailable IDs, typed errors, and source traces. Each contribution retains
rule/version/system identity, base weight, quality, evidence strength,
multipliers, correlation keys, evidence references, and trace lineage.

## Versioned active policy

`config/inference/career_compat_v1.json` is the sole behavior-changing active
configuration. Version `career-compat-1.0.0` records:

- neutral additive normalization at `0.5`, range `[0.0, 1.0]`, no
  intermediate contribution rounding, and three-place public compatibility
  precision;
- natal context and identity priority multipliers;
- unvalidated-quality fallback `1.0` and identity contribution evidence
  strength, matching existing score behavior;
- the documented Rajayoga compatibility weight `0.18` while preserving its
  declared RuleMatch base weight `1.0`;
- category/context conflict records with priority, quality, evidence, and
  independent-support resolution ordering;
- agreement as absolute net contribution divided by absolute contribution;
- MVP-01 confidence weights: coverage `0.4`, matched contribution strength
  `0.3`, and completeness `0.3`;
- explicit zero-weight compatibility factors for quality, context agreement,
  independent evidence, and category diversity. Those metrics are calculated
  and exposed by the generic policy but have neutral coefficients so current
  public confidence remains exact;
- unresolved-conflict and missing-capability policies; and
- explicit no-match result: insufficient evidence, score `0.5`, confidence
  `0.0`.

Confidence is structural confidence, not a probability or a claim of
predictive calibration.

## Career and Yoga migration

Career factual preparation and candidate evaluation remain typed compatibility
adapters. Candidate RuleMatches supply declared meaning. The existing Kendra
base becomes an explicit `career.base_kendra_strength` RuleMatch-backed
contribution; unavailable strength data produces a neutral unavailable
baseline rather than adverse evidence. The shared engine applies the
Rajayoga compatibility override and all final contribution math.

`interpret_career` calls the shared engine exactly once. The outward
projection takes InferenceResult score/confidence and only formats the
existing components, indicators, evidence rows, summary, scoring breakdown,
and fixed public trace ID. It does not apply weights, clip, resolve conflicts,
or calculate confidence. Yoga detection and Yoga public output are unchanged.

The inert `adjusted_score`/`contribution` fields in the historical Career
evaluation-batch persistence contract remain only to preserve Prompt-01/02
logical manifests. Inference and public projection do not consume them; new
callers must use typed Contribution values from InferenceResult.

## Validation

Run on Windows in both supported environments:

```powershell
& 'jyothishyam_env/prompt01-py311/Scripts/python.exe' tools/validate_prompt03.py full
& 'jyothishyam_env/prompt01-py314/Scripts/python.exe' tools/validate_prompt03.py full
```

The validator runs Prompt-03 model/aggregation/Career/architecture tests,
the preserved Prompt-02 RuleMatch contracts, deterministic inference
manifest comparison, WP17 enforcement, the complete repository suite, the
unchanged Prompt-02 scenario manifest, rule lint, strict no-update snapshot
comparison, and protected-artifact/worktree mutation checks. CI uses the same
gate in Python 3.11 and 3.14.

## Scope limitations and Prompt-04 handoff

Prompt-03 migrates Career only. It does not add other domains, statistical
calibration, new astrology, timing calculation, typed DomainPrediction,
OutputAssembler, rule governance, DSL/dependency work, or production-release
certification.

Prompt-04 may establish a stable read-only AstroState query and capability
boundary. Prompt-03 has not added hidden AstroState access or anticipatory
enrichment APIs.
