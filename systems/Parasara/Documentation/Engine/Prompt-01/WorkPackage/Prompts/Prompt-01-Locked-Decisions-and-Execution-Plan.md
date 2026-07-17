# Prompt-01 Locked Architecture Decisions and Execution Plan

Status: APPROVED FOR EXECUTION PLANNING  
Decision owner: Project owner, assisted by architecture review  
Date: 2026-07-14  
Source: Master Architecture, Prompt-01, 25 audits, and Final Audit Consolidation

## 1. Executive decision

The recommendations in `Prompt-01-Final-Audit-Consolidation.md` are adopted with the decisions below.

Prompt-01 remains a bounded predicate-contract migration. It will not redesign astrology rules, domain scoring, universal RuleMatch, inference, the full DSL/compiler, OutputAssembler, or the public API.

Implementation may begin with WP00 after this decision record is placed in the repository. Production behavior changes begin only after a reproducible Python 3.14/3.11 baseline matrix and WP01 characterization tests exist.

## 2. Locked software-architecture decisions

### Result contract

1. Use one canonical `PredicateResult` for all factual predicates.
2. Use these ten fields:
   - `matched`
   - `predicate_id`
   - `predicate_version`
   - `inputs`
   - `evidence`
   - `trace_steps`
   - `errors`
   - `cache_hit`
   - `evaluation_time_ms`
   - `status`
3. Every field is present. Collections use normalized empty immutable values. Only `evaluation_time_ms` may be nullable.
4. `cache_hit` defaults to `False`.
5. Canonical logical equality and hashing exclude `cache_hit` and `evaluation_time_ms`.
6. Full diagnostic serialization may include telemetry, but canonical logical serialization excludes it.

### PredicateStatus truth table

Use exactly these terminal statuses:

- `matched`
- `unmatched`
- `missing_capability`
- `invalid_parameters`
- `error`
- `timeout`
- `skipped`

Truth rules:

- `matched=True` is valid only with status `matched`.
- All other statuses require `matched=False`.
- Contradictory construction is rejected.
- `skipped` is primarily a condition-tree child outcome and is not a factual negative result.

### Immutable representation

Use a project-owned immutable mapping implementation (`FrozenMapping`) plus tuples.

Requirements:

- recursive defensive freezing;
- no shared caller-owned mutable values;
- deterministic key ordering in canonical projection;
- JSON-safe canonical views;
- unsupported values fail explicitly;
- no permissive `default=str` in canonical serialization.

### Errors

Use immutable `PredicateError` with:

- `code`
- `message`
- `predicate_id`
- `details`
- `recoverable`

Use stable string-valued error codes. Messages and details must be safe, bounded and JSON-safe. Raw exceptions and stack traces remain internal diagnostics.

Expected input, capability and known runtime failures become typed results. Unexpected programming defects are re-raised in strict development/test mode and converted to a safe typed error in production mode.

### Timeouts

Use an explicit evaluation-context deadline checked cooperatively at evaluator boundaries. Do not use unsafe thread cancellation. A timeout result is produced only where a timeout can actually be enforced.

### Evidence

Every predicate provides factual evidence for matched and unmatched evaluation when the underlying fact is available.

Evidence must include:

- canonical predicate/entity identity;
- expected value;
- actual observed value;
- comparison or relationship where relevant;
- capability/readiness facts where relevant.

Errors remain in `errors`, not evidence. Domain scores, confidence and narratives never enter predicate evidence.

### Trace

Use immutable `PredicateTraceStep` with:

- stable path-derived `step_id`;
- typed operation name;
- immutable inputs/details;
- factual result or observation;
- optional parent reference;
- optional safe error-code reference.

Timing and cache-hit information are telemetry, not logical trace identity. Trace step order follows semantic evaluation order.

### Registry

Replace the handler dictionary contract with validated predicate definitions containing:

- predicate ID;
- SemVer predicate version;
- description;
- parameter schema;
- required capabilities;
- cacheable;
- deterministic;
- cost class;
- system scope;
- deprecation status;
- replacement predicate;
- explicit aliases.

Reject blank/invalid IDs, invalid versions, non-callable handlers, unknown metadata and incompatible duplicates. Bootstrap deterministically and expose a read-only registry after startup.

`ASPECT` remains an explicit compatibility alias of `ASPECT_EXISTS` until an approved semantic migration says otherwise.

### Parameters

Use strict validation:

- house is a non-Boolean integer from 1 through 12;
- planet IDs are trimmed and normalized through a declared canonical catalog;
- only registered aliases are accepted;
- unknown keys are rejected;
- material type coercion is rejected;
- defaults are declared centrally in schemas;
- canonical parameters are used in result inputs and cache identity.

### Capabilities

Use a registry-declared, versioned capability catalog.

Distinguish:

