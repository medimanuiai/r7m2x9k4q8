Prompt-02 — RuleMatch

> **Current Python policy - 2026-11-06:** [Root policy](../../../../../../AGENTS.md) selects Python 3.11.9 only
> for development, tests, and CI and explicitly supersedes every dual-version
> requirement below. Retained Python 3.14 results/commands are historical, not
> current instructions. Run appropriate checks once on the selected runtime;
> keep correctness, regression, end-to-end, and same-runtime determinism checks.
> Missing second-version evidence is never a defect or blocker. Future specs,
> prompts, and handoffs must carry this policy; only an explicit user request
> can reinstate multiple Python versions.

Document status: Implementation-ready specification; pending review and approval
Official implementation unit: Prompt-02
Predecessor: Prompt-01 — PredicateResult
Successor: Prompt-03 — InferenceEngine
Supported implementation and validation platform: Windows, Python 3.11 and Python 3.14

1. Governing references and authority

Implement this specification under the following precedence:

Jyothishyam Master Architecture Specification v1.0.docx — governing architecture and highest authority.

Prompt-Plan.docx — official Prompt-00 through Prompt-10 sequence and titles.

Prompt-01.docx — authoritative predecessor contract for PredicateResult and typed condition evaluation.

target-state.md and the Prompt-01 README.md — approved current-state and completion records.

Jyothishyam Architecture Consolidation.docx — secondary historical drafting material only.

If repository behavior or a lower-authority document conflicts with a higher-authority requirement, do not silently choose one. Preserve the higher-authority requirement, document the discrepancy, and stop for review if compliance would require an architectural contradiction or an unapproved public-contract migration.

This document is the standalone implementation specification for the official Prompt-02 — RuleMatch unit. References to “Stage 2” in historical material are not a separate project unit and must not be used in branches, reports, tests, or documentation created for this work.

2. Background and current state

Prompt-01 is complete. It established the universal immutable PredicateResult contract, typed predicate statuses/errors/traces, validated predicate definitions and parameters, deterministic factual-state preparation, PredicateEvaluator, engine-owned bounded caching, and typed condition-tree evaluation. Active tuple, raw-Boolean, and dictionary predicate contracts were retired from production paths.

MVP-01 is also complete and merged. It provides the account-free Birth-to-Career web journey and depends on the existing Career response behavior. Prompt-02 is an internal rule-contract migration. It must not change astrological meaning, Career scoring, user-visible MVP-01 behavior, approved snapshots, protected artifacts, or deterministic JSON output.

At the authorized starting point:

branch is main;

local and remote main are expected at commit 2c8d5ce6e86cb8a747e3f0b634116deb7083256c;

tracked worktree is clean;

Prompt-02 implementation has not started;

the following personal validation exports are intentionally untracked and must not be modified, staged, committed, deleted, renamed, or included in cleanup operations:

Manohar-try1.json

Manohar-try2.json

Manohar-try3.json

Manohar-try4.json

Do not rely on obsolete test counts. Establish the current baseline from the synchronized starting commit before modifying code.

3. Purpose and architectural role

Create one universal, typed, immutable, deterministic RuleMatch contract for all active generic Rule Engine evaluations.

The required boundary is:

Immutable evaluation snapshot
  -> PredicateEvaluator
  -> PredicateResult
  -> typed condition-tree evaluation
  -> generic Rule Engine
  -> RuleMatch
  -> existing consumers and compatibility projections

The generic Rule Engine alone constructs RuleMatch objects. Predicates answer factual questions and return only PredicateResult. Condition evaluation combines factual results without assigning domain meaning. The Rule Engine applies declarative rule metadata to the evaluated condition and creates RuleMatch. Prompt-03 will later combine RuleMatch[] into scores, confidence, conflicts, and domain inference.

Prompt-02 must establish a trustworthy boundary between factual evaluation and inference without implementing inference early.

4. Locked architectural decisions

The following decisions are final for Prompt-02:

Only the generic Rule Engine constructs the universal RuleMatch.

Predicates return PredicateResult; they never return or construct RuleMatch.

RuleMatch carries the rule’s declared base_weight only.

RuleMatch must not contain adjusted_weight, final_contribution, normalized score, confidence, conflict resolution, or aggregation output.

Weight adjustment, context multipliers, priority application during combination, contribution calculation, aggregation, normalization, confidence, and conflict resolution belong exclusively to Prompt-03 InferenceEngine.

Multi-domain applicability is represented by deterministic domains: tuple[str, ...]. It must not be collapsed into an ambiguous singular domain.

status is the authoritative outcome. matched remains a required compatibility-friendly Boolean constrained by status.

PredicateResult owns factual leaf evidence and predicate-level errors.

The typed condition result owns logical composition, evaluated-child order, short-circuit behavior, and skipped condition branches.

RuleMatch owns rule identity, outcome, declared semantic metadata, rule-level evidence references, rule-level errors, and the root rule trace.

