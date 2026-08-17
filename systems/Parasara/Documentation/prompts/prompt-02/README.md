# Prompt-02 — Universal RuleMatch

Status: IMPLEMENTED — PENDING COMMIT REVIEW
Authority: Jyothishyam Master Architecture Specification v1.0 and Prompt-02 — RuleMatch
Owner: Parāśara engine maintainers
Last verified: 2026-08-14

## Scope and completion boundary

Prompt-02 adds the universal immutable result of one rule evaluation. The
generic Rule Engine is the sole active producer. Yoga and Career consume that
result through thin compatibility wrappers; their existing public projections
remain one-way and unchanged. This work does not implement inference,
adjusted weights, contributions, scores, confidence, conflicts, narrative,
typed domain output, rule-graph compilation, or later prompts.

## Universal model

`engine/rules/rule_match.py` defines `RuleMatch` with these exact fields:

`rule_match_schema_version`, `system`, `rule_id`, `rule_version`,
`rule_family`, `rule_set_version`, `category`, `domains`, `status`, `matched`,
`base_weight`, `priority`, `context`, `quality`, `predicate_results`,
`evidence`, `provenance`, `metadata`, `trace_id`, `condition_trace_id`,
`trace_references`, and `errors`.

All nested mappings and sequences are canonically frozen. Domains are unique
and sorted. Base weights are declared rule metadata only and must be finite.
`matched` is true exactly when authoritative status is `MATCHED`.

The status taxonomy is `MATCHED`, `UNMATCHED`, `SKIPPED`, `EXCLUDED`,
`MISSING_CAPABILITY`, `INVALID`, and `ERROR`. Invalid definitions and
unavailable/error outcomes therefore remain distinguishable from factual
nonmatches.

## Evidence and trace ownership

`predicate_results` contains the exact evaluated factual leaves in condition
evaluation order. Explicit skipped `ConditionChildResult` records remain in
the canonical condition tree and do not create synthetic PredicateResults.
RuleMatch evidence identifies the condition/fact result and its stable logical
identity; it does not copy the public Yoga evidence or Career scoring rows.

The Rule Engine creates the root deterministic UUIDv5 trace. It retains the
condition node identity, factual predicate trace references, consumer fact
trace references, and bounded typed errors. Trace references use canonical
`(order, trace_type, trace_id, relation)` ordering. Errors preserve
deterministic definition/evaluation detection order with stable de-duplication
and never contain exception strings or machine paths.

## Generic Rule Engine boundary

`engine/rules/rule_engine.py` accepts one complete `ResolvedRule` plus a
canonical `PredicateResult` or `ConditionResult`, then constructs RuleMatch.
It maps predicate statuses without collapsing non-factual states, extracts
evaluated leaves recursively, creates evidence/errors/traces, and provides
canonical collection ordering:

1. priority descending;
2. rule ID ascending;
3. rule version ascending;
4. evaluation-plan position ascending.

Active Yoga and Career code never constructs RuleMatch directly. Model
deserialization reconstructs the immutable value in `rule_match.py`; that is
not an evaluation path.

## Metadata resolution

Current protected rule files predate the full Master Architecture schema and
cannot be changed in this prompt. The adapters therefore resolve only stable
facts already explicit in their active repositories/contracts:

- Yoga resolves system `parashara`, rule-set `v1`, family `yoga`, natal
  context, source category/version/base weight/provenance, and source-plan
  position. Its current enrichment is domain-neutral, so `domains` is empty;
  missing legacy priority resolves to the documented compatibility value zero.
- Career resolves system `parashara`, rule-set `v1`, domain `career`, natal
  context, and existing candidate metadata. Explicit source priority is
  retained; older sources without priority use diagnostic compatibility value
  zero and are marked as such. The unversioned derived lord candidate uses the
  explicit non-production sentinel `legacy-unversioned`. Base weight comes
  from `base_score` when declared or the selected rule's `weights.base`; the
  rajayoga RuleMatch therefore retains `1.0` while its separate legacy Career
  scoring value `0.18` remains outside RuleMatch.
- Invalid Yoga rows receive stable diagnostic identities/version sentinels
  only so they remain inspectable; they never publish a successful RuleMatch.
  A finite source-declared base weight is still mandatory and is never
  synthesized for a diagnostic row.

These are compatibility-resolution policies, not new astrological rules or
production governance approval.

## Serialization

`rule_match_to_logical_data`, canonical JSON bytes, SHA-256 identity, strict
JSON deserialization, and logical round-trip reconstruction are deterministic.
Unknown keys, duplicate JSON keys, non-finite values, malformed UTF-8, and
inference/presentation fields are rejected. The RuleMatch boundary explicitly
rejects `adjusted_weight`, contribution, score, confidence, conflict, and
narrative fields, including when nested in evidence/provenance/metadata.

## Consumer migration

- `YogaEvaluationRecord` contains one RuleMatch and retains only Yoga-specific
  name/source/definition/condition and compatibility projection data. Identity,
  outcome, weight, provenance, and root trace are delegated to RuleMatch.
- `CareerCandidateEvaluation` contains one RuleMatch and one typed Career fact.
  Its adjusted score/contribution fields remain solely in the legacy Career
  compatibility wrapper pending Prompt-03; they are not copied into RuleMatch.
- Both batches expose canonically ordered `rule_matches`. Existing public
  projection order remains source/catalog order to preserve compatibility.
- Internal WP17 trace-artifact hashes change because those diagnostics now
  serialize RuleMatch. Public output, approved snapshots, protected artifacts,
  and personal validation exports do not change.

## Prompt-03 handoff

The next architectural input is `RuleMatch[]`, including factual
PredicateResults, declared base weights, priorities, domains, context,
provenance, statuses, evidence, errors, and traces. Prompt-03 alone owns
contribution signs, adjusted weights, aggregation, normalization, confidence,
correlation, conflicts, and inference explanation. Prompt-03 has not started.

## Validation evidence

Prompt-01's historical validator remains identical to the completed Prompt-01
baseline. Prompt-02 validation uses `python tools/validate_prompt02.py focused`
and `python tools/validate_prompt02.py full`; the scoped entry point reuses the
Prompt-01 protection, snapshot, architecture, collection, and regression gates
without redefining Prompt-01's frozen manifest identity.

Windows validation completed on 2026-08-14:

- Python 3.11.9 and Python 3.14.6 each collected 831 nodes and completed with
  829 passed, 2 skipped; each lane also passed all 22 WP17 checks.
- Both lanes produced ordered-node SHA-256
  `7b4bbfbe7478cbd1677ae6d2689015112e6324dadb87286a1c811ace7deb8dd0`
  and deterministic manifest SHA-256
  `75b65d2cd1420c6261aadbb8159d10fb8c641137ce08d29f2a651952e5cdfaf7`.
- The canonical combined Yoga/Career RuleMatch collection is 53,207 bytes in
  both lanes with SHA-256
  `133b6a10f521df15e140ae5f0655aeacdc05926091293d4014aae29c5e9c77e3`.
- The approved snapshot remains 4,041 bytes with SHA-256
  `da2059ba3cfb92eed267f93d1e41585dac1422d68f685022c8609cfd04ad57af`.
- All 24 protected artifacts and all four personal validation exports remain
  byte-identical. The Next.js 14 production build passed compile, lint,
  type-check, and static generation without public source changes.
