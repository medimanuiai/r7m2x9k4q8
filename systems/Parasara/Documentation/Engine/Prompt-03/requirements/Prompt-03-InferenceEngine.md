Prompt-03 — InferenceEngine

> **Current Python policy - 2026-11-06:** [Root policy](../../../../../../AGENTS.md) selects Python 3.11.9 only
> for development, tests, and CI and explicitly supersedes every dual-version
> requirement below. Retained Python 3.14 results/commands are historical, not
> current instructions. Run appropriate checks once on the selected runtime;
> keep correctness, regression, end-to-end, and same-runtime determinism checks.
> Missing second-version evidence is never a defect or blocker. Future specs,
> prompts, and handoffs must carry this policy; only an explicit user request
> can reinstate multiple Python versions.

Document status: Implementation-ready specification; pending review and approval
Official implementation unit: Prompt-03
Predecessor: Prompt-02 — RuleMatch
Successor: Prompt-04 — AstroState API
Recommended VS Code Codex setting: GPT-5.6 Sol — High
Supported implementation and validation platform: Windows, Python 3.11 and Python 3.14

1. Governing references and authority

Apply this precedence:

Jyothishyam Master Architecture Specification v1.0.docx — governing architecture.

Prompt-Plan.docx — official Prompt sequence and titles.

Prompt-01.docx — universal PredicateResult and typed condition boundary.

The approved standalone Prompt-02 — RuleMatch specification and merged Prompt-02 implementation.

target-state.md and current implementation-status documentation.

Jyothishyam Architecture Consolidation.docx — secondary drafting material only.

If current code or lower-authority documentation conflicts with the Master Architecture, report the conflict and follow the higher authority. Stop for review if compliance requires changing astrology semantics, approved public behavior, or another Prompt’s boundary.

This document specifies only the official Prompt-03 — InferenceEngine unit. Do not introduce Stage numbering, a new audit series, or an excessive work-package structure.

2. Starting state

Prompt-01 and Prompt-02 are complete, validated, published, and merged.

The authorized starting state is:

branch: main;

local and remote main: 9509bd9faa1195e8faf06bef9e6a917ecd6ad07a;

tracked worktree: clean;

Prompt-03 implementation: not started;

universal PredicateResult: active;

universal RuleMatch: active and constructed by the generic Rule Engine;

current active CI gate: Prompt-02 scoped validation;

MVP-01 Career public behavior: protected;

four personal validation exports remain untracked and protected:

Manohar-try1.json

Manohar-try2.json

Manohar-try3.json

Manohar-try4.json

Do not hard-code historical test totals. Establish and report the current baseline before modification.

3. Purpose and architectural role

Create exactly one shared generic InferenceEngine that converts an ordered collection of universal RuleMatch objects into one immutable, deterministic, explainable InferenceResult for a requested domain.

The required boundary is:

PredicateResult
  -> universal RuleMatch[]
  -> shared InferenceEngine
  -> InferenceResult
  -> current compatibility projection
  -> existing MVP-01 Career JSON

The Inference Engine owns:

contribution construction;

application of declared weights and versioned multipliers;

deterministic aggregation;

normalization;

evidence-strength assessment;

independent-evidence handling;

conflict detection and resolution records;

agreement measurement;

data-completeness effects;

confidence calculation;

inference-level explanation factors and trace lineage.

Predicates determine facts. Rules assign declared astrological meaning. The Inference Engine combines those meanings. Domain interpreters select rule packs and present typed results; they do not own generic scoring or confidence.

4. Locked architectural decisions

There is exactly one generic InferenceEngine implementation shared by every domain.

Its only astrological-semantic inputs are already-evaluated universal RuleMatch objects and explicit typed context/configuration.

The engine never evaluates predicates, conditions, YAML rules, or raw chart data.

The engine never mutates AstroState, PredicateResult, RuleMatch, configuration, or consumer state.

RuleMatch.base_weight remains declared rule metadata. Adjusted contribution values exist only in Contribution objects created by the Inference Engine.

Score and confidence are separate outputs with separate calculations and traces.

A normalized score of 0.5 is neutral. It must not silently mean “missing data.” Status and confidence distinguish neutrality from insufficient evidence.

No matched rules produces INSUFFICIENT_EVIDENCE, normalized score 0.5, and confidence 0.0, unless an already-approved versioned compatibility policy requires an exactly equivalent representation.

Positive and negative evidence are both preserved. Conflict resolution never silently deletes the losing evidence.

Current Career scoring and confidence behavior must be moved—not rewritten—into the shared engine through versioned generic configuration.

Existing Career coefficients, thresholds, rounding, ordering, and fallbacks must be discovered from the repository and preserved exactly. Do not invent replacement values.

Yoga-derived Career effects enter inference only through universal RuleMatch and typed Contribution; Yoga detection itself is not redesigned.