Evidence is referenced or summarized across layers; complete serialized leaf evidence must not be copied into multiple containers.

Prompt-02 propagates existing rule-set identity, lifecycle, provenance, quality, and metadata. It does not implement Prompt-06 governance, version selection, promotion, rollback, or strict/experimental policy redesign.

Compatibility adapters must be narrow, explicit, tested, and prevented from becoming the new internal source of truth.

The repository—not this specification—determines the exact existing Yoga and Career file paths and migration seams during the required discovery pass.

5. Scope

Prompt-02 includes only the work necessary to establish and adopt universal RuleMatch:

discover all active rule loaders, evaluators, result shapes, Yoga consumers, Career consumers, serializers, tests, and compatibility boundaries;

define the RuleMatchStatus, RuleMatchError, trace-reference support, and immutable RuleMatch model;

define deterministic validation and serialization;

make the generic Rule Engine the sole constructor of RuleMatch;

preserve typed PredicateResult objects and condition-tree trace lineage;

validate and propagate existing rule identity, version, rule-set version, family, category, domains, context, priority, declared base weight, quality, provenance, and metadata;

migrate active Yoga and Career rule-match consumers to universal RuleMatch or a narrow typed wrapper/projection around it;

eliminate active untyped rule-match dictionaries and duplicate rule-match models where migration is within this unit’s boundary;

preserve existing public JSON through explicit compatibility projections where necessary;

add focused contract, migration, determinism, serialization, architecture, and regression protection;

update Prompt-02 technical documentation and completion records.

6. Explicit non-goals

Do not implement, redesign, or expand any of the following:

Prompt-03 score aggregation, adjusted weights, inference, normalization, confidence, or conflict resolution;

Prompt-04 AstroState API;

Prompt-05 typed domain outputs or broad interpreter redesign;

Prompt-06 complete rule-set selection, governance, approval, promotion, rollback, or historical replay infrastructure;

Prompt-07 DSL operators, macro system, references, compiler redesign, or AST expansion;

Prompt-08 rule dependency graph or rule-to-rule execution;

new houses or aspects work;

Vargas, Dashas, transits, timing redesign, or new enrichments;

new prediction domains or new astrology rules;

astrology mathematics, rule conditions, rule weights, priorities, or semantic meaning;

Career scoring formulas, Career confidence, or Career narratives;

Yoga detection semantics;

MVP user-interface features;

accounts, persistence, payments, geocoding, or iPhone development;

broad performance, concurrency, distributed cache, or deployment architecture;

another audit series, another implementation numbering system, or an excessive work-package hierarchy.

Do not refactor unrelated code merely because a cleaner design is possible.

7. Dependencies and prerequisites

Prompt-02 depends on the completed Prompt-01 contracts:

immutable PredicateResult and its canonical serializer;

typed predicate statuses, errors, and trace steps;

validated predicate registry metadata and parameters;

deterministic evaluation context and factual-state digest behavior relevant to predicates;

typed condition-tree evaluation that preserves evaluated predicate results, logical order, errors, and skipped branches;

existing generic Rule Engine and declarative rule metadata;

existing Yoga and Career behavior that must remain compatible.

Prompt-02 may use the current AstroState and query seams but must not perform the Prompt-04 API redesign. It may propagate currently resolved rule-set metadata but must not perform Prompt-06 governance work. It must preserve current DSL semantics and must not anticipate Prompt-07 or Prompt-08.

If any required Prompt-01 contract is missing or an active production path still depends on a legacy predicate tuple/raw-Boolean contract, stop and report the prerequisite failure. Do not silently reopen Prompt-01 or hide the gap inside RuleMatch.

8. Universal RuleMatch contract

Use the project’s established typed-model convention—frozen dataclass, frozen Pydantic model, or an equivalent immutable model. The logical contract is:

class RuleMatchStatus(str, Enum):
    MATCHED = "matched"
    UNMATCHED = "unmatched"
    SKIPPED = "skipped"
    EXCLUDED = "excluded"
    MISSING_CAPABILITY = "missing_capability"
    INVALID = "invalid"
    ERROR = "error"


@dataclass(frozen=True)
class RuleMatchError:
    code: str
    message: str
    phase: str
    recoverable: bool
    details: Mapping[str, JsonValue]
    source_predicate_id: str | None = None
    source_trace_id: str | None = None


@dataclass(frozen=True)
class RuleTraceReference:
    trace_id: str
    trace_type: str
    relation: str
    order: int


@dataclass(frozen=True)
class RuleMatch:
    rule_match_schema_version: str
    system: str
    rule_id: str
    rule_version: str
    rule_family: str
    rule_set_version: str
    category: str
    domains: tuple[str, ...]
    status: RuleMatchStatus
    matched: bool
    base_weight: float
    priority: int
    context: str
    quality: float | None
    predicate_results: tuple[PredicateResult, ...]
    evidence: Mapping[str, JsonValue]
    provenance: Mapping[str, JsonValue]
    metadata: Mapping[str, JsonValue]
    trace_id: str
    condition_trace_id: str | None
    trace_references: tuple[RuleTraceReference, ...]
    errors: tuple[RuleMatchError, ...]