- unsupported system capability at load/validation time;
- missing chart capability at runtime;
- capability present but empty;
- capability malformed;
- requested entity absent;
- factual result false.

Missing capability never becomes negative evidence.

### AstroState lifecycle and digest

Predicates accept only a prepared immutable factual snapshot.

Preparation and enrichment occur explicitly before predicate evaluation. Predicates do not mutate AstroState, execute enrichment engines, access raw Surya data, perform I/O, read environment/CWD configuration, or read system time implicitly.

The canonical digest covers predicate-relevant normalized facts, capability readiness/content, schema/producer versions and relevant explicit evaluation context. It excludes Yoga/domain outputs, cache telemetry, performance timing and random IDs.

### Evaluation context

Use a minimal typed context containing only behavior-changing values, including explicit evaluation instant when relevant, system/mode and relevant versions. Only predicate-relevant context participates in cache identity.

### Cache

Use an engine-instance-owned bounded cache.

Cache identity includes:

- AstroState digest;
- canonical predicate ID;
- predicate version;
- canonical parameters;
- relevant context identity;
- relevant capability/enrichment versions.

Cache immutable logical values. Derive `cache_hit=True` only on retrieval. Do not cache invalid parameters, programming errors, timeouts or skipped results. Cache missing-capability/error results only if recovery dependencies are explicitly versioned; otherwise do not cache them.

Concurrent mutation of registry, state or cache is unsupported in Stage 01. Evaluation is sequential unless a later architecture stage adds concurrency ownership.

### ConditionResult and operators

Use immutable `ConditionResult` for logical nodes; never label logical operators as predicates.

Semantics:

- evaluate children left-to-right;
- AND stops on the first decisive false/non-success result;
- OR stops on the first decisive matched result;
- NOT requires exactly one child;
- empty AND/OR is invalid;
- malformed nodes and unknown operators are definition errors;
- unknown predicates fail validation and become safe typed definition errors only at defensive runtime boundaries;
- evaluated children retain full typed results;
- unevaluated children receive explicit skipped trace/child representations.

Mixed-status policy:

- definition errors and invalid parameters take precedence over factual results;
- unexpected errors/timeouts remain errors/timeouts unless a previously evaluated child has already made the logical result decisive;
- missing capability is not converted to unmatched;
- factual unmatched is used only when the fact was successfully evaluated.

## 3. Locked compatibility decisions

### Yoga

- Preserve the current valid Yoga rule set, firing, row order and externally consumed keys.
- Use typed internal predicate and condition results.
- Provide a named temporary one-way compatibility projection.
- Replace random logical identity with a stable reference without changing externally required fields unless explicitly approved.
- Continue current Yoga state attachment only as temporary compatibility.
- Remove the five confirmed-unused tuple helpers only after caller verification and characterization tests.

### Career

- Migrate factual checks to the typed predicate boundary.
- Preserve candidate membership and order, score, confidence, components, indicators, evidence meanings, rounding and public dictionary shape exactly.
- Non-factual statuses must not masquerade as unmatched internally.
- Do not implement universal RuleMatch or redesign scoring in Prompt-01.

### Public output and snapshots

- New PredicateResult, status, error and trace fields remain internal by default.
- Public JSON remains unchanged unless separately versioned and approved.
- Approved golden output is a compatibility contract.
- Debug reports and traces are diagnostic artifacts.
- Never auto-update snapshots to make tests pass.
- A snapshot difference requires investigation and explicit approval.

## 4. Astrology-semantic preservation locks

Prompt-01 will not change uncertain astrology semantics.

### PLANET_EXALTED

Preserve current matched/unmatched behavior during Stage 01. Improve typing, validation, evidence and trace only where this does not change results. Record the suspected semantic defect for a later versioned SME-approved correction.

### Aspects

Preserve current valid Yoga behavior. Do not silently choose between list/graph shapes, conjunction semantics, target-none behavior or tradition profiles. Introduce explicit adapters/capability identity sufficient to prevent missing-data confusion, but defer semantic unification.

### Functional roles and HOUSE_LORDS_COMBINATION

Preserve current Career and Yoga results. Freeze the currently effective source/configuration into explicit versioned preparation rather than CWD-dependent predicate-time computation. Do not activate or remove `HOUSE_LORDS_COMBINATION` in a way that changes Yoga firing. Treat it as a separately recorded unresolved rule disposition outside behavioral changes in Prompt-01.

Any change to Yoga firing, Career score/confidence, component membership, indicator membership or ordering stops the package and requires explicit review.

## 5. Deferred decisions

Defer these to later stages:

- universal RuleMatch;
- shared inference/confidence architecture;
- typed domain prediction models;
- OutputAssembler and typed frontend schema;
- full DSL/compiler/AST/macros/references;
- distributed/persistent caching;
- broad concurrent evaluation;
- additional domain implementations;
- Dasha-wide timing redesign, except preventing implicit time from leaking into Prompt-01 predicate behavior.