The public MVP-01 Career schema and values remain unchanged through a narrow outward compatibility projection.

Full typed DomainPrediction, domain narratives, and public output redesign belong to Prompt-05.

Dasha/transit calculation and new timing behavior are excluded. Prompt-03 accepts an optional frozen timing context only where current data already exists.

Rule-set governance and full version selection remain Prompt-06 responsibilities. Prompt-03 propagates existing resolved versions.

The first active migration target is Career. Do not create empty implementations for Wealth, Marriage, Children, Health, or Safety merely to claim coverage.

5. Scope

Prompt-03 includes:

repository discovery of every existing score, weight, clipping, normalization, confidence, evidence-counting, and conflict-like calculation;

definition of immutable generic inference models and enums;

definition of versioned typed InferenceConfig loaded from versioned data/configuration;

one shared deterministic InferenceEngine.aggregate(...) API;

typed conversion from eligible RuleMatch objects to contributions;

deterministic contribution aggregation and normalization;

explicit no-match and partial-data behavior;

deterministic conflict records and agreement measurement;

confidence computed independently from score;

correlation-aware independent-evidence counting for confidence;

generic inference trace and explanation factors;

migration of current Career scoring/confidence into the shared engine;

migration of Yoga-derived Career effects through the shared engine;

narrow public compatibility projection preserving MVP-01 output;

focused unit, integration, architecture, determinism, serialization, regression, and dual-Python validation;

Prompt-03 documentation and completion records.

6. Explicit non-goals

Do not implement or redesign:

Prompt-04 AstroState query API or capability architecture;

Prompt-05 DomainPrediction, DomainIndicator, NarrativeSection, or final typed public domain models;

Prompt-06 complete rule governance or version-selection infrastructure;

Prompt-07 DSL expansion, macros, references, quantifiers, or compiler redesign;

Prompt-08 dependency graph;

Prompt-09 full architecture verification;

Prompt-10 production readiness or release certification;

predicates, condition-tree semantics, or the universal RuleMatch contract;

new astrology rules, weights, coefficients, thresholds, or interpretations;

new Yoga detection or grading behavior;

new houses, aspects, Vargas, Shadbala, Dashas, transits, or timing calculations;

Wealth, Marriage, Children, Health, Safety, or other new domain implementations;

public narrative generation;

public JSON schema changes;

user-interface features, accounts, persistence, payments, geocoding, or iPhone development;

statistical calibration or claims of predictive accuracy;

persistent/distributed caching, concurrency redesign, or broad performance architecture.

Do not use compatibility preservation as permission to leave final generic aggregation or confidence calculation inside the Career interpreter.

7. Dependencies and prerequisites

Prompt-03 requires:

immutable typed PredicateResult from Prompt-01;

immutable universal RuleMatch from Prompt-02;

deterministic RuleMatch ordering and serialization;

rule identity, domain scope, category, context, priority, base weight, quality, evidence, errors, provenance, and trace references;

existing Career candidate facts and public compatibility projection;

existing Yoga-to-Career compatibility seam;

one frozen evaluation context and resolved current versions where already available;

approved snapshots, protected-artifact checks, and Prompt-02 validation infrastructure.

If active rule matches lack enough declared or compatibility metadata to reproduce current Career direction and weight, use the narrow documented compatibility resolution already established by Prompt-02. Do not edit protected legacy rule sources or fabricate classical metadata. If exact current behavior cannot be reproduced through a generic typed input, stop and report the blocker.

8. Required public engine API

Implement one shared API equivalent to:

class InferenceEngine:
    def aggregate(
        self,
        *,
        domain: str,
        rule_matches: Sequence[RuleMatch],
        timing_context: TimingContext | None,
        data_completeness: DataCompleteness,
        config: InferenceConfig,
    ) -> InferenceResult:
        ...

Equivalent project-conventional typing is acceptable. The following semantics are mandatory:

arguments are explicit; no hidden globals or implicit current time;

domain is canonical and must be present in each included RuleMatch.domains, unless an explicitly declared shared rule is permitted by current metadata;

input RuleMatch objects are already evaluated and immutable;

only MATCHED rules become score-bearing contributions;

other statuses remain available for completeness, warnings, explanation, and trace accounting but never become negative evidence by default;

ordering is canonical and independent of caller container order;

returned InferenceResult is immutable and canonically serializable;

repeated execution with the same inputs/configuration yields byte-identical normalized logical output.

Do not create separate CareerInferenceEngine, YogaInferenceEngine, or per-domain aggregation engines.

9. Required typed contracts

Use the project’s established frozen dataclass, frozen Pydantic, enum, JSON value, and immutable mapping conventions.

9.1 Enums

class InferenceStatus(str, Enum):
    EVALUATED = "evaluated"
    PARTIAL = "partial"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    FAILED = "failed"