Equivalent names for pre-existing shared JSON, error, or trace-reference types are acceptable. The public logical fields and semantics above are not optional. Do not add an adjusted_weight alias.

The implementation may use internal constructors or factories, but ordinary callers must not instantiate partially validated RuleMatch objects. Construction must flow through a generic Rule Engine-owned factory or equivalent internal boundary.

9. Field definitions

rule_match_schema_version: str

Version of the RuleMatch serialization contract. It is distinct from rule, rule-set, engine, predicate-library, DSL, and output-schema versions. It must be nonempty and deterministically serialized.

system: str

Interpretation-system scope, such as parashara, obtained from resolved rule or evaluation metadata. Shared infrastructure must not infer a system from a domain name.

rule_id: str

Canonical stable rule identifier. It must be nonempty and unique within system + rule_set_version under the existing loader contract. Display names must not substitute for identity.

rule_version: str

Version of the individual rule definition. Never fabricate or silently default a production value when the resolved rule contract requires one.

rule_family: str

Existing rule family or equivalent stable classification from declarative metadata. It is not a Python class name.

rule_set_version: str

Resolved rule-set version already available to the current evaluation. Prompt-02 propagates it into RuleMatch; Prompt-06 will later own complete selection and governance wiring.

category: str

Canonical rule category from declarative metadata, such as a Yoga or domain-specific category. It must not be derived from a consumer’s file path.

domains: tuple[str, ...]

Complete multi-domain scope declared by the rule. Values must be canonical, unique, immutable, and serialized in deterministic canonical order. A rule applicable to Career and Wealth must retain both values. A compatibility serializer may project one requested domain only when an existing public contract requires it, but that projection must not mutate or narrow the universal model.

Rules with genuinely system-wide diagnostic scope may use an empty tuple only if the existing rule metadata explicitly permits domain-neutral rules. Absence of required domain metadata must otherwise be invalid.

status: RuleMatchStatus

Authoritative rule-evaluation outcome as defined in Section 10.

matched: bool

Compatibility-friendly Boolean derived from or validated against status. It is True only when status == MATCHED; it is False for every other status. It must never be used to erase the distinction among unmatched, skipped, excluded, unavailable, invalid, and failed outcomes.

base_weight: float

Declared semantic weight read from the selected rule metadata. It must be finite, retain existing approved semantics, and satisfy the existing rule-schema range. Prompt-02 must not change its value or invent a new numeric range.

base_weight is input metadata for Prompt-03. It is not a score contribution. No context multiplier, quality multiplier, priority multiplier, normalization, clipping, or sign resolution may be applied in Prompt-02.

priority: int

Declared rule priority from metadata. Prompt-02 preserves and validates it according to the existing rule schema. Prompt-02 does not use it to resolve conflicts or calculate contributions.

context: str

Canonical declared or resolved rule context already supported by the current engine, such as natal, yoga, or another existing context. Prompt-02 must not introduce new timing semantics.

quality: float | None

Existing declared rule-quality metadata, when present. A non-null value must be finite and within the existing accepted range; if the repository has no approved quality value, use None rather than fabricating one. Prompt-03 may later use quality during inference.

predicate_results: tuple[PredicateResult, ...]

The authoritative evaluated factual leaves used by the condition tree, in deterministic evaluation order. Preserve the exact immutable typed results. Do not convert them to booleans or dictionaries internally. Do not duplicate the same logical predicate evaluation solely to inflate evidence.

Short-circuited predicate leaves that were never evaluated are not fake PredicateResult objects. They remain condition-tree skipped branches and are referenced through the condition trace.

evidence: Mapping[str, JsonValue]

Immutable rule-level evidence index or summary. It may contain stable AstroState fact IDs, rule metadata references, condition-node IDs, predicate trace IDs, and concise derived labels already produced by the current rule semantics.

It must not contain complete copied serializations of every PredicateResult, full duplicated condition traces, inference output, narrative, scores, confidence, or mutable objects. Empty evidence serializes as {}.

provenance: Mapping[str, JsonValue]

Existing source and authorship information carried from rule metadata. Preserve available source type, source title/name, chapter/section/verse, translation or notes, rule author, reviewer, and approval fields without inventing missing facts. Empty provenance may be used only when allowed by the existing non-production rule contract; Prompt-02 does not create new governance approval.

metadata: Mapping[str, JsonValue]

Remaining immutable, JSON-safe rule metadata needed for replay, compatibility, or explainability. Do not use this field as an untyped escape hatch for adjusted weights, scores, confidence, domain predictions, mutable runtime state, or full copied evidence.

trace_id: str

Stable root trace identity for this rule evaluation. It must be deterministic or produced by the project’s stable run-scoped trace service. Random UUIDs that alter normalized logical output are prohibited.

condition_trace_id: str | None