## 6. Validation environment decision

Use Python 3.14 as the Stage-01 primary development target and Python 3.11 as the compatibility/current-CI baseline. Maintain separate isolated environments and validate both throughout Prompt-01.

WP00 must establish one isolated environment per Python version from the same repository-owned dependency source. Each environment includes at minimum:

- runtime dependencies;
- pytest;
- PyYAML;
- Pydantic;
- existing required pytest plugins and validation tools.

Prefer a pinned Stage-01 requirements/lock file derived from the repository's existing dependency declarations. Do not perform opportunistic dependency upgrades.

Before production changes, perform the following on both Python 3.14 and Python 3.11:

1. Verify the exact interpreter and environment isolation.
2. Verify required imports.
3. Collect tests without writing pytest/bytecode caches where practical.
4. Run the full safe baseline.
5. Run rule lint.
6. Run the approved snapshot comparison in no-update mode using a temporary output path.
7. Record pass/fail/skip results honestly.

Python 3.11 failures are baseline blockers because the current CI contract uses 3.11. Python 3.14 failures must be classified as project, dependency, tooling, or environment incompatibilities. Any 3.14 incompatibility that affects core dependencies or an architectural choice must be resolved before WP02. Do not weaken tests, approve snapshots, modify production behavior, or perform opportunistic dependency upgrades to force either lane to pass.

## 7. Locked execution sequence

Execute one separately reviewed package at a time:

1. **WP00 — Decision record and reproducible Python 3.14/3.11 baseline matrix**
2. **WP01 — P0 characterization fixtures and tests**
3. **WP02 — Immutable status, error, trace and PredicateResult models**
4. **WP03 — Recursive freeze and canonical logical/full serialization**
5. **WP04 — Predicate definition metadata and deterministic registry**
6. **WP05 — Parameter schemas and canonical normalization**
7. **WP06 — Capability catalog and readiness semantics**
8. **WP07 — Prepared AstroState boundary and canonical digest**
9. **WP08 — PLANET_IN_HOUSE reference migration**
10. **WP09 — Evaluator and cache replacement**
11. **WP10 — ConditionResult and deterministic AND/OR/NOT**
12. **WP11 — Remaining registered predicate migration**
13. **WP12 — Active condition-format validation**
14. **WP13 — Yoga typed integration and compatibility projection**
15. **WP14 — Remove confirmed-unused Yoga tuple helpers**
16. **WP15 — Career factual compatibility migration**
17. **WP16 — Remaining caller migration and legacy adapter removal**
18. **WP17 — Architecture, safety and determinism enforcement**
19. **WP18 — Full regression, golden no-update and bounded performance validation**
20. **WP19 — CI gates, documentation and completion evidence**

## 8. Execution controls

- Use a separate implementation prompt and reviewable commit for every package.
- Begin each risky package with its tests.
- Do not combine packages to save time.
- Do not modify files outside the package scope without stopping for review.
- Do not update rules, weights, astrology tables, public schemas or approved snapshots unless the package explicitly authorizes it.
- Preserve unrelated user changes.
- Stop on any unapproved semantic or public-output difference.
- Record commands, results and files modified.
- Do not mark Prompt-01 complete until WP19 evidence exists.

## 9. Completion gates

Prompt-01 is complete only when:

- all ten PredicateResult fields and supporting immutable models are implemented;
- all six registered IDs use validated metadata, versions, schemas and capabilities;
- predicates are pure and operate on prepared state;
- cache identity is content/version based;
- AND/OR/NOT are typed, deterministic and short-circuiting;
- Yoga and Career compatibility tests pass;
- active tuple/raw-boolean predicate contracts and callers equal zero;
- errors, evidence and traces are typed, safe and preserved;
- cold/warm and repeated logical outputs are identical;
- architecture enforcement and CI gates run successfully;
- public JSON and approved snapshots remain unchanged unless separately approved;
- documentation and completion matrix are updated with recorded evidence.

## 10. Release-only urgent register

These do not block Prompt-01 implementation but must be addressed before public release:

- review/anonymize named exact-birth datasets;
- authorize or filter raw generated chart API output;
- replace public child-process detail with safe errors;
- classify/redact report and CI artifacts;
- complete licensing/provenance review;
- decide whether to authorize repository-history exposure scanning.

Keep these tasks separate from Prompt-01 packages.

## 11. Readiness verdict

Architectural decisions locked: **YES**  
Astrology behavior policy locked: **YES — preserve current behavior**  
Compatibility baseline defined: **YES**  
Implementation sequence locked: **YES**  
Validation environment ready: **NO — WP00**  
Prompt-01 execution readiness: **READY TO BEGIN WP00 ONLY**

Production implementation becomes ready after WP00 establishes the environment/baseline and WP01 establishes characterization protection.