class ContributionSign(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"


class ConflictSide(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    TIED = "tied"
    NONE = "none"


class CapabilityAvailability(str, Enum):
    AVAILABLE = "available"
    PARTIAL = "partial"
    UNAVAILABLE = "unavailable"
    NOT_REQUIRED = "not_required"

9.2 Supporting models

@dataclass(frozen=True)
class InferenceError:
    code: str
    message: str
    phase: str
    recoverable: bool
    details: Mapping[str, JsonValue]
    source_rule_id: str | None = None
    source_trace_id: str | None = None


@dataclass(frozen=True)
class EvidenceReference:
    evidence_id: str
    source_type: str
    source_id: str
    trace_id: str | None
    correlation_key: str
    order: int


@dataclass(frozen=True)
class Contribution:
    contribution_id: str
    rule_id: str
    rule_version: str
    rule_set_version: str
    domain: str
    category: str
    context: str
    sign: ContributionSign
    base_weight: float
    rule_quality: float
    evidence_strength: float
    context_multiplier: float
    priority_multiplier: float
    final_contribution: float
    priority: int
    evidence_references: tuple[EvidenceReference, ...]
    correlation_keys: tuple[str, ...]
    source_rule_trace_id: str
    trace_id: str


@dataclass(frozen=True)
class ConflictRecord:
    conflict_id: str
    domain: str
    positive_rule_ids: tuple[str, ...]
    negative_rule_ids: tuple[str, ...]
    highest_priority: int
    resolution_method: str
    winning_side: ConflictSide
    unresolved: bool
    confidence_impact: float
    rationale_code: str
    trace_id: str


@dataclass(frozen=True)
class InferenceComponent:
    component_id: str
    domain: str
    category: str
    raw_contribution: float
    normalized_value: float
    contribution_ids: tuple[str, ...]
    rule_ids: tuple[str, ...]
    evidence_references: tuple[EvidenceReference, ...]
    trace_id: str


@dataclass(frozen=True)
class ExplanationFactor:
    factor_id: str
    factor_type: str
    direction: ContributionSign
    magnitude: float
    source_rule_ids: tuple[str, ...]
    evidence_references: tuple[EvidenceReference, ...]
    trace_id: str

InferenceComponent and ExplanationFactor are generic internal inference models. They are not Prompt-05 public DomainComponent, DomainIndicator, or narrative models.

9.3 Data completeness

@dataclass(frozen=True)
class DataCompleteness:
    domain: str
    d1: CapabilityAvailability
    d9: CapabilityAvailability
    d10: CapabilityAvailability
    aspects: CapabilityAvailability
    functional_roles: CapabilityAvailability
    shadbala: CapabilityAvailability
    dasha: CapabilityAvailability
    transits: CapabilityAvailability
    rule_pack: CapabilityAvailability
    required_capabilities: tuple[str, ...]
    missing_required: tuple[str, ...]
    missing_optional: tuple[str, ...]
    completeness_score: float
    trace_id: str

This model is a frozen input snapshot. Prompt-03 may create the smallest Career adapter needed to populate it from facts already exposed by the repository. It must not redesign AstroState or implement hidden enrichment calculations. completeness_score must be in [0.0, 1.0], derived deterministically under versioned configuration, and agree with the declared missing-capability lists.

9.4 Inference result

@dataclass(frozen=True)
class InferenceResult:
    inference_schema_version: str
    inference_version: str
    system: str
    rule_set_version: str
    domain: str
    status: InferenceStatus
    raw_score: float
    normalized_score: float
    confidence: float
    agreement: float
    positive_contributions: tuple[Contribution, ...]
    negative_contributions: tuple[Contribution, ...]
    neutral_contributions: tuple[Contribution, ...]
    mixed_contributions: tuple[Contribution, ...]
    components: tuple[InferenceComponent, ...]
    conflicts: tuple[ConflictRecord, ...]
    data_completeness: DataCompleteness
    explanation_factors: tuple[ExplanationFactor, ...]
    excluded_rule_ids: tuple[str, ...]
    unavailable_rule_ids: tuple[str, ...]
    errors: tuple[InferenceError, ...]
    trace_id: str

Equivalent names for existing shared primitive/supporting types are acceptable. The logical fields and ownership are mandatory. Do not place public narrative or a DomainPrediction inside InferenceResult.

10. Field and ownership semantics

Versions and identity

inference_schema_version versions serialization shape.

inference_version identifies the algorithm/configuration contract.

system and rule_set_version propagate resolved input identity. Mixed incompatible versions must be rejected rather than silently combined.

stable IDs must be derived deterministically or through the existing stable run-scoped trace mechanism. Random UUIDs are prohibited in normalized logical output.

Scores

raw_score is the deterministic ordered sum of final_contribution values before public normalization.

normalized_score is the configured normalized value in [0.0, 1.0].

confidence is a separate structural-confidence measure in [0.0, 1.0]; it is not a probability claim.

agreement measures consistency among independent score-bearing contributions and is in [0.0, 1.0].

Contribution collections

every score-bearing matched rule produces one or more typed contributions according to explicit rule effect metadata or the documented current compatibility resolver;

positive, negative, neutral, and mixed collections remain separate;

no contribution exists without originating rule identity, evidence references, and trace lineage;

nonmatched, skipped, excluded, unavailable, invalid, and failed rules do not become score-bearing contributions;

their identities remain available through exclusions, unavailable IDs, errors, and traces.

Components

Components are deterministic generic groupings by configured existing category/component mapping. They summarize contributions without changing the total. Do not invent new domain interpretation or public labels.

Explanation factors

Explanation factors are structured inference-level reasons such as dominant support, dominant challenge, unresolved conflict, missing required data, or low independent-evidence diversity. They contain codes/typed data, not final natural-language narrative.

11. Contribution construction

For each eligible matched RuleMatch:

verify the requested domain is in the canonical multi-domain scope or that current metadata explicitly permits shared applicability;

resolve effect sign from explicit existing rule metadata;

where protected legacy rules lack an explicit sign, use only the documented compatibility resolver that reproduces existing Career behavior;

preserve base_weight as declared metadata and use its magnitude exactly once;

resolve rule quality without fabricating production-grade quality;

compute evidence strength through the versioned evidence policy;

select the configured context multiplier;

select the configured priority multiplier or identity multiplier policy;

calculate final_contribution in a fixed deterministic operation order;

attach evidence references, correlation keys, source trace, and contribution trace.

The conceptual formula is:

final_contribution =
    sign_multiplier
    × abs(base_weight)
    × rule_quality
    × evidence_strength
    × context_multiplier
    × priority_multiplier

The exact active Prompt-03 values and compatibility behavior must be extracted from current approved Career behavior and stored in versioned configuration. Do not choose the Master Architecture’s example multipliers merely because they are examples.

If current base_weight is already signed, normalize it once into sign + magnitude; never apply the sign twice. A zero weight is neutral. MIXED must be supported only through explicit metadata or an existing deterministic compatibility split; do not guess a mixed decomposition.

12. Evidence strength and independent evidence

Evidence strength is distinct from rule quality.

The versioned policy may use only facts already present in RuleMatch and its preserved PredicateResult leaves, such as:

evaluated predicate count;

matched factual-leaf count;

evidence completeness;

direct stable fact references;

current approved strength facts already present in evidence;

existing Varga or timing confirmation already represented by the rule context.

It must not:

inspect AstroState or raw Surya JSON;

recompute dignity, aspects, Shadbala, Yoga, Dasha, or transit facts;

treat missing capability as negative evidence;

infer astrological strength from display text;

create new classical thresholds.

Every contribution must expose at least one stable evidence or trace reference. If a legacy compatibility contribution lacks a stable fact ID, use its originating rule and predicate trace IDs and document the limitation.

For confidence, group overlapping evidence through explicit correlation_key, evidence group, or stable source fact IDs. Duplicate rules based on the same underlying fact must not count as fully independent support. Prompt-03 must not silently suppress their score contribution unless the versioned current compatibility policy already does so; duplicate-evidence control initially applies to independence/confidence accounting.

13. Versioned inference configuration

Create one immutable typed InferenceConfig and one versioned YAML/JSON configuration source using existing project conventions.

It must contain or resolve:

inference_version;

supported inference_schema_version;

normalization strategy and parameters;

baseline/neutral score;

public score bounds;

context multipliers;

priority multiplier policy;

rule-quality fallback policy;

evidence-strength policy and bounds;

contribution precision/rounding policy;

component grouping policy;

conflict detection and resolution policy;

agreement policy;

confidence factors, coefficients, penalties, and bounds;

completeness capability weights by domain where current behavior requires them;

no-match behavior;

trace detail policy;

current Career compatibility mapping required to reproduce approved behavior.

Requirements:

all behavior-changing values have names and versions;

no hidden environment-dependent defaults in production paths;

no coefficients are hardcoded in the Career interpreter;

missing requested configuration fails clearly;

configuration is immutable after load;

configuration identity propagates into traces and deterministic output;

Prompt-03 implements only the active strategy required for current Career compatibility plus clean typed extension seams; do not implement unused speculative strategies.

This is inference configuration, not Prompt-06 rule-set governance.

14. Aggregation and normalization

Aggregate contributions in deterministic canonical order. Do not depend on dictionary, set, filesystem, or parallel-completion order.

Required contribution ordering:

requested domain;

context order from versioned configuration;

priority descending;

rule ID ascending;

rule version ascending;

contribution ID ascending.

Use a numerically deterministic summation/precision policy compatible with the current project and validated across Python 3.11 and 3.14.

Normalization requirements:

output range is [0.0, 1.0];

0.5 represents neutral balance;

use the versioned strategy that exactly preserves existing Career public behavior;

clipping, if required by current behavior, must be explicit in trace/explanation data;

do not silently clip intermediate values;

normalization must be generic and not import or reference the Career interpreter;

no-match behavior is Section 4 decision 8;

neutral evidence and insufficient evidence must remain distinguishable through status and confidence.

15. Conflict detection and resolution

Conflicts are disagreements among evidence-backed contributions for the same domain and relevant configured component/context relationship.

The engine must:

preserve all positive and negative contributions;

detect conflicts deterministically;

compare priority, rule quality, evidence strength, domain relevance already declared in metadata, timing context already supplied, and independent support in that order unless the versioned compatibility policy establishes a narrower current sequence;

record the resolution method and winning side;

mark exact unresolved ties explicitly;

apply confidence penalties through versioned configuration;

never erase the losing contribution from explanation or trace;

avoid allowing a short-lived context to silently replace baseline context;

preserve context-separated contribution breakdowns.

For Prompt-03, conflict resolution records may identify a winner without deleting or rewriting contributions. Score aggregation must remain compatible with current Career behavior. Do not invent new cancellation astrology.

Conflict rationale is a deterministic code and structured data. Final user-facing prose belongs later.

16. Agreement and confidence

Confidence is structural confidence, not statistical probability.

The shared engine must calculate it separately from score using versioned factors that account for, at minimum:

rule quality;

evidence strength;

data completeness;

cross-context agreement where multiple existing contexts are present;

number of independent evidence groups;

rule/category diversity;

unresolved conflicts;

missing required/optional capabilities;

calibration input only if an approved calibration artifact already exists.

Do not fabricate historical accuracy or SME quality. Missing unvalidated quality must follow the explicit configured fallback and remain visible in traces.

Required invariants:

0.0 <= confidence <= 1.0;

confidence is not assigned from normalized score;

a high score may have low confidence;

a neutral score may have nonzero confidence when strong independent positive and negative evidence cancel;

unresolved conflict must not increase confidence;

removing required data must not increase confidence;

adding only duplicate evidence must not increase independent-support credit;

no-match insufficient evidence has confidence 0.0;

existing MVP-01 Career confidence must remain unchanged through the migrated versioned policy.

If exact compatibility requires neutral defaults for newly explicit factors, encode and document those defaults in the versioned configuration rather than bypassing the shared engine.

17. Data completeness and missing data

DataCompleteness is supplied explicitly to inference. The engine must not query AstroState, invoke enrichments, or infer capability availability from absent dictionary keys.

Required behavior:

missing required capability may produce PARTIAL or INSUFFICIENT_EVIDENCE according to versioned current policy;

missing optional capability may lower confidence without invalidating the natal conclusion;

missing data never becomes a negative contribution;

an unavailable RuleMatch never becomes an unmatched rule or adverse signal;

completeness effects are domain-aware through configuration, not conditional branches inside Career;

all penalties and status changes are traceable;

fatal invalid input/configuration produces FAILED, typed errors, and no fabricated neutral success.

Prompt-03 must not decide new domain requirements such as advanced D9/D10 policies beyond what current approved Career behavior already uses. Later domain specifications may extend versioned completeness configuration.

18. Timing-context boundary

The API accepts one optional frozen TimingContext because the Master Architecture requires a common inference boundary.

For Prompt-03:

use an existing immutable timing-context type if one is already authoritative;

otherwise define only the smallest generic protocol/value object needed to pass current context identity and existing multipliers;

do not calculate Dasha periods, transits, or current time;

do not call now();

do not add new timing rules;

None is valid for the current natal-only Career path;

timing absence must be represented through completeness/configuration, not invented adverse evidence.

19. Career migration

Before modifying code, characterize the complete current Career pipeline:

candidate creation;

direction/sign determination;

base and adjusted weights;

category/component mapping;

score accumulation;

clipping/normalization;

confidence calculation;

evidence counting;

handling of Yoga-derived Career effects;

missing-data behavior;

ordering and rounding;

public JSON projection;

snapshots and representative fixtures.

Then migrate the behavior:

Career selects or receives its universal RuleMatch objects.

A thin adapter supplies explicit DataCompleteness, optional timing context, and versioned InferenceConfig.

Career calls the shared InferenceEngine.aggregate(...) exactly once per requested Career evaluation.

Existing public Career fields are projected from InferenceResult through one narrow compatibility serializer.

Career may retain domain labels and current narrative compatibility, but it must not calculate generic weights, totals, normalized score, confidence, agreement, or conflicts.

Existing scoring/confidence helper functions must be moved, retired, or converted into generic engine-owned policies. No new caller may depend on legacy Career aggregation.

Exact existing public score, confidence, evidence, ordering, and deterministic JSON must remain unchanged.

If current public compatibility cannot be preserved while removing generic aggregation from Career, stop and report the exact formula/contract conflict. Do not keep two active sources of truth.

20. Yoga-derived Career contributions

Yoga detection remains owned by the Rule Engine/Yoga layer.

Yoga results enter Career inference only through the universal RuleMatch contained in the approved Prompt-02 wrapper.

The Inference Engine converts eligible Yoga RuleMatch objects into contributions using versioned generic context/category configuration.

Do not synthesize base weights, signs, priorities, quality, or provenance from Yoga display names.

Continue using the documented compatibility resolver where protected legacy Yoga rules lack metadata.

Do not calculate a Yoga score in Yoga code or Career code.

Existing Yoga public output and Yoga-only snapshots remain unchanged.

21. Public compatibility boundary

Prompt-03 is an internal architecture migration. The required direction is:

RuleMatch[]
  -> InferenceEngine
  -> InferenceResult
  -> narrow Career compatibility projection
  -> unchanged MVP-01 public JSON

The compatibility projection may rename or select fields required by the existing public contract. It must not:

recompute score or confidence;

apply weights or clipping;

resolve conflicts;

inspect raw RuleMatch evidence to create new conclusions;

mutate InferenceResult;

become a second inference engine.

Do not update approved snapshots. If exact public compatibility is impossible, stop with a readable before/after diff and migration proposal.

22. Error handling

Use typed deterministic errors for:

incompatible rule/system/rule-set versions;

invalid domain scope;

malformed configuration;

unknown normalization or policy identifier;

non-finite numeric inputs;

invalid completeness data;

missing mandatory evidence references;

inconsistent sign/base-weight resolution;

contribution construction failure;

aggregation/normalization failure;

trace-limit or configured evaluation-limit failure.

Expected rule-level unavailable/error statuses must follow explicit inference policy and remain distinguishable. Unexpected programming defects remain visible in strict development/test runs; do not swallow them into a fabricated InferenceResult.

Public compatibility output must not expose stack traces, internal paths, or sensitive birth details.

23. Determinism and serialization

Provide canonical serializers for every new model.

Requirements:

deterministic field order and enum values;

immutable tuples serialize as arrays;

immutable mappings serialize with canonical key order;

finite numbers only;

fixed operation and rounding order;

empty collections serialize as [] or {}, not null;

no memory addresses, Python repr, unordered sets, random IDs, independent system time, or platform-specific paths;

stable contribution, conflict, component, explanation, and trace ordering;

repeated cold/warm evaluations produce identical normalized logical output;

shuffled input RuleMatch order produces identical normalized output;

Windows Python 3.11 and 3.14 produce identical normalized bytes/hashes;

runtime-only timings, if measured, remain outside logical snapshots.

Do not add inference caching in Prompt-03 unless an existing architecture seam requires a minimal compatibility use. If used, its key must include the ordered RuleMatch digest, domain, inference/config version, timing digest, and completeness digest, and cached/uncached logical output must be identical.

24. Validation and invariants

Enforce:

only one generic active aggregation implementation;

all active final Career score and confidence originate from InferenceResult;

every contribution references an eligible matched RuleMatch;

every contribution has evidence/trace lineage;

no predicate or Rule Engine code imports inference implementation;

no domain interpreter implements generic aggregation or confidence;

score, confidence, agreement, completeness, multipliers, and strength factors are finite and within defined bounds;

raw_score equals the deterministic sum of all final contributions;

component totals reconcile with contributions under the configured precision policy;

conflicts reference existing positive/negative contributions;

explanation factors reference existing rules/evidence;

status agrees with evidence, completeness, and errors;

no-match semantics are explicit;

mixed system or incompatible rule-set versions are rejected;

public Career compatibility output remains exact;

no later-Prompt scope or new astrology semantics are introduced.

25. Required repository discovery before modification

Inspect and report:

current branch, local/remote main, merge base, and tracked/untracked status;

current Prompt-02 validation commands and CI workflow;

protected-artifact and approved-snapshot mechanisms;

universal RuleMatch construction, fields, wrappers, and serializers;

every active scoring, weight adjustment, multiplier, sum, clip, normalization, confidence, conflict, agreement, evidence-count, and completeness calculation;

exact Career formulas, constants, rounding, ordering, defaults, and call sites;

Yoga-derived Career weighting path;

all public Career compatibility projections;

all active callers that consume Career score/confidence;

existing configuration-loading conventions;

existing timing/completeness types or closest factual seams;

relevant tests, snapshots, deterministic hashes, architecture gates, and documentation;

likely breaking changes and the narrowest migration plan.

Search broadly and use actual repository paths. Do not assume paths from architecture documents. Present the discovery inventory and baseline before implementation.

26. Implementation safety and sequence

Switch to main using non-destructive commands, fetch normally, and verify local/remote synchronization.

Verify exact starting commit 9509bd9faa1195e8faf06bef9e6a917ecd6ad07a. If different, stop before branching.

Verify the tracked worktree is clean and only the four protected personal exports are untracked.

Record non-mutating identity evidence for personal exports, protected artifacts, approved snapshots, and the current Prompt-02 validator.

Establish the current baseline in Windows Python 3.11, Python 3.14, frontend build, snapshot comparison, and protected-artifact checks.

Perform and report Section 25 discovery and the exact current Career formula.

Create branch agent/parasara-prompt03-inferenceengine only after starting checks pass.

Add typed inference enums, models, validation, and canonical serialization.

Add versioned InferenceConfig containing the extracted current behavior; do not invent coefficients.

Implement the sole generic InferenceEngine and contribution/conflict/confidence policies.

Add the smallest explicit completeness/timing adapters without Prompt-04 or timing redesign.

Migrate Yoga-derived Career effects into contributions.

Migrate Career score/confidence to one shared-engine call and narrow outward compatibility projection.

Retire or prohibit active Career-owned generic aggregation/confidence paths.

Add focused tests and architecture enforcement.

Run focused and full validation in both Python lanes, frontend compatibility, determinism, snapshots, and protected-artifact checks.

Add a narrowly scoped Prompt-03 validator and wire it only after local validation proves the evolved contract. Preserve earlier validators and historical manifests byte-for-byte unless the existing validator architecture explicitly separates immutable historical data from the active gate.

Update only required Prompt-03 documentation and completion records.

Produce the Section 30 report and stop before commit.

Do not commit, push, open a PR, merge, publish, or begin Prompt-04 during the implementation session. Do not use destructive Git commands, force operations, broad cleanup, or snapshot-update modes.

27. Required tests

Model and serialization tests

construction, defaults, immutability, nested defensive freezing;

enum/status serialization;

finite numeric and range validation;

deterministic round trip and byte-stable serialization;

empty collection normalization;

stable IDs and trace references;

cross-Python normalized hash equality.

Contribution tests

positive, negative, neutral, and explicit mixed contributions;

signed legacy weight normalized exactly once;

rule quality, evidence strength, context, and priority factors;

missing/nonvalidated quality fallback;

missing evidence rejection or typed compatibility handling;

correlation keys and duplicate-evidence grouping;

deterministic order and exact math reconciliation;

nonmatched/unavailable/error rules do not contribute.

Aggregation and normalization tests

positive-only, negative-only, neutral-only, and mixed sets;

no matches;

equal cancellation;

score lower/upper bounds;

explicit clipping trace;

normalization strategy/config validation;

shuffled-input equivalence;

repeated-run equivalence;

components reconcile with contributions.

Conflict tests

positive/negative conflict detection;

higher priority;

higher quality;

stronger evidence;

independent support;

exact unresolved tie;

losing evidence preserved;

confidence penalty applied exactly once;

deterministic conflict identity and ordering.

Confidence and completeness tests

confidence independent from normalized score;

high score with low confidence;

neutral score with nonzero confidence under strong opposing evidence;

missing required data does not increase confidence;

missing optional data follows configured policy;

duplicate evidence does not increase independence credit;

disagreement does not increase confidence;

no-match confidence is zero;

bounds and deterministic rounding.

Career/Yoga integration tests

Career calls the shared engine once;

final Career score originates from InferenceResult;

final Career confidence originates from InferenceResult;

prior representative Career scores and confidence remain exact;

Yoga-derived Career effects become typed contributions;

Yoga detection/public output remains unchanged;

evidence and rule/trace lineage remain complete;

missing capabilities do not become adverse signals;

MVP-01 public JSON and deterministic download remain unchanged.

Architecture tests

exactly one active generic inference aggregator;

no generic score/confidence implementation remains in Career or Yoga;

predicates and Rule Engine do not import inference;

Inference Engine does not access AstroState, Surya JSON, predicates, rule YAML evaluation, or output assembly;

compatibility projection does not calculate score/confidence;

no Prompt-04 through Prompt-10 scope;

no hardcoded behavior-changing coefficients outside versioned inference configuration;

previous Prompt validators/manifests remain intact;

active CI invokes the scoped current validator.

Regression tests

full backend suite in Python 3.11 and 3.14;

frontend production build;

approved snapshot exact comparison without update mode;

protected-artifact exact comparison;

personal-export hashes unchanged;

current Yoga/Career/MVP-01 contract tests;

deterministic subprocess/cold/warm/shuffled-input comparisons.

Never weaken or delete valid tests, loosen tolerances, skip incomplete behavior, or approve changed snapshots.

28. Required Windows validation

Run and report exact commands and results for:

pre-change baseline under Windows Python 3.11;

pre-change baseline under Windows Python 3.14;

focused Prompt-03 tests;

architecture enforcement;

Prompt-03 scoped validator under Python 3.11;

Prompt-03 scoped validator under Python 3.14;

full backend regression under both lanes;

frontend production build and relevant MVP-01 integration;

deterministic cross-lane output/hash comparison;

approved snapshot comparison without update mode;

protected-artifact comparison;

four personal-export hash comparison.

Do not substitute Linux validation. Do not report historical test counts as current results.

29. Documentation requirements

Update or create only what Prompt-03 requires:

InferenceEngine API and boundary;

InferenceResult, Contribution, ConflictRecord, DataCompleteness, config, error, and explanation contracts;

versioned aggregation, normalization, conflict, confidence, and precision policies;

structural-confidence limitation;

evidence correlation/independence policy;

Career and Yoga migration notes;

public compatibility boundary;

configuration reference with sources for migrated existing values;

Prompt-03 validator/CI usage;

completion matrix/status and known limitations;

explicit Prompt-04 handoff.

Do not claim statistical calibration, all-domain completion, production readiness, or later-Prompt completion.

30. Acceptance criteria and stopping report

Prompt-03 is acceptable only when:

exactly one shared generic InferenceEngine exists;

immutable typed inference contracts and canonical serializers exist;

all behavior-changing inference values are versioned configuration;

every contribution preserves rule/evidence/trace identity;

aggregation, normalization, conflict records, agreement, completeness, and confidence are deterministic and explainable;

score and confidence are separate;

missing data is not adverse evidence;

duplicate evidence does not inflate independent-support confidence;

Career no longer owns generic final score/confidence calculation;

Yoga does not calculate domain score;

MVP-01 Career score, confidence, evidence, order, public JSON, and snapshots remain unchanged;

no active second aggregation/confidence path remains;

dual-Python, frontend, determinism, snapshots, and protected-artifact gates pass;

Prompt-01 and Prompt-02 historical validators/manifests remain preserved;

documentation truthfully reports scope and limitations;

Prompt-04 has not started;

no commit or publication action has occurred.

After implementation and validation, provide:

Prompt
------
Prompt-03 — InferenceEngine

Starting State
--------------
Branch:
Starting main commit:
Local/remote synchronized:
Tracked worktree:
Protected personal exports:

Baseline
--------
Python 3.11:
Python 3.14:
Frontend:
Approved snapshot:
Protected artifacts:

Repository Discovery
--------------------
Existing Career score formula:
Existing Career confidence formula:
Existing normalization/clipping:
Existing Yoga-derived Career path:
Existing compatibility projections:
Migration risks:

Implementation Status
---------------------
Implemented / Blocked

Shared Contracts
----------------
InferenceResult:
Contribution:
ConflictRecord:
DataCompleteness:
InferenceConfig/version:

Migration Results
-----------------
Shared engine calls:
Career-owned generic aggregators before/after:
Career-owned confidence implementations before/after:
Yoga-derived contribution path:
Compatibility adapters remaining:

Architecture Boundaries
-----------------------
Predicate changes:
RuleMatch contract changes:
AstroState API changes:
Typed DomainPrediction added:
Rule governance/DSL/dependency changes:
Prompt-04 started:

Files Added
-----------

Files Modified
--------------

Tests Added
-----------

Validation Evidence
-------------------
Focused tests:
Python 3.11 full result:
Python 3.14 full result:
Frontend result:
Determinism hashes:
Approved snapshot:
Protected artifacts:
Personal exports:
Earlier validator integrity:

Public Behavior
---------------
MVP-01 score unchanged:
MVP-01 confidence unchanged:
MVP-01 schema unchanged:
Public snapshot unchanged:

Documentation Updated
---------------------

Known Limitations
-----------------

Remaining TODO
--------------

Risks or Blockers
-----------------

Acceptance Criteria
-------------------
PASS / FAIL with failed items listed

Ready for Commit Review
-----------------------
YES / NO

Ready for Prompt-04
-------------------
YES / NO — architectural handoff only; Prompt-04 not started

Recommended Next Action
-----------------------
Review Prompt-03 implementation and validation before authorizing commit/push/PR.

Stop after the report. Do not commit merely because validation passes.

31. Explicit handoff boundary to Prompt-04

Prompt-03 ends with:

Universal RuleMatch[]
  -> shared InferenceEngine
  -> immutable InferenceResult
  -> narrow unchanged Career compatibility projection

Prompt-04 will later establish the stable read-only AstroState query API and capability-access boundary. Prompt-03 must not add hidden AstroState queries, enrichment computation, or broad capability APIs in anticipation of Prompt-04.

Final instruction to VS Code Codex

Implement only Prompt-03 — InferenceEngine.

Begin from synchronized clean main at 9509bd9faa1195e8faf06bef9e6a917ecd6ad07a. Establish the current baseline and inspect the real Career formula before choosing files or configuration values. Move the existing approved Career scoring/confidence behavior into one versioned shared inference service without changing astrological meaning or MVP-01 output. Preserve Prompt-01/02 contracts, snapshots, protected artifacts, and the four personal exports.

Implement and validate fully, produce the required report, and stop before commit, push, PR, merge, Prompt-04, or unrelated work.