Reference to the typed condition-tree trace. It is required whenever condition evaluation began and produced a trace. It may be None when the rule was excluded or rejected before condition evaluation.

trace_references: tuple[RuleTraceReference, ...]

Ordered references connecting the rule trace to condition, predicate, validation, or exclusion traces without embedding full trace payloads repeatedly. Each reference must have a stable identity, typed relationship, and deterministic order.

errors: tuple[RuleMatchError, ...]

Rule-level validation, construction, availability, exclusion-policy, or evaluation errors. Predicate-level errors remain authoritative inside their originating PredicateResult; a RuleMatchError may reference them by predicate and trace identity but must not duplicate the full error payload. Empty errors serialize as [].

10. Status and outcome semantics

The status model is mandatory:

Status

Meaning

matched

Condition evaluation

matched

Condition was validly evaluated and true.

True

Completed sufficiently to determine true.

unmatched

Condition was validly evaluated and false with required facts available.

False

Completed sufficiently to determine false.

skipped

The rule was deliberately not evaluated under an existing explicit execution policy, request filter, or condition-level prerequisite.

False

May not have started.

excluded

The rule was excluded by an already-existing selection, lifecycle, system-scope, or approval policy.

False

Must not be fabricated as false.

missing_capability

Required factual capability was unavailable, so truth could not be determined.

False

Partial or unavailable.

invalid

Rule definition, metadata, resolved input, or construction data was invalid.

False

Must not become an ordinary nonmatch.

error

Evaluation began or construction was attempted but failed unexpectedly or through a defined evaluation error.

False

Failed.

Additional rules:

unmatched means “evaluated false,” never “could not evaluate.”

A missing capability must not be converted to unmatched.

Invalid production rules must continue to fail existing strict loading/startup behavior. An invalid RuleMatch is permitted only in an existing diagnostic/quarantine path that explicitly represents invalid rules; Prompt-02 must not weaken strict loading.

excluded propagates current policy decisions only. Prompt-02 must not invent Prompt-06 governance behavior.

Condition-level short-circuited children do not make the whole rule skipped if the parent condition validly resolves to matched or unmatched.

Diagnostic/internal evaluation may retain every status. Existing normal/public projections may continue to expose only the subset they currently expose.

11. Evidence and trace ownership

Use the following ownership model:

Predicate layer

PredicateResult owns:

one factual leaf outcome;

canonical predicate inputs;

factual evidence;

predicate-level trace steps;

predicate-level errors;

predicate version and cache semantics.

Condition layer

The typed condition result owns:

AND/OR/NOT composition;

declared left-to-right evaluation order;

evaluated child references;

short-circuit reason;

skipped child/node identities;

condition-level errors and status;

the condition trace identity.

Prompt-02 must use the existing Prompt-01 condition contract. It may add only the smallest compatibility field or adapter necessary to expose stable references needed by RuleMatch; it must not redesign or expand the DSL.

Rule layer

RuleMatch owns:

rule identity and semantic metadata;

rule-level outcome;

ordered evaluated PredicateResult objects;

references to the condition trace and child traces;

concise rule-level evidence index/summary;

rule-level errors;

root rule trace identity.

No-duplication rule

Do not copy complete predicate evidence into RuleMatch.evidence, then copy it again into the rule trace. Preserve the authoritative typed object once and link to it through stable IDs or trace references. A concise human- or machine-readable summary is allowed only when it adds rule-level meaning and remains traceable to its source facts.

Compatibility serializers may duplicate fields only when necessary to preserve an approved existing public shape. Such duplication must exist at the serializer boundary, not in the universal internal model, and must be covered by exact compatibility tests.

12. Determinism and serialization

Provide one canonical serializer for RuleMatch and its supporting models.

Requirements:

deterministic field order;

canonical enum values exactly as defined in Section 10;

immutable tuples serialized as JSON arrays;

mapping keys sorted lexicographically by the shared canonical serializer;

domains canonicalized, de-duplicated, and sorted deterministically;

predicate_results preserved in actual condition evaluation order;

trace_references ordered by order, with stable tie-breaking by type and trace ID;

errors preserved in deterministic detection/evaluation order with stable tie-breaking where necessary;

JSON-safe recursive normalization;

finite numeric values only; reject NaN and infinity;

normalize negative zero according to the project’s existing numeric serializer;

empty mappings serialize as {} and empty sequences as [], never null;

no memory addresses, unordered sets, object repr, system-clock reads, random identifiers, filesystem paths, or platform-dependent values in logical output;

repeated serialization of logically identical RuleMatch objects produces byte-identical normalized JSON;

cached versus uncached predicate execution must not alter the logical RuleMatch after existing Prompt-01 runtime-only fields are normalized according to its contract;

Windows Python 3.11 and Python 3.14 must produce identical normalized logical output for the same inputs and versions.

RuleMatch ordering in a returned collection must be:

priority descending;

rule ID ascending;

rule version ascending;

stable evaluation-plan position as the final tie-breaker.

This ordering affects output and traces only; it must not change rule-evaluation semantics.

13. Validation and invariants

Validate at construction and, where appropriate, during rule loading:

every required string identity/version field is nonempty;

rule_id is canonical and valid under the existing loader contract;

domains is immutable, canonical, unique, and deterministic;

status and matched satisfy the invariant in Section 10;

base_weight and quality, when present, are finite;

base_weight and priority satisfy existing rule-schema limits without changing those limits;

quality, when non-null, satisfies the existing accepted range;

matched and unmatched results have a condition trace when condition evaluation occurred;

missing capability, invalid, and error outcomes contain sufficient typed error or trace evidence to explain why truth was not determined;

predicate results are immutable PredicateResult instances;

rule-level errors do not silently replace predicate errors;

provenance and metadata are immutable and JSON-safe;

trace identities are stable and references resolve within the run’s trace bundle;

no rule-level field contains adjusted weight, contribution, final score, confidence, conflict result, or narrative;

no raw Surya Siddhānta JSON, request payload, mutable AstroState reference, or sensitive birth input is embedded merely for convenience.

Invalid construction must fail through a typed deterministic error. Do not create partially valid RuleMatch dictionaries.

14. Generic Rule Engine construction rules

The generic Rule Engine must:

receive a validated declarative rule, immutable evaluation snapshot/context, and typed condition-evaluation result;

read identity, version, scope, category, priority, base weight, context, quality, provenance, and metadata from the resolved rule contract;

map the condition outcome to RuleMatchStatus without collapsing unavailable or failed results into unmatched;

preserve evaluated PredicateResult objects in deterministic order;

create concise rule-level evidence and stable trace references;

create the root trace_id through the existing deterministic trace mechanism;

construct and validate RuleMatch through one engine-owned factory/builder boundary;

return universal RuleMatch internally before any Yoga, Career, or public compatibility projection;

normalize collections of matches using Section 12 ordering;

preserve existing strict failures for invalid production rules.

The generic Rule Engine must not:

call predicates outside the typed Prompt-01 evaluator contract;

return raw (bool, evidence) tuples or untyped match dictionaries;

calculate adjusted weight or score contribution;

compute confidence or resolve conflicts;

generate public narrative;

change rule conditions, weights, priorities, or astrological semantics;

access raw Surya JSON;

mutate AstroState, rule definitions, PredicateResult, or cached data.

15. Yoga migration requirements

During repository discovery, identify the actual active Yoga rule-evaluation and serialization seams.

Migration requirements:

Yoga rule conditions continue to use the generic condition evaluator;

the generic Rule Engine constructs universal RuleMatch before Yoga-specific handling;

Yoga may return RuleMatch[] internally or use a typed Yoga wrapper that contains one RuleMatch without duplicating its identity, evidence, provenance, weight, or trace fields;

current Yoga detection semantics, rule order, strength behavior, public compatibility shape, and snapshots remain unchanged;

no Yoga code may reconstruct rule-match dictionaries from predicate booleans;

no fallback Yoga evaluator may bypass PredicateResult or universal RuleMatch;

matched, unmatched, missing-capability, skipped, and error outcomes remain distinguishable internally;

positive and negative existing Yoga fixtures must retain their prior logical results and approved serialized projections.

Do not redesign YogaDiagnostic; that belongs to later typed-domain work unless a narrow wrapper already exists and only needs to hold universal RuleMatch.

16. Career migration and compatibility

During repository discovery, identify the actual Career rule-evaluation, scoring-input, evidence, and serialization seams.

Migration requirements:

Career consumes universal RuleMatch or a narrow compatibility projection derived from it;

existing Career score, confidence, evidence, labels, narrative, and ordering remain behaviorally identical;

no scoring or confidence formula moves into RuleMatch or the generic Rule Engine;

the existing temporary Prompt-01 Career bridge may be narrowed or adapted, but Prompt-02 must not redesign the Career interpreter;

multi-domain rule scope remains complete in the universal model even if the Career projection selects the Career view;

errors and missing capabilities must not be silently presented as ordinary negative Career evidence;

MVP-01 Career public JSON and deterministic download remain unchanged;

approved Career and end-to-end snapshots remain byte-identical unless an unavoidable public-contract migration is discovered.

If universal RuleMatch cannot be introduced without changing the Career score, confidence, or public response schema, stop before making that change and report the exact blocker and proposed migration for approval.

17. Public API and snapshot compatibility boundaries

Prompt-02 is an internal contract migration. Preserve existing public APIs and JSON.

Allowed compatibility mechanism:

Universal RuleMatch
  -> narrow explicit compatibility serializer/projection
  -> unchanged existing Yoga/Career/public shape

Not allowed:

Legacy dictionary/tuple
  -> treated as internal source of truth
  -> universal RuleMatch reconstructed later

Every compatibility adapter must:

have an explicit name and one documented owner;

accept universal typed input;

be located at the narrowest consumer or serializer boundary;

preserve exact current behavior;

be covered by compatibility tests;

contain no astrology, scoring, or confidence logic;

not be used by new internal callers;

be listed in the completion report.

Do not update an approved snapshot merely because the new internal model serializes differently. If a public snapshot would have to change, stop and request approval with a human-readable before/after diff, schema impact, consumer impact, and migration rationale.

18. Error and missing-capability behavior

Required distinctions:

condition evaluated false -> UNMATCHED;

required capability unavailable -> MISSING_CAPABILITY;

rule not evaluated under explicit policy -> SKIPPED or EXCLUDED according to Section 10;

malformed rule metadata or resolved input -> typed validation failure and, only where an existing diagnostic path permits, INVALID;

expected evaluation failure -> ERROR with typed recoverable details;

unexpected programming defect -> remains visible in strict development/test execution and must not be swallowed into a generic nonmatch.

The Rule Engine applies the existing explicit rule-level failure policy. Prompt-02 may map current policy outcomes into the new status model but must not invent Prompt-06 governance or Prompt-07 DSL semantics.

Do not expose raw stack traces, secrets, full birth inputs, or unstable exception representations in RuleMatch. Secure internal logs may retain diagnostic details under existing policy.

19. Required repository discovery before modification

Before creating or modifying implementation files, inspect and report:

current branch, local HEAD, remote main, and tracked worktree status;

presence and status of the four protected untracked personal JSON files;

current full validation commands for Windows Python 3.11 and 3.14;

protected-artifact manifest and approved-snapshot verification mechanism;

all rule model/result classes and untyped rule-match dictionaries;

generic Rule Engine entry points and construction paths;

rule loaders, metadata schemas, serializers, and ordering logic;

typed Prompt-01 condition-result contract and how it exposes skipped branches and trace IDs;

all active callers of rule evaluation;

Yoga evaluation, wrapper, evidence, and serialization seams;

Career evaluation, scoring-input, evidence, and serialization seams;

diagnostic versus normal rule-evaluation modes;

all code that reads weight, priority, domain/domains, provenance, trace, or rule status from existing match objects;

all tests and snapshots that lock Yoga, Career, rule-engine, or MVP-01 behavior;

all remaining legacy or compatibility projections relevant to rule matches;

likely breaking changes and the narrowest compatible migration plan.

Search the repository broadly; do not assume filenames from the architecture documents. Report the inventory before implementation. Do not create an audit series or multiple planning work packages.

20. Implementation safety and sequence

Follow this sequence:

On Windows, switch to main using non-destructive Git commands, fetch normally, and verify that local and remote main are synchronized.

Verify the exact starting commit is 2c8d5ce6e86cb8a747e3f0b634116deb7083256c. If it differs, stop and report before creating a branch.

Verify the tracked worktree is clean. The four listed untracked JSON files are permitted but must remain untouched. Any other unexpected change must be reported.

Record hashes or equivalent non-mutating identity evidence for the four personal JSON files, protected artifacts, and approved snapshots.

Establish and report the current baseline in both supported Python lanes and the frontend/public compatibility checks relevant to MVP-01. Do not assume historical counts.

Perform the repository discovery in Section 19 and present the bounded migration plan.

Create one Prompt-02 branch only after the starting-state checks pass. Use a clear Prompt-based name such as agent/parasara-prompt02-rulematch; do not use Stage numbering.

Add supporting status/error/trace-reference models and universal immutable RuleMatch using existing project conventions.

Add canonical construction, validation, deterministic serialization, and collection ordering inside the generic Rule Engine boundary.

Migrate the discovered Yoga seam with the narrowest compatible wrapper or projection.

Migrate the discovered Career seam while locking score, confidence, evidence, and public JSON behavior.

Remove or prohibit active untyped rule-match dictionaries after all active callers use the universal contract. Retain only explicitly justified serializer-boundary projections.

Add and run focused tests, then full regression in Python 3.11 and 3.14, plus existing frontend/public compatibility validation.

Verify the four personal files, all protected artifacts, approved snapshots, and deterministic output are unchanged.

Update only required Prompt-02 documentation and completion records.

Produce the final report in Section 26 and stop for review.

Do not commit, push, open a pull request, merge, or publish during this implementation session. Implement and validate first, then stop for review. Never use destructive Git commands, broad cleanup commands, force operations, or snapshot-update modes.

21. Required tests

Add the smallest focused suite that proves the contract and migration. Reuse existing fixtures where practical.

Unit tests

valid matched construction;

valid unmatched construction;

every non-success status;

status/matched invariant enforcement;

required identity and version validation;

deterministic multi-domain canonicalization;

immutable fields and defensive freezing of nested mappings;

finite base_weight and optional quality validation;

empty evidence/errors/trace references normalization;

rule-level error construction and source references;

rejection of score, adjusted-weight, confidence, contribution, and mutable payload leakage where enforceable;

deterministic trace identity/factory behavior.

Serialization tests

deterministic field and mapping order;

repeated byte-identical normalized serialization;

serialization round trip;

stable enum values;

tuple-to-array behavior;

nested JSON normalization;

no NaN, infinity, Python repr, random ID, or platform-specific value;

equivalent normalized output under Python 3.11 and 3.14;

matched and unmatched diagnostic serialization.

Generic Rule Engine tests

only the generic Rule Engine constructs active universal matches;

matched condition -> MATCHED;

false condition -> UNMATCHED;

missing capability -> MISSING_CAPABILITY;

invalid metadata/input -> strict rejection or existing diagnostic INVALID behavior;

expected evaluation failure -> ERROR;

skipped/excluded policy mapping;

predicate results preserved in evaluation order;

short-circuited branches represented through condition trace rather than fake predicate results;

identity, rule-set version, domains, base weight, priority, context, quality, provenance, and metadata propagated without alteration;

collection ordering by priority and identity;

no adjusted weight or inference calculation.

Yoga integration tests

existing matching Yoga remains matched;

existing nonmatching Yoga remains unmatched;

evidence and trace lineage survive migration;

Yoga receives or wraps universal RuleMatch;

no active Yoga code reconstructs untyped rule-match dictionaries from predicate booleans;

current Yoga public/snapshot projection remains exact.

Career and MVP-01 compatibility tests

existing representative Career score is unchanged;

existing confidence is unchanged;

evidence content and deterministic ordering are unchanged;

missing-capability/error behavior is not converted to negative evidence;

Career consumes universal RuleMatch or a narrow typed projection;

MVP-01 public JSON and deterministic download remain unchanged;

frontend production build and existing user-journey validation pass.

Architecture tests

no active predicate imports or constructs RuleMatch;

no domain/Yoga consumer constructs universal matches directly;

no active generic Rule Engine path returns raw rule-match tuple/dictionary contracts;

no adjusted_weight, contribution, score, confidence, or conflict calculation exists in RuleMatch or its factory;

no Prompt-04 through Prompt-08 scope is introduced;

no raw Surya JSON access is added;

compatibility adapters flow from universal model to legacy/public projection, never the reverse;

deterministic domains is plural and cannot be silently narrowed internally.

Determinism and regression tests

repeated cold and warm evaluation produces identical normalized logical RuleMatch output;

shuffled loader input produces the same normalized returned ordering where rule semantics allow;

Python 3.11 and 3.14 normalized hashes match;

full existing backend suite passes in both lanes;

existing frontend build and relevant integration suite pass;

approved snapshots remain byte-identical;

protected artifacts and personal exports remain unchanged.

Do not weaken, delete, broadly skip, or replace valid existing assertions merely to pass the migration.

22. Required validation

Validation must run on Windows in both supported lanes:

Python 3.11 baseline lane;

Python 3.14 forward lane.

Before implementation, discover and run the repository’s current authoritative baseline commands. After implementation, run:

focused Prompt-02 model and Rule Engine tests;

focused Yoga and Career compatibility tests;

architecture enforcement tests;

deterministic serialization and repeated-run tests;

full backend regression under Python 3.11;

full backend regression under Python 3.14;

existing approved-snapshot comparison without update mode;

protected-artifact and worktree checks;

existing frontend production build and relevant MVP-01 integration checks.

Report exact commands, interpreter versions, pass/fail/skip counts, hashes where applicable, and any environmental limitation. Do not report “all tests passed” without evidence. Do not substitute Linux results for required Windows validation.

23. Protected-artifact and snapshot safeguards

Discover the authoritative protected-artifact list from the repository; do not rely only on a historical count.

Record the pre-change and post-change identity of every protected artifact.

Use approved snapshot comparison only; never enable update/approve mode.

Do not modify golden inputs, golden outputs, public snapshots, or protected manifests to accommodate the new internal contract.

Do not touch, stage, delete, rename, reformat, or regenerate Manohar-try1.json through Manohar-try4.json.

Do not use broad cleanup, reset, checkout, restore, or deletion commands that could affect untracked or user-owned files.

If a protected artifact or approved snapshot changes, stop, restore nothing destructively, and report the exact diff and cause for review.

24. Documentation requirements

Update or create only the documentation needed for Prompt-02:

RuleMatch model reference;

status/outcome semantics;

evidence and trace ownership diagram or concise description;

generic Rule Engine construction contract;

rule-author metadata requirements relevant to propagation;

Yoga and Career compatibility projection notes;

error-code/status catalog additions;

deterministic serialization and ordering contract;

migration inventory and remaining compatibility adapters;

completion matrix/status record using truthful validation vocabulary.

Do not rewrite the Master Architecture, renumber Prompts, introduce Stage numbering, or claim Prompt-03/production readiness.

25. Acceptance criteria

Prompt-02 implementation is acceptable only when every item below passes:

one immutable typed universal RuleMatch exists;

RuleMatchStatus, rule-level errors, and trace references have explicit typed contracts;

only the generic Rule Engine constructs active universal RuleMatch objects;

predicates continue to return only PredicateResult;

typed condition results remain the owner of logical composition and skipped branches;

rule identity, versions, system, family, category, plural domains, context, priority, base weight, quality, provenance, metadata, predicate results, and trace lineage are preserved;

base_weight is declared metadata only;

no adjusted weight, contribution, aggregation, score, confidence, or conflict resolution is implemented;

matched, unmatched, skipped, excluded, missing capability, invalid, and error outcomes remain distinguishable;

missing capability and failures are never silently converted to unmatched;

rule evidence remains complete and traceable without unnecessary duplication;

deterministic ordering and byte-stable normalized serialization pass;

active Yoga and Career paths consume or narrowly wrap universal RuleMatch;

active untyped rule-match dictionaries are zero, except explicitly listed serializer-boundary projections that are not internal contracts;

Yoga semantics and outputs are preserved;

Career score, confidence, evidence, and public behavior are preserved;

MVP-01 public JSON, deterministic download, approved snapshots, and frontend behavior are unchanged;

current full regression passes on Windows Python 3.11 and 3.14;

protected artifacts and the four personal JSON files are unchanged;

required documentation and completion records are updated;

no Prompt-03 through Prompt-08 or unrelated product scope has been introduced;

no commit, push, PR, merge, or publication has occurred before review.

Do not declare completion if an active consumer still treats an untyped dictionary or tuple as the primary rule-match contract.

26. Implementation stopping point and final report

After implementation and validation, stop before committing. Provide one concise evidence-backed report with exactly these sections:

Prompt
------
Prompt-02 — RuleMatch

Starting State
--------------
Branch:
Local HEAD:
Remote main:
Tracked worktree:
Protected untracked files:

Baseline
--------
Python 3.11 command and result:
Python 3.14 command and result:
Frontend/public compatibility result:
Approved snapshot identity:
Protected-artifact result:

Repository Discovery
--------------------
Generic Rule Engine construction paths before:
Existing rule-match models/dictionaries before:
Yoga migration seam:
Career migration seam:
Public compatibility seams:
Likely breaking changes identified:

Implementation Status
---------------------
Implemented / Blocked

Architecture Changes
--------------------
Expected Prompt-02 contract changes only / list deviation

Files Added
-----------

Files Modified
--------------

Universal Contract
------------------
RuleMatch model:
Status model:
Evidence ownership:
Trace ownership:
Deterministic ordering:

Migration Results
-----------------
Active untyped rule-match contracts before:
Active untyped rule-match contracts after:
Yoga result:
Career result:
Compatibility adapters remaining:

Prompt-03 Boundary Verification
-------------------------------
Adjusted weight added: NO
Score/inference added: NO
Confidence added: NO
Conflict resolution added: NO

Tests Added
-----------

Validation Evidence
-------------------
Focused tests:
Python 3.11 full result:
Python 3.14 full result:
Frontend/public compatibility result:
Determinism result and hashes:
Approved snapshot comparison:
Protected-artifact comparison:
Personal JSON comparison:

Public Behavior
---------------
MVP-01 behavior unchanged: YES / NO
Public schema changed: NO, or STOPPED FOR REVIEW

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

Ready for Prompt-03
-------------------
YES / NO — architectural handoff only; Prompt-03 not started

Recommended Next Action
-----------------------
Review Prompt-02 implementation and validation before authorizing commit/push/PR.

Do not commit merely because acceptance criteria pass. Wait for explicit review and authorization.

27. Handoff boundary to Prompt-03

Prompt-02 ends when the Rule Engine produces a deterministic ordered collection of universal RuleMatch objects and existing consumers use that contract without changing public behavior.

The Prompt-03 input boundary is:

RuleMatch[]
  - factual PredicateResults preserved
  - declared base weights preserved
  - priorities preserved
  - multi-domain scope preserved
  - contexts and provenance preserved
  - statuses, evidence, errors, and traces preserved

Prompt-03 alone will define and implement:

contribution signs and typed contribution objects;

adjusted weights and context multipliers;

quality/evidence/priority multipliers used during combination;

positive, negative, neutral, and mixed aggregation;

score normalization;

confidence calculation;

duplicate-evidence/correlation handling during inference;

conflict detection and deterministic resolution;

inference-level explanations and InferenceResult.

Prompt-02 must not anticipate those policies in fields, helper methods, adapters, or consumer logic. When Prompt-02 passes, stop. Do not begin Prompt-03.

Final instruction to VS Code Codex

Implement only Prompt-02 — RuleMatch under this specification and the governing Master Architecture.

Begin with the synchronized starting-state verification and repository discovery. Choose the narrowest compatible implementation based on actual repository contracts. Preserve astrological semantics, MVP-01 behavior, approved snapshots, protected artifacts, and the four personal validation exports. Do not use destructive Git operations. Do not implement inference or later Prompt scope.

Implement and validate fully, produce the required report, and stop before commit, push, pull request, merge, publication, or Prompt-03 work.