# Parāśara — Prompt-08 Dependency Graph Specification

> **Current Python policy - 2026-11-06:** [Root policy](../../../../../../AGENTS.md) selects Python 3.11.9 only
> for development, tests, and CI and explicitly supersedes every dual-version
> requirement below. Retained Python 3.14 results/commands are historical, not
> current instructions. Run appropriate checks once on the selected runtime;
> keep correctness, regression, end-to-end, and same-runtime determinism checks.
> Missing second-version evidence is never a defect or blocker. Future specs,
> prompts, and handoffs must carry this policy; only an explicit user request
> can reinstate multiple Python versions.

**Document version:** 1.0.0  
**Status:** Specification produced; user review pending; implementation not started  
**Date:** 2026-09-17  
**Author:** Codex, repository architecture session  
**Reviewer:** User approval pending; future implementation requires independent review  
**Baseline:** `main` at `ec6b49a164389aada4e741561d75cb866527e6cf`  
**Compatibility:** Accepted Prompts 01–07; Python 3.11 and 3.14; existing public compatibility profile unchanged

## 1. Decision and scope

Prompt-08 shall introduce one immutable, deterministic, version-authorized rule dependency graph and execution plan. `RuleGraphCompiler` owns graph construction, validation, canonical projections, and topological planning. `ResolvedEvaluationVersions` remains the sole runtime authorization authority. `RuleEngine` remains the sole rule execution and RuleMatch owner.

Dependency declarations live in exactly one separately versioned strict JSON graph artifact selected by the manifest. They do not enter DSL schema 1.0.0. The existing `RuleDslCompiler` first compiles the unchanged DSL document; the graph compiler binds those exact compiled rules to the dependency declarations. This is one staged compilation pipeline, not two competing rule compilers.

Edges have the master architecture's three kinds: `requires_matches`, `requires_absence`, and `optional_supports`. All impose predecessor completion order. The first two gate evaluation on factual rule outcomes. Optional support is a non-gating, trace-only relationship; it does not assign weight, confidence, truth, or evidence. Dependencies are never predicates, AstroState facts, or rule-result expression operators.

The implementation and its fixtures are synthetic infrastructure only. Current `parashara/v1`, Career, Yoga, dormant rules, astrology meaning, ordering, public serializers, and the approved snapshot remain unchanged. Production astrology migration belongs to FWP-03 with a new governed rule-set identity.

Normative MUST/SHALL statements are acceptance requirements. This document specifies future work; it authorizes no implementation in this session.

## 2. Governing sources and repository findings

### 2.1 Authority and classification

Reviewed governing sources:

- `Documentation/AI-Prompt/Jyothishyam Master Architecture Specification v1.0.docx`: especially §§25, 28–36, 103–109, 113–120, 144, 156, 225–230, 235, 240–244.
- `Documentation/AI-Prompt/Prompt-Plan.docx`: Prompt-08 is Dependency Graph; Prompt-09 is Architecture Verification; Prompt-10 is Production Readiness and Release Certification.
- `systems/Parasara/Documentation/Engine/Prompt-06/requirements/Prompt-06-Rule-Versioning.md`.
- `systems/Parasara/Documentation/Engine/Prompt-07/requirements/Prompt-07-Rule-DSL.md`.
- Current/target architecture navigation documents under `systems/Parasara/Documentation/architecture/`, implementation status/roadmap references, and graph/reference/cache searches across production, tests, and documentation.

The master explicitly defines rule nodes, three dependency kinds, deterministic topological sorting, and dependency skip traces (§§106–109). An ordering-only graph would not fulfill that contract. Its suggested status names are represented through the accepted Prompt-02 statuses plus typed reasons; new RuleMatch enum values are unnecessary. Its recommended compiled-plan fields (§104) are supplied by references to existing compiled rules, predicate bindings, capabilities, macro traces, and the new plan. No duplicate AST, cost evaluator, or enrichment scheduler is created.

| Classification | Verified repository evidence | Prompt-08 consequence |
|---|---|---|
| Accepted implemented version authority | `engine/versioning.py`: `RuleVersionResolver`, `ResolvedEvaluationVersions.require_same`, source verification, compiled-rule issuance, lifecycle/replay | Extend its graph slot; never select versions in the graph compiler |
| Accepted DSL compiler | `rules/dsl/{models,parser,compiler}.py`: schema 1.0.0, one DSL source, maximum 256 rules, sealed compiled artifacts, instance-local LRU | Consume its exact objects; preserve its source, component fingerprint, and existing digests |
| Accepted rule execution | `rules/rule_engine.py`: `ResolvedRule`, `evaluate_compiled_rule`, private `_build_match`, `order_matches` | Add a graph-plan entry point and graph-only bypass guard here |
| Accepted factual contracts | `rules/models.py`, `conditions.py`, `definition_validation.py` | Reuse PredicateStatus, ConditionResult, existing validation and short circuit behavior |
| Accepted RuleMatch | `rules/rule_match.py`: SKIPPED, typed errors, open string-valued trace references | Represent dependency skip in existing contract without editing this module |
| Accepted inference | `inference/engine.py` and Prompt-03 specification | Owns all aggregation and scoring; graph does not manufacture inference evidence |
| Existing caches | PredicateEvaluator LRU and RuleDslCompiler LRU | Add only a bounded instance-local graph-plan cache |
| Existing unrelated graphs | Aspect relationships/enrichments | Factual relationships are not execution graph nodes |
| Dormant/historical material | Legacy macros placeholder, dormant primitive/derived seeds, old work-package exclusions, shadowed `rajayoga_naive` seed | No activation, migration, or inferred dependencies |
| Future architecture | Rule-result expressions, plugin loading, enrichment scheduling, result/inference caches, incremental evaluation | Not implemented or implied by this stage |

Required source review also covered `tests/versioning/`, `tests/dsl/`, `tools/validate_prompt06.py`, and `tools/validate_prompt07.py`, including authority replacement, all seven runtime statuses, component content/limit fingerprints, cache reauthorization, scenario manifests, lifecycle, replay, and scope tests.

No dependency graph compiler, execution planner, graph fixtures, or graph tests existed at session start. A mention of `dependency_graph` in versioning is an intentionally disabled extension point, not an implementation. Macro recursion checks concern one DSL document and are not cross-rule graph planning.

### 2.2 Predecessor extension, not predecessor redesign

Prompt-06 created `future_components.dependency_graph`; Prompt-07 §18 expressly reserves separately versioned dependencies for Prompt-08. The future changes here activate that seam. No PredicateResult, ConditionResult, RuleMatch, DSL semantic-contract, inference, domain, or public serialization contract changes are required.

Stage-local “Prompt-08 absent” tests and validator guards must be advanced explicitly to “graph opt-in only, DSL unchanged, current v1 graph absent.” The exact files are listed in §16. These historical scope assertions are not perpetual bans on the approved next stage. Historical specifications remain untouched.

The current DSL equality `RuleRevisionIdentity.semantic_content_sha256 == CompiledRule.compiled_semantic_sha256` remains exact. Graph-enabled execution has a distinct composed semantic identity defined in §8; it does not overwrite or reinterpret the DSL digest. This avoids a circular manifest digest and preserves Prompt-07 authorizations.

If implementation needs a predecessor contract change beyond these named extension points, it MUST stop and request approval. No such conflict was found in this specification review.

## 3. Ownership and types

| Concern | Single owner | Excluded responsibility |
|---|---|---|
| Dependency authoring | Governed graph artifact selected by rule-pack manifest | No hidden derivation from labels, predicate calls, file names, or astrology facts |
| DSL parsing, macros, binding, lowering, DSL semantic identity | Existing RuleDslCompiler | Does not parse graph JSON or execute dependencies |
| Dependency parsing, graph validation, identity, planning | New RuleGraphCompiler in `rules/graph/compiler.py` using its parser/models | Does not evaluate conditions, produce RuleMatch, score, or select a manifest |
| Component/source/rule/graph/plan runtime authorization | Existing ResolvedEvaluationVersions, issued by RuleVersionResolver | Does not implement an alternative graph algorithm |
| Dependency gate interpretation, sequential execution, dependency traces, RuleMatch production | Existing RuleEngine | Does not invent factual truth or score |
| Condition truth and predicate outcomes | Existing ConditionEvaluator / PredicateEvaluator | No dependency lookup or calls to other rules |
| Inference contributions, evidence policy, scores/confidence | Existing InferenceEngine | Graph does not change its eligibility or weighting policy |

New immutable diagnostic/model types are `RuleNodeKey`, `DependencyKind`, `DependencyDeclaration`, `GraphDiagnostic`, `GraphAnalysis`, `ValidatedRuleGraph`, `RuleExecutionPlan`, `DependencyDecision`, `RuleExecutionTrace`, `GraphEvaluationRecord`, and typed success/failure outcomes. Their role is graph configuration, plan, or audit envelope, never a replacement rule result.

Only rule nodes exist. Predicate, condition, macro, AstroState, capability, enrichment, timing, domain, plugin, and generic task nodes are forbidden. Existing capabilities remain input requirements checked by factual evaluation.

## 4. Exact authoring contract

### 4.1 One strict graph JSON artifact

The manifest selects one UTF-8 `.json` graph artifact. There is no inline DSL dependency field, YAML alternative, automatic sidecar search, external include, wildcard, expression, implicit “latest,” or per-rule graph file.

Exact schema, illustrated with two synthetic rules:

```json
{
  "graph_schema_version": "1.0.0",
  "system": "synthetic",
  "rule_set_family": "prompt08_fixture",
  "rule_set_version": "fixture-v1",
  "rules": [
    {
      "rule_id": "synthetic.a",
      "revision": "1.0.0",
      "requires_matches": [],
      "requires_absence": [],
      "optional_supports": []
    },
    {
      "rule_id": "synthetic.b",
      "revision": "1.0.0",
      "requires_matches": [
        {"rule_id": "synthetic.a", "revision": "1.0.0"}
      ],
      "requires_absence": [],
      "optional_supports": []
    }
  ]
}
```

All displayed fields are required, including empty arrays. No other fields are allowed at any depth. Null, Boolean, and numeric values are invalid in authoring: this schema uses only objects, arrays, and strings. Duplicate object keys fail at every depth, before any last-wins conversion. Reject BOM, malformed UTF-8, non-NFC strings, unpaired surrogates, trailing documents/content, comments, NaN/Infinity, and unsupported schema versions. Alternate JSON whitespace and escape spelling for the same allowed string are non-semantic.

System/family/set version must exactly equal the selected DSL document and manifest. Identity strings use the existing versioning safe identity grammar, maximum 128 characters; rule IDs use the concrete Prompt-02 grammar `^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$`; revisions use Prompt-07 SemVer grammar. No templates/materialization are supported. Source IDs use repository-relative POSIX paths, maximum 256 characters, with no empty, dot, traversal, absolute, drive, UNC, backslash, URL, or expansion segments. The authority resolves the real path under its explicit root, rejects escape through links, and never uses CWD.

The `rules` array must cover every compiled manifest member exactly once and no others. One concrete revision per rule ID is allowed in a graph pack; two revisions of one ID in one pack are rejected as ambiguous, even though different packs may coexist. Root nodes have three empty arrays. Authoring row order is non-semantic: canonical node order always comes from manifest source position. Dependency list order is non-semantic and canonicalized after duplicate detection.

Empty graph: rejected, because the accepted DSL requires a nonempty compiled rule set. A nonempty graph with zero edges is valid and still requires the plan entry point. No compatibility claim for empty DSL documents is introduced.

### 4.2 Edge identity and policy

For an entry in dependent B's `requires_matches` list referencing A, the edge is **A → B**. The same direction applies to all kinds. Canonical edge identity is `(prerequisite source_order, dependent source_order, kind)`.

Each prerequisite/dependent pair may occur at most once across all three lists. Repeated same-kind edges fail `DUPLICATE_DEPENDENCY`; assigning two kinds to the same pair fails `CONFLICTING_DEPENDENCY`. Do not deduplicate silently. Self references fail `SELF_DEPENDENCY` before topological analysis.

Unknown ID, known ID with wrong revision, document set/version mismatch, and unauthorized membership are separate diagnostics. A reference has no system/family/version override; those qualifiers are inherited from the document. A foreign fully qualified reference is an unknown field or unknown ID, never an import. Cross-system, cross-rule-set, cross-version, excluded/dormant-rule, and unavailable-plugin references are forbidden.

Cross-domain edges are prohibited in graph schema 1.0.0: both nodes must have identical canonical `ResolvedRule.domains` tuples. Equal empty tuples are allowed only when existing domain-neutral validation permits them. There is no “allowed cross-domain” metadata in this schema. A future explicit cross-domain contract needs separate approval; master §108 does not require enabling it now.

“Optional” means the prerequisite's terminal outcome does not gate the dependent. It does not mean an optional/missing node. Optional-support edges still require authorized membership, impose ordering, count toward limits, and participate in cycle detection.

Changing a dependency ID, revision, kind, or presence is executable semantic change. It requires a new rule-set version and a new revision of each dependent whose declaration changes. No mutation under an old identity is authorized. The base DSL revision label must reflect that revision too, even if its condition remains identical.

## 5. Immutable node identity and membership

A node refers to one exact `CompiledRule` already authorized by Prompt-06. Its immutable `RuleNodeKey` projection contains exactly:

```text
system
rule_set_family
rule_set_version
rule_id
revision
dsl_compiled_semantic_sha256
source_artifact_id
source_identity
source_artifact_semantic_sha256
source_order
```

System/family/version come from the compiled set and manifest, not `ResolvedRule.rule_family` (which is rule metadata, not necessarily the rule-set family). The last four fields are the manifest-selected DSL artifact ID/path/canonical DSL digest and zero-based rule position. Source order must be unique, contiguous 0..N-1 and equal to `ResolvedRule.evaluation_plan_position`. Membership must be an exact bijection among manifest rules, compiled rules, and graph rows.

The selected manifest fingerprint and exact authority object bind the containing plan at issuance/runtime. The fingerprint is deliberately excluded from node/graph/plan semantic projections because the manifest itself pins graph/plan digests. Including it would create an impossible hash cycle. Nodes cannot acquire authority outside their sealed containing graph.

There is no generated UUID, user node alias, second mutable node ID, or priority-derived identity. Edges store source-position references to the authoritative node table rather than copies of all node fields. DSL AST, lowered conditions, metadata, capabilities, and predicate bindings remain on the referenced compiled objects.

## 6. Runtime semantics and evidence boundary

### 6.1 Scheduling versus dependency satisfaction

A node becomes scheduling-eligible after every incoming edge's prerequisite has reached a terminal rule outcome. The deterministic plan ensures this without dynamic scheduling. Eligibility does not imply dependency satisfaction, condition truth, a matched RuleMatch, or inference eligibility.

For required edges, evaluate every incoming decision in canonical edge order; do not short circuit diagnostic collection. All required edges must be satisfied before evaluating the dependent's own condition. Optional edges never affect that Boolean gate. Even if all required edges pass, the dependent's condition can be unmatched, unavailable, invalid, errored, timed out, or skipped.

| Prerequisite root outcome | Existing prerequisite RuleMatch status | requires_matches | requires_absence | optional_supports |
|---|---|---|---|---|
| matched | MATCHED | satisfied | unsatisfied | observed_matched; gate ignored |
| unmatched | UNMATCHED | unsatisfied | satisfied | observed_unmatched; gate ignored |
| missing_capability | MISSING_CAPABILITY | unavailable | unavailable | observed_unavailable; gate ignored |
| invalid_parameters | INVALID | unavailable | unavailable | observed_unavailable; gate ignored |
| error | ERROR | unavailable | unavailable | observed_unavailable; gate ignored |
| timeout | ERROR, with existing condition_timeout provenance | unavailable | unavailable | observed_unavailable; gate ignored |
| skipped | SKIPPED | unavailable | unavailable | observed_unavailable; gate ignored |

The RuleEngine records the actual condition-root `PredicateStatus` while evaluating; it MUST NOT attempt to recover timeout versus error by reading RuleMatch.status alone. A dependency-gated skip has `root_outcome = null`, `completion_kind = dependency_skip`, and RuleMatch.SKIPPED. A condition-returned skip has `root_outcome = skipped`, `completion_kind = condition_evaluated`. Both are unavailable to subsequent required edges, but their provenance stays distinct.

`requires_absence` means a prerequisite was evaluated and factually unmatched. Missing capability, failure, timeout, and skip never prove absence. Optional supports records an observation only; no supporting contribution or extra evidence is emitted.

Governance exclusion is handled before compilation by manifest membership. EXCLUDED is not a valid completed node in this closed plan. Encountering an excluded/unknown/nonterminal runtime outcome is an invariant failure, not a false result or satisfied absence edge.

### 6.2 Dependent result and trace

If any required edge is unavailable, the dependent is SKIPPED with `skip_reason = dependency_unavailable`. Otherwise if any is unsatisfied it is SKIPPED with `skip_reason = dependency_unsatisfied`. Unavailability takes precedence, while all decisions are retained. The condition evaluator is not called, predicate_results is empty, condition_trace_id is null, and evidence is the empty mapping. No synthetic PredicateResult or ConditionResult is fabricated.

RuleEngine uses its private existing match-construction path with `status_override=RuleMatchStatus.SKIPPED` and a `RuleTraceReference(trace_type="dependency", relation="dependency_gate", ...)` pointing to its typed `RuleExecutionTrace`. This is an existing trace extension point. A skip is not recorded as a predicate error.

Each DependencyDecision has exact prerequisite/dependent source positions, kind, prerequisite rule trace ID, prerequisite completion_kind, root_outcome (nullable), RuleMatch status, and the decision vocabulary in the table. Each RuleExecutionTrace contains plan digest, node source position, execution ordinal, ordered decisions, `gate = passed|unsatisfied|unavailable`, `condition_evaluated` Boolean, completion_kind, root_outcome, and nullable skip_reason. RuleEngine owns these observations; the compiler produces no runtime trace.

The dependency trace ID is `"graph." + SHA256(canonical_json_bytes({"contract":"rule-dependency-trace@1.0.0","plan_sha256":P,"source_order":i,"snapshot_sha256":S,"context_sha256":C}))`. It does not contain its own ID or the dependent RuleMatch ID. The RuleMatch uses this as an additional reference and includes P and i in its existing deterministic trace-components seed. Prerequisite trace IDs refer only backward in the DAG. Trace references and dependency decisions are not inserted into factual evidence.

For a node that evaluates, RuleEngine calls the same private condition-execution helper used by its public DSL entry point. All existing status mappings, condition short circuit behavior, evidence construction, errors, and timeout translation remain intact. The only additional data is the internal dependency trace reference.

Inference consumes the completed ordinary RuleMatches through its existing API and policy. Skipped/unavailable nodes do not become negative contributions. A matched dependent derives its factual evidence exclusively from its own condition; dependency traces describe eligibility and lineage. The graph never imports predecessor evidence into that condition or supplies an inference multiplier. Optional support is deliberately not a scoring mechanism.

### 6.3 Failure atomicity

Ordinary typed predicate failures complete a node; disconnected rules and optional dependents can still evaluate. Required dependents skip under the table. This produces a complete ledger of all nodes, including typed non-factual results.

Authority, source/component, graph/plan digest, membership, structural-limit, or runtime invariant failures abort the whole graph evaluation. No generator, callback, partial match sequence, or partial authoritative record is returned. Internal matches accumulated before the failure are discarded. Unexpected programming exceptions propagate; they are not broadly caught and converted to nonmatches.

## 7. Deterministic construction, planning, and cycles

1. Check source path, byte and lexical nesting budgets before JSON object construction. Parse strict JSON and validate exact schema.
2. Validate the document selector and obtain the complete Prompt-07 analyzed/compiled inventory. Verify manifest membership and source positions.
3. Traverse nodes by ascending source_order. Within a node, process kinds in the fixed order requires_matches, requires_absence, optional_supports. Sort valid references by prerequisite source_order. Invalid references sort by ASCII rule_id/revision before diagnosis.
4. Reject unknown/revision-mismatched/duplicate/self/cross-domain references before cycle analysis. Create the immutable node table and edge tuple sorted by `(prerequisite position, dependent position, kind ordinal)`.
5. Use Kahn's algorithm with a min-priority queue keyed by source_order. Populate roots sorted by source_order. At each step remove the smallest ready node, append it once, process outgoing edges in canonical edge order, and enqueue a dependent as soon as its indegree becomes zero. Rule priority never breaks ties.
6. Disconnected components, multiple roots, and multiple leaves participate in the same queue; do not concatenate independently sorted components.
7. If emitted count is less than N, diagnose cyclic strongly connected components using iterative traversal with nodes and adjacency sorted by source_order. Ignore noncyclic residual descendants. Emit one diagnostic per cyclic SCC ordered by its minimum member.
8. For each SCC, select its lowest-position node, run deterministic depth-first traversal of sorted in-component neighbors, marking visited nodes once and retaining parent links, until the first encountered edge returns to that start, and emit that closed witness (start repeated at end). Include sorted SCC members separately. Do not enumerate all cycles. Self cycles were already rejected.
9. For a DAG, compute depth as 1 for roots and `1 + max(prerequisite depth)` otherwise, in topological order, including optional edges. Reject maximum depth >64.

No execution layers or parallel scheduling are exposed. Depth is a validated bound, not another execution order. The plan contains exactly one permutation of 0..N-1. Empty ready queue before all nodes are emitted is a cycle, never a reason to run residual rules in source order.

Example: source order A=0, B=1, C=2, D=3 with C→A and B→D yields execution [1,2,0,3]. After C completes, newly ready A precedes already-ready D. This distinguishes the contract from layer-by-layer sorting. With no edges, execution is source order.

Traversal uses integer positions and explicit sorting, never dict/set iteration, object addresses, filesystem order, locale collation, Python recursion limits, timing, or hash-seed behavior. IDs are ASCII; artifact paths are logical POSIX strings. Windows/Linux and Python 3.11/3.14 must produce identical canonical bytes for identical authorized semantic inputs.

## 8. Canonical projections and digests

### 8.1 One canonical encoder

Use existing `FrozenMapping`, `freeze_canonical`, and `canonical_json_bytes`: sorted mapping keys, compact JSON, strict UTF-8 without BOM/newline, validated NFC strings, preserved explicitly canonical array order. SHA means lowercase hex SHA-256 of those bytes. No float, duration, absolute path, object repr, seal, memory identity, cache statistics, or lifecycle state enters graph identities.

The following are exact projection definitions; short names D, N, E, G, P are notation, not extra mutable stored identity fields:

| Digest | Exact projection |
|---|---|
| raw source digest (audit only) | SHA-256 of exact graph source bytes |
| declaration digest D | `{"contract":"rule-dependency-declarations@1.0.0","document":normalized_document}`; document has exactly §4's fields, rows sorted by rule_id/revision, references sorted by rule_id/revision, kind fields fixed, all empty arrays retained |
| node projection digest N | `{"contract":"rule-dependency-nodes@1.0.0","nodes":[RuleNodeKey projections in source order]}` |
| edge projection digest E | `{"contract":"rule-dependency-edges@1.0.0","edges":[{"prerequisite":i,"dependent":j,"kind":k} in canonical edge order]}` |
| per-node composed execution semantic digest | `{"contract":"graph-bound-rule@1.0.0","node":RuleNodeKey,"dependencies":[{"prerequisite":RuleNodeKey,"kind":k} sorted by prerequisite position then kind]}` |
| graph digest G | `{"contract":"rule-dependency-graph@1.0.0","declarations_sha256":D,"nodes_sha256":N,"edges_sha256":E}` |
| plan digest P | `{"contract":"rule-execution-plan@1.0.0","graph_sha256":G,"dsl_compiled_rule_set_sha256":B,"graph_compiler_content_sha256":K,"graph_contract_sha256":H,"execution_order":[positions]}` |
| graph schema/compatibility digest H | SHA of GRAPH_CONTRACT_DATA described below |
| compiler component digest K | SHA of normalized implementation module digests plus GRAPH_CONTRACT_DATA, as below |

B is the existing Prompt-07 compiled rule-set digest. Full node/edge/graph projections are available for inspection; stored digests are validated derived properties, not caller-editable authority. No duplicate “graph ID,” “active graph version,” or alternative plan hash exists.

The per-node composed digest makes dependency semantics explicit without changing the Prompt-07 condition compilation contract. Base `compiled_semantic_sha256` still means exactly the existing DSL semantic_contract. For graph-enabled packs it is insufficient for execution by itself: the graph-bound digest and full plan are additionally required. Declarations are therefore part of executed rule semantics, while base DSL analysis remains reusable and byte-stable for unchanged DSL inputs.

Changing a node's declaration changes D, E, its composed identity, G, and P. Changing a prerequisite's compiled semantics changes N, its consumers' composed identities, G, and P. Changing source position or manifest membership changes N/E as applicable and G/P. Reordering graph JSON rows or dependency arrays changes only raw bytes; reordering DSL rules changes semantic positions and identities. Whitespace, line endings, JSON key order, equivalent escapes, cache warmth, process/CWD/platform, and lifecycle-only changes do not change D/N/E/G/P. A compiler implementation-only change changes K/P and the selected manifest even when G stays the same. Schema/outcome/planning/limit changes change H/K/P and need compatibility review.

The selected manifest includes G/P and is hashed last. Graph and plan projections never include the final manifest fingerprint, raw source bytes, or the graph component's enclosing artifact pins. There is no digest cycle.

### 8.2 Corrected component fingerprint contract

GRAPH_CONTRACT_DATA is a single immutable constant containing all of:

- graph schema, declaration/node/edge/graph/composed-rule/plan/trace contract identifiers above;
- compiler identity/version and compatibility string;
- exact JSON field schemas, identity grammars, path rules and strict parser policy;
- kind order, direction, duplicate/conflict policy, no-cross-system/set/domain policy, empty graph policy;
- the entire runtime outcome table and skip precedence;
- node/edge ordering, Kahn tie-breaking, SCC/witness algorithm and depth definition;
- diagnostic code/message table, stage order, sorting/truncation policy;
- every limit from §11, including parser, diagnostics, cache and trace bounds;
- canonical projection definitions and runtime result ordering contract.

The top-level GRAPH_CONTRACT_DATA keys are exactly `identity`, `version`, `compatibility_contract`, `contracts`, `authoring_schema`, `identity_grammars`, `path_policy`, `parser_policy`, `edge_policy`, `outcome_policy`, `planning_policy`, `diagnostics_policy`, `resource_limits`, `canonical_projections`, and `result_ordering`. Their values encode the corresponding normative tables and algorithms here; arrays use the explicit orders in this document. Tests lock the complete projection, not a handpicked subset. No second numeric limit table may drift from this constant. Runtime aliases read it.

The component helper accepts exactly these logical module IDs and supplied UTF-8 contents in this fixed order:

```text
graph/__init__.py
graph/models.py
graph/parser.py
graph/compiler.py
graph/runtime_contract.py
```

Normalize CRLF and bare CR to LF; preserve all other source content. In compiler.py only, require and replace the single literal line `GRAPH_COMPILER_CONTENT_SHA256 = "<64 lowercase hex>"` with `GRAPH_COMPILER_CONTENT_SHA256 = "<SELF>"` before hashing. Missing/multiple literals fail. Hash the canonical projection `{"compiler_contract":GRAPH_CONTRACT_DATA,"implementation_modules":[{"module_id":id,"content_sha256":sha(normalized_source)}]}`. The helper performs no filesystem lookup. Validator/tooling supplies the actual files and proves the published digest equals recomputation.

Changes to models, parser, planner, runtime contract data/helpers, or any locked limit change K; line-ending-only changes do not. RuleEngine/versioning integration remains owned by the existing engine component, with regression and same-authority checks; their entire source files are not smuggled into the DSL component. Graph runtime contract helpers are pure policy/projection utilities, never a second executor.

## 9. Manifest activation, authorization, and trust

### 9.1 Exact non-null graph component

Only future synthetic/new governed manifests may select:

```json
{
  "identity": "parashara-rule-graph-compiler",
  "version": "1.0.0",
  "compatibility_contract": "compiled-rule-set+rulematch-dependencies@1.0.0",
  "content_sha256": "<K>",
  "artifact_path": "synthetic/prompt08_fixture/fixture-v1/dependencies.json",
  "logical_sha256": "<G>",
  "metadata": {
    "graph_schema_version": "1.0.0",
    "graph_contract_sha256": "<H>",
    "declarations_sha256": "<D>",
    "plan_sha256": "<P>"
  }
}
```

These fields are exact; placeholders denote verified lowercase hashes, never accepted literal values. The manifest's existing `future_components.dsl` is mandatory and remains the supported Prompt-07 component, including its corrected content digest and exact metadata. Graph-without-DSL, mixed legacy/DSL graph membership, unsupported compiler/schema/contract, and a graph artifact under a null graph slot fail.

The graph source is selected solely through this component's `artifact_path`; it is not redundantly added as a rule source in `ordered_source_artifacts`. That existing list continues to authorize the one DSL source and its rule revisions. Source authority follows the existing ComponentIdentity artifact seam used by inference: the graph loader verifies the selected path, strict content D, reconstructed G/P, and component K/H. `logical_sha256` has the single meaning G. Do not duplicate it under metadata. Raw graph SHA is audit-only.

Current v1 remains byte-identical:

```json
"future_components": {
  "dsl": null,
  "dependency_graph": null
}
```

### 9.2 Compile/resolve sequence without circular authority

1. Build/test tooling uses RuleDslCompiler.analyze_source, then RuleGraphCompiler.analyze_source with that unsealed analysis and graph bytes. Analysis outputs are diagnostic values only. The additional analysis-only dsl_source_artifact_id argument supplies the proposed manifest DSL artifact ID needed by RuleNodeKey; authoritative compilation derives that ID exclusively from the selected manifest and rejects disagreement.
2. Tooling constructs a synthetic/new proposed manifest with existing DSL pins, rule identities, D/G/P and K/H, then computes its fingerprint and catalog file digest last. No public production API accepts arbitrary analyzed data as authority.
3. RuleVersionResolver applies existing catalog/lifecycle/component/source checks. For graph manifests it invokes the same pure graph analysis algorithm on manifest-selected local artifacts and checks every pin, including membership and composed semantics, before issuing ResolvedEvaluationVersions.
4. A RuleDslCompiler bound to that exact authority compiles the authorized DSL source using the existing API.
5. A RuleGraphCompiler bound to that exact authority calls compile_authorized with that exact sealed CompiledRuleSet. It loads only the selected graph source through the authority, verifies D/G/P/K/H and all members, then privately seals one ValidatedRuleGraph and RuleExecutionPlan.
6. The authority authorizes issuance and runtime use; RuleEngine reauthorizes the exact plan and exact compiled objects immediately before execution.

The authority retains one private strong reference to its issued plan for this one graph artifact, plus the existing compiled issuance records. It is not a process registry. A repeat cold graph compilation under the same authority must reconcile to that already-issued immutable plan or fail; it cannot silently replace it. No public register/adopt method lets callers install plans. New runs resolve new authorities and issue new plans even when all strings match.

Public construction, dataclasses.replace, shallow/deep copy, pickle/deserialization, changed data plus recomputed hashes, copied authority labels, or caller-supplied graph/plan JSON must not mint an issued artifact. A byte-identical deserialized plan is an inspection value only. Authorization checks exact object identity, private factory provenance, exact same authority, exact issued CompiledRuleSet/rules, complete membership, and manifest-pinned digests. It never relies on hashes alone.

Threat model matches Prompts 06/07: untrusted configuration and supported public API misuse are covered; arbitrary hostile Python memory mutation/private monkeypatching is not a claimed boundary. No cryptography, signatures, HMAC, random tokens, external service, or process-global registry is introduced.

### 9.3 Replacement, replay, and lifecycle

Before each compile request, including cache hits, re-read/revalidate the selected graph source and repeat authorization. Post-resolution semantic source replacement fails against D/G/P. At execution use the sealed in-memory plan; runtime never reparses files or swaps it while a chart is running. Disk changes during execution cannot alter the selected immutable objects; a new compile/resolve detects them. A supplied different plan/authority fails even when labels and manifest fingerprint are equal.

Replay selects REPLAY using the existing resolver, reconstructs trusted objects from retained authorized DSL/graph sources and exact component implementations, and checks the retained plan/trace/match digests. Retain the manifest, catalog decision, both sources or authorized canonical reconstructions at their logical paths, K/H, DSL and predicate/evaluator components, snapshot/context/instant, source order, and expected logical results. JSON is not a substitute for compiler artifacts. Missing artifacts fail HISTORICAL_CONTENT_UNAVAILABLE; unavailable compatible runtime fails the existing replay compatibility error. No fallback or download.

Rollback selects a whole compatible rule-set/component combination under existing Prompt-06 policy. Deprecated requires explicit rollback authorization; archived is replay-only. Lifecycle transitions never rewrite semantic content or change D/G/P/K/H. A changed lifecycle affects new resolution policy and audit, not an in-flight sealed run. Preserve both graph versions for coexistence and replay.

## 10. Execution API, ordering, and cache

### 10.1 Runtime sequence and API restriction

Proposed API signatures (keyword-only inputs):

```text
RuleGraphCompiler.analyze_source(
    source_id, payload, analyzed_rule_set, dsl_source_artifact_id
) -> GraphAnalysisSucceeded | GraphCompilationFailed

RuleGraphCompiler(resolved_versions, cache_capacity=1)
RuleGraphCompiler.compile_authorized(
    compiled_rule_set
) -> GraphCompilationSucceeded(plan) | GraphCompilationFailed

ResolvedEvaluationVersions.load_authorized_graph_source(...)
ResolvedEvaluationVersions.authorize_graph_analysis(analysis)
ResolvedEvaluationVersions.authorize_execution_plan(plan) -> None

RuleEngine.evaluate_plan(
    plan, condition_evaluator, snapshot, context
) -> GraphEvaluationProduced(record) | GraphEvaluationFailed(diagnostics)
```

The manifest selects source identity; compile_authorized has no caller path, byte, graph, edge, or order override. authorize_graph_analysis is validation only and cannot issue a seal. Issuance hooks are private.

Plans are constructed during compilation, before chart evaluation. Runtime may compile a missing plan through the compiler before entering RuleEngine, but MUST NOT recompute topology, choose another sort, filter nodes by domain, prune failed branches, or replace the plan during evaluation. A plan always covers the whole selected rule set.

RuleEngine first verifies engine/plan/compiled/evaluator same-authority and all plan pins. The new plan API accepts an existing AstroStateSnapshot and PredicateEvaluationContext, never independently supplied state/digest/context-mapping triples. It calls authority.authorize_snapshot(snapshot), requires context.evaluation_instant to equal the authority's normalized explicit instant (UTC, zero fractional seconds), derives S from snapshot.logical_digest and C as SHA-256 of canonical_json_bytes(context_canonical_projection(context)), and obtains PreparedAstroState through the existing prepare_predicate_snapshot adapter. Failed preparation aborts with RUNTIME_INVARIANT and its bounded preparation diagnostic; no RuleMatch is published. Missing per-predicate capabilities remain ordinary typed outcomes after successful preparation. It evaluates sequentially according to execution_order, records dependency decisions and actual condition outcomes, constructs one RuleMatch per node, verifies complete membership and trace consistency, then publishes the immutable record. The existing factual preparation API supplies state; graph code never manufactures or mutates AstroState.

For graph-enabled authorities, direct `build_match` and public `evaluate_compiled_rule` fail DIRECT_EXECUTION_BYPASS before evaluating anything. An unbound engine cannot evaluate a compiled graph rule. The graph loop uses a private shared condition helper, not an exposed bypass flag/token. Graph-null DSL evaluation and legacy current-v1 paths behave exactly as before. Public callers cannot request a subplan or inject prerequisite RuleMatches.

`GraphEvaluationRecord` is a private-factory-sealed audit envelope owned by RuleEngine containing the exact authority, plan, snapshot/context digests, one source-ordered tuple of RuleMatches and associated per-node traces. Its `ordered_matches` view is derived with existing `RuleEngine.order_matches`: `(-priority, rule_id, rule_version, evaluation_plan_position)`. Do not store a second independently editable result list. Internal execution order is observable in the explicit audit trace only.

Source positions, DSL root IDs, RuleMatch metadata, and standard result ordering are never overwritten with topological rank. Current v1 ordering is unchanged. No graph data is added to public Career/Yoga output. The graph's completed record can supply ordinary matches to later orchestration/inference through existing contracts; Prompt-08 does not wire it into Career, Yoga, or a new public endpoint.

### 10.2 Plan cache

Master §§104, 117–120 requires a compiled-plan cache boundary; implement one optional instance-owned LRU in RuleGraphCompiler with capacity 0 or 1, default 1. One authority selects exactly one DSL document and one graph artifact, so a larger per-authority cache has no justified semantic workload. Capacity 0 disables acceleration, not reauthorization or the authority's single issuance reference. Test eviction/replacement on raw-format variants and disabled mode.

Exact logical key:

```text
(
 manifest_fingerprint_sha256,
 graph_source_raw_sha256,
 declarations_sha256,
 compiled_rule_set_sha256,
 graph_compiler_content_sha256,
 graph_contract_sha256,
 dsl_component_projection_sha256,
 predicate_library_component_projection_sha256,
 condition_evaluator_component_projection_sha256,
 ordered_DSL_source_artifact_projection_sha256
)
```

Component projections are the existing canonical ComponentIdentity serialization; ordered DSL artifact projection is the exact manifest array. Manifest and compiled-set pins transitively include system, set version, IDs/revisions, membership/order, and DSL schema. Including raw graph bytes ensures audit provenance is refreshed after formatting changes, although the same semantic sealed plan can be reused after verification.

The authority object is a structural partition, not a memory-address component of canonical keys. No cross-authority sharing of sealed plans is permitted. Two compiler/authority pairs coexist in one process with separate caches. A hit repeats source analysis/pin verification, exact compiled-object authorization and plan authorization before returning. Failed authorization evicts that entry and returns failure with no stale fallback. Failures are never cached.

Content/component/schema/limit changes produce new keys and require a new governed manifest. Lifecycle-only changes do not change semantic keys; fresh resolution enforces changed eligibility. Source changes can replace the one cache entry only after reauthorization; semantic changes under the old authority fail. Cache entries contain no chart facts or evaluation outcomes. Telemetry is noncanonical.

Incremental recomputation, partial graph recompilation, dirty-node propagation, live edits, result caches, inference caches, parallel scheduling, and active-graph globals are deferred and prohibited. The master does not require incremental evaluation in this bounded stage. Always validate/reconstruct the complete graph and plan; do not ship a placeholder incremental API.

## 11. Locked resource limits

| Resource | Exact limit | Rationale |
|---|---:|---|
| Graph source bytes | 1,048,576 | Bounded input, matching the accepted DSL source ceiling |
| Graph artifacts per selected set | 1 | One selected declaration authority |
| Nodes | 1..256 | Matches existing one-document DSL rule limit |
| Edges total, all kinds | 4,096 | Bounded sparse relationships and traces |
| Incoming dependencies per node, all kinds | 32 | Prevents quadratic dense declarations without evidence of need |
| DAG depth in nodes, roots=1 | 64 | Bounded dependency chains independent of Python recursion |
| JSON container nesting, root=1 | 8 | Schema needs at most five container levels; headroom is finite |
| Mapping entries | 16 | Exact schemas are smaller; rejects oversized unknown objects early |
| Authoring JSON array elements | 256 | Rows at most 256; each dependency list also constrained by combined 32 limit |
| All strings | 256 code points | Identifiers additionally at most 128; source IDs at most 256 |
| Diagnostic records | 256 | At most 255 ordinary errors plus final truncation marker |
| Cycle witnesses | One per cyclic SCC, at most 256 nodes plus repeated start | No exponential cycle enumeration |
| Cache entries per compiler | 0 or 1, default 1 | Exactly one manifest-selected plan per authority |
| Issued plan retained per authority | 1 | Prevents replacement and unbounded issuance history |
| Runtime rule trace records | N, at most 256 | Exactly one per node |
| Runtime dependency decisions | E, at most 4,096 | Exactly one per edge, no transitive expansion |

Parser preflight counts nesting outside JSON strings with escape-aware scanning before recursive stdlib decode. It checks byte bounds before decoding, duplicate keys during decode, and collection/string limits before canonical expansion. No reliance on catching RecursionError as the intended bound. Structural parsing error yields one fatal diagnostic and no downstream graph.

All limits are acceptance limits. A host timeout is an operational abort with no authoritative result; wall time never chooses topology or a canonical diagnostic. Predicate timeout behavior remains owned by Prompt-01. No planner deadline is a substitute for bounded traversal.

## 12. Typed diagnostics

GraphDiagnostic is frozen and contains exactly `code, message, stage, source_id, field_path, node_source_order|null, prerequisite_source_order|null, details`. Messages are fixed by the following table; code names are prefixed with `P08E`. Details are schema-defined safe IDs, integer positions/counts, enum strings, and bounded tuples; never raw source, exceptions, absolute paths, stack traces, or arbitrary reprs.

| Code | Fixed message / condition |
|---|---|
| P08E001_INVALID_SOURCE | Graph source violates the encoding, path, or strict JSON contract. |
| P08E002_DUPLICATE_KEY | A graph object repeats a field. |
| P08E003_SCHEMA_MISMATCH | Graph fields or schema version are unsupported. |
| P08E101_UNKNOWN_DEPENDENCY | A dependency is not a member of the selected rule set. |
| P08E102_REVISION_MISMATCH | A dependency revision differs from its selected rule revision. |
| P08E103_VERSION_MISMATCH | Graph system, family, or rule-set version differs from the selected manifest. |
| P08E104_DUPLICATE_DEPENDENCY | A dependency pair and kind are repeated. |
| P08E105_CONFLICTING_DEPENDENCY | A dependency pair declares more than one kind. |
| P08E106_SELF_DEPENDENCY | A rule depends on itself. |
| P08E107_MEMBERSHIP_MISMATCH | Graph nodes are not the exact compiled manifest membership. |
| P08E108_CROSS_DOMAIN_DEPENDENCY | Dependency nodes have different domain scopes. |
| P08E201_CYCLE | The rule dependency graph contains a cycle. |
| P08E301_UNAUTHORIZED_SOURCE | The selected authority does not authorize this graph source. |
| P08E302_AUTHORITY_MISMATCH | Graph or plan objects do not share the exact issued authority. |
| P08E303_COMPONENT_MISMATCH | Graph or DSL component contracts do not match the manifest. |
| P08E304_DECLARATION_DIGEST_MISMATCH | Graph declarations differ from the selected manifest. |
| P08E305_GRAPH_DIGEST_MISMATCH | Validated graph semantics differ from the selected manifest. |
| P08E306_PLAN_DIGEST_MISMATCH | Execution plan semantics differ from the selected manifest. |
| P08E307_DIRECT_EXECUTION_BYPASS | Graph-enabled rules require the authorized plan entry point. |
| P08E308_RUNTIME_INVARIANT | Graph execution cannot publish a complete consistent rule ledger. |
| P08E401_LIMIT_VIOLATION | A locked graph resource limit was exceeded. |
| P08E999_DIAGNOSTIC_LIMIT | Additional graph diagnostics were deterministically suppressed. |

Limit details have exact `resource, limit, observed`. Cycle details have `members, witness`. Unknown/revision details contain safe rule_id/revision; unsafe lexical IDs use field_path alone. Digest details use named expected/observed lowercase digests. Authority errors never expose object identities.

Stage order is source, parse, schema, membership, edges, cycles, planning, authorization, execution. Source/parse structural failures are fatal. Otherwise deterministic validation visits schema fields in §4 order; unknown fields sort lexically; valid rule rows are indexed in manifest order, unmatched rows by rule_id/revision; dependency references sort by ID/revision until positions resolve. Ties retain array index only for diagnostics about identical duplicate occurrences. Final ordering is `(stage ordinal, node position or 256, prerequisite position or 256, code, field_path, canonical details bytes)`. No discovery hash order enters output.

Keep first 255 ordinary diagnostics in this canonical traversal, then append P08E999 as the last record if further diagnostics exist. Traversal remains bounded by §11. Do not run planning after invalid membership/edges. Cycle diagnostics must distinguish SCC members from merely blocked descendants. Byte/source coordinates are optional only in raw parser logs, never in canonical semantic identity; field_path is the required public diagnostic location.

Versioning resolution failures retain existing VersioningError codes. Map graph authority/bypass to AUTHORITY_MISMATCH, component failures to INCOMPATIBLE_COMPONENT_VERSION, D/G/P mismatch to CONTENT_DIGEST_MISMATCH, structural graph invalidity to INVALID_VERSIONING_DATA, and missing retained sources to HISTORICAL_CONTENT_UNAVAILABLE, carrying the bounded P08 diagnostic in details. Pure compiler analysis returns GraphCompilationFailed; neither path returns a RuleMatch.

## 13. Serialization boundary

Public presentation output remains the existing OutputAssembler contract with no graph fields. Existing public JSON and RuleMatch logical JSON do not reconstruct an execution plan or evaluated graph record.

Internal `to_logical_data` projections expose graph/plan/trace data for deterministic inspection, scenario tests, and replay records. They contain no private seals or authority object. Untrusted JSON may parse only into unsealed diagnostic data. There is no public authoritative `from_json`, pickle restore, plan adoption, graph mutation, or digest-setting API.

Trusted reconstruction means resolve the local authorized manifest and artifacts, invoke the same compilers, compare all canonical identities, and issue new same-run sealed objects. A digest detects inconsistency; replacing both data and digest does not prove authorization. Authority comes from the existing catalog/resolver chain and exact issued objects. Public result objects and caller trace references are not inputs to graph planning or prerequisite outcomes.

## 14. Roadmap and exclusions

After Prompt-08 acceptance, the approved order is:

1. FWP-01 Core Input and Enrichment Closure.
2. FWP-02 Timing Systems Integration.
3. FWP-03 Governed MVP Rule Library.
4. FWP-04 Six-Domain Interpretation Completion.
5. FWP-05 Stable Public API and End-to-End Acceptance.
6. Prompt-09 Architecture Verification.
7. Prompt-10 Production Readiness and Release Certification.

Prompt-08 stage-specific ownership/absence tests are acceptance checks for this component. They do not implement the Prompt-09 verification framework, repository-wide architecture scanner, release certification, or any functional work package.

Exclude current-v1 migration, Career/Yoga integration, corpus activation, new predicates/operators, astrology tables/weights/meaning, public serializers/schema/frontend/API/mobile, plugin framework, generic workflow tasks, enrichment scheduling, inference changes, graph visualization, distributed execution, cryptographic provenance, and remote artifact services. GitHub delivery and existing branch cleanup remain deferred to Prompt-10.

## 15. Specification-session preservation evidence

The session started on the exact requested branch/HEAD with no staged files. Prompt-06 and Prompt-07 acceptance are recorded from the user's instruction (Prompt-07 PASS; blockers/highs/mediums all zero), not inferred from old specification-session status headings.

A byte inventory captured all tracked files, all non-ignored untracked files, relevant ignored project artifacts, and .git/info/exclude: **589 files**. Its SHA-256 is **9cd69e8ae3d15144fb150be7aaf671a9c59927c816c9323801c5b8e63b39835e** over the ASCII JSON path-to-SHA256 map with sorted keys and compact separators. The capture is session audit data; no extra report file was created. Generated dependency/build/bytecode/pytest/virtual-environment caches are not project source artifacts; unreadable old virtual-environment temporary directories were not treated as source changes.

Relevant ignored files captured were:

```text
systems/Jyothishyam-Systems-and-Subsystems-Status.md
systems/Parasara/tests/snapshots/generated_surya_parasara_output.json
systems/Parasara/tests/snapshots/generated_vertical_slice_career.json
systems/SuryaSiddhanta/ndastro_engine/data/ephemeris/de440t.bsp
```

The 51 inherited status entries were:

```text
 M systems/Parasara/engine/domain/factories.py
 M systems/Parasara/engine/enrichments/yoga_engine.py
 M systems/Parasara/engine/inference/config.py
 M systems/Parasara/engine/inference/engine.py
 M systems/Parasara/engine/interpreters/career.py
 M systems/Parasara/engine/output_assembler.py
 M systems/Parasara/engine/rules/evaluator.py
 M systems/Parasara/engine/rules/loader.py
 M systems/Parasara/engine/rules/prepared_state.py
 M systems/Parasara/engine/rules/rule_engine.py
 M systems/Parasara/engine/rules/yoga_loader.py
 M systems/Parasara/tools/generate_snapshot.py
?? systems/Parasara/Documentation/Engine/MVP/Manohar-try1.json
?? systems/Parasara/Documentation/Engine/MVP/Manohar-try2.json
?? systems/Parasara/Documentation/Engine/MVP/Manohar-try3.json
?? systems/Parasara/Documentation/Engine/MVP/Manohar-try4.json
?? systems/Parasara/Documentation/Engine/Prompt-02/README.md
?? systems/Parasara/Documentation/Engine/Prompt-02/Reports/README.md
?? systems/Parasara/Documentation/Engine/Prompt-02/requirements/Prompt-02-RuleMatch.md
?? systems/Parasara/Documentation/Engine/Prompt-03/requirements/Prompt-03-InferenceEngine.md
?? systems/Parasara/Documentation/Engine/Prompt-06/requirements/Prompt-06-Rule-Versioning.md
?? systems/Parasara/Documentation/Engine/Prompt-07/requirements/Prompt-07-Rule-DSL.md
?? systems/Parasara/config/versioning/parashara_rule_sets_v1.json
?? systems/Parasara/engine/rules/dsl/__init__.py
?? systems/Parasara/engine/rules/dsl/compiler.py
?? systems/Parasara/engine/rules/dsl/models.py
?? systems/Parasara/engine/rules/dsl/parser.py
?? systems/Parasara/engine/versioning.py
?? systems/Parasara/rules/parashara/v1/rule-set-manifest.json
?? tests/dsl/__init__.py
?? tests/dsl/conftest.py
?? tests/dsl/fixtures/macros.yaml
?? tests/dsl/fixtures/minimal.yaml
?? tests/dsl/scenario_manifest.py
?? tests/dsl/test_architecture_scope.py
?? tests/dsl/test_compiler_authority.py
?? tests/dsl/test_determinism_compatibility.py
?? tests/dsl/test_macro_expansion.py
?? tests/dsl/test_parser_schema.py
?? tests/dsl/test_predicate_binding.py
?? tests/versioning/__init__.py
?? tests/versioning/conftest.py
?? tests/versioning/scenario_manifest.py
?? tests/versioning/test_cache_isolation.py
?? tests/versioning/test_compatibility_and_scope.py
?? tests/versioning/test_manifest.py
?? tests/versioning/test_propagation_authority.py
?? tests/versioning/test_replay_rollback.py
?? tests/versioning/test_selection_lifecycle.py
?? tools/validate_prompt06.py
?? tools/validate_prompt07.py
```

The Prompt-06 semantic inventory is the versioning module/catalog/v1 manifest, its integration edits, versioning tests and validator listed in the accepted Prompt-07 specification's worktree record. Prompt-07 adds the DSL package/tests/validator and its approved versioning/rule_engine/synthetic-builder extensions. Shared modified files are cumulative; this session does not claim a byte-level split of uncommitted Prompt-06 versus Prompt-07 edits.

The four Manohar exports, Prompt-02/03 documentation, and prepared_state.py line-ending status are inherited separately. New session documentation is only this Prompt-08 file; the private tracker is the sole edited pre-existing file.

| Protected artifact | Session baseline |
|---|---|
| Prompt-06 specification bytes | 59,991; SHA-256 bb09a93af73c3c6125c70ceb3b74db913b55acc9fec7f63785a3bfdbef6dcc2c |
| Prompt-07 specification bytes | 77,476; SHA-256 bc1d4fb8791ade91b78be55f0b1120b206e62d72a31ab8925c5fa92e97402601 |
| Current v1 manifest file | SHA-256 687c7bb19ce03671882e989db267d588a3c9beace1c42df25390ab643ebae265 |
| Current v1 manifest fingerprint | 3e942f97cec7c24079faabc3db358b84177b752a8eb35a7b0d909f84a92d1220 |
| Current v1 catalog | SHA-256 b4a94e0ff94209bf901e4f74573bb9fb95206116cdf6f9efcda189ccf7135a1a |
| Approved snapshot | 4,041 bytes; SHA-256 da2059ba3cfb92eed267f93d1e41585dac1422d68f685022c8609cfd04ad57af |
| prepared_state.py bytes | SHA-256 a2fca2dd17edd7092e8bee1cc8431891400d09f979a90f4f44d17b71c9466970 |
| Local exclude | SHA-256 7cf3f2dc7f8ba559150be7c20c7a582efd69c4d5d05cbd2bf50cc3aa38166d51 |

prepared_state.py equals HEAD after CRLF→LF normalization; ordinary git diff is empty for it. Its inherited status does not authorize rewriting it. The only project-specific local exclusion is the exact private tracker path. The tracker is ignored by .git/info/exclude line 7, absent from git ls-files and the staged index.

Existing validation executed in this session, before creating this document:

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
& .\jyothishyam_env\prompt01-py311\Scripts\python.exe tools/validate_prompt07.py --mode full
& .\jyothishyam_env\prompt01-py314\Scripts\python.exe tools/validate_prompt07.py --mode full
```

Both returned exit 0 and PROMPT_07_VALIDATION: COMPLETE (Python 3.11.9 and 3.14.6). Both collected 1,145 tests with ordered node-ID SHA-256 4eeb57d5ba29aa2ac2b3a3039166b3be4f251a8daf65dd4faba4dabed8b9fea8 and passed the complete repository suite. The validator does not print every suite's pass/skip subtotal, so this document does not invent one.

Both also passed DSL contracts, 60 versioning tests, 619 focused Prompt-01 tests, 17 RuleMatch tests, 19 inference tests, 62 AstroState tests, 93 domain tests, 22 WP17 tests, all composed predecessor scenario gates, rule lint, source-boundary checks, strict snapshot generation and personal-export preservation. Prompt-07 scenario SHA was exactly 248bfabc5cc143ab4d64d5b297e5a3449b2573459f2bd22428708ec1c745beee, including hash-seed/process/alternate-CWD checks. Prompt-06 scenario SHA was 4299d7792cfaf440751937ae6e5393631ab48df7a294a5f42cb9f4e493a21763.

Initial attempts through bare py -3.11 / py -3.14 failed at import smoke because those launchers did not select the prepared project environments. No dependency installation or source correction was made; the existing dependency-equipped environments passed. Linux validation was not run in this Windows specification session.

The byte comparison after validation confirmed that only the authorized private tracker differed from the initial 589-file inventory, with no new files, staged files, branch changes, or HEAD changes. Final session verification must additionally allow only this one untracked specification. Architecture progress stays 7/10; Prompt-08 remains unimplemented and user review is pending.

## 16. One bounded future implementation plan

### 16.1 Exact files to add

Production files:

```text
systems/Parasara/engine/rules/graph/__init__.py
systems/Parasara/engine/rules/graph/models.py
systems/Parasara/engine/rules/graph/parser.py
systems/Parasara/engine/rules/graph/compiler.py
systems/Parasara/engine/rules/graph/runtime_contract.py
```

Tests, synthetic fixtures, and validator:

```text
tests/graph/__init__.py
tests/graph/conftest.py
tests/graph/fixtures/rules.yaml
tests/graph/fixtures/dependencies.json
tests/graph/scenario_manifest.py
tests/graph/test_schema_and_membership.py
tests/graph/test_planning_and_cycles.py
tests/graph/test_runtime_outcomes.py
tests/graph/test_authority.py
tests/graph/test_canonicalization_and_limits.py
tests/graph/test_cache_replay.py
tests/graph/test_determinism_compatibility.py
tests/graph/test_architecture_scope.py
tools/validate_prompt08.py
```

Only the two listed checked-in fixtures are added. Rules are named synthetic.a/b/c/d and use synthetic domain/category/labels and neutral test weights, never Career/Yoga names or astrology interpretations. Reuse an already registered Prompt-07-compatible factual leaf solely as a binding fixture; runtime status matrices use a test PredicateEvaluator double, as existing tests/dsl/test_compiler_authority.py does. No new production predicate or astrology assertion is needed. Temporary manifests/catalogs, version variants, malformed inputs, large graphs, and lifecycle evidence are generated under test temporary roots, not a new astrology corpus.

### 16.2 Exact existing files permitted to change

```text
systems/Parasara/engine/versioning.py
systems/Parasara/engine/rules/rule_engine.py
tests/versioning/conftest.py
tests/versioning/test_manifest.py
tests/versioning/test_compatibility_and_scope.py
tests/dsl/test_architecture_scope.py
tools/validate_prompt07.py
```

Purposes are strictly limited:

- versioning.py: serialize/parse/validate the supported non-null graph component; verify its selected source and pure analysis; preserve null serialization exactly; add same-authority plan issuance/authorization and historical checks.
- rule_engine.py: add plan evaluation, internal complete ledger and dependency trace production, graph-enabled direct-entry rejection, and private reuse of existing compiled-condition evaluation. Preserve graph-null behavior.
- tests/versioning/conftest.py: extend the synthetic catalog builder with a graph opt-in; existing add/add_dsl defaults and resulting manifests remain unchanged.
- tests/versioning/test_manifest.py: retain rejection of unsupported/malformed non-null graph components and add valid synthetic graph activation.
- tests/versioning/test_compatibility_and_scope.py and tests/dsl/test_architecture_scope.py: replace only obsolete global Prompt-08-absence assertions with graph opt-in/current-v1-null/DSL-ownership invariants. Keep DSL package free of topology/execution code.
- tools/validate_prompt07.py: advance only its historical graph-absence gate to the same opt-in/current-v1/DSL-boundary check. Do not change scenario digests, regression composition, protected pins, or nonmutation behavior.

No DSL production file is listed or needed. No existing fixture or scenario_manifest is listed for modification. No predecessor specification, current v1 manifest/catalog/corpus, inference module, RuleMatch model, conditions, predicates, prepared_state, public serializer, Career, Yoga, frontend, or approved snapshot may change.

### 16.3 Types/APIs, reuse, and restrictions

Implement the types and signatures in §§3/10. graph/models.py owns frozen data and private construction hooks; parser.py owns only strict JSON parsing; compiler.py owns complete graph analysis, planning, projection/digest construction, sealing and cache; runtime_contract.py owns immutable policy data and pure trace/decision projection helpers. RuleEngine alone observes results, applies those policies, and constructs the sealed GraphEvaluationRecord.

Reuse existing CompiledRule/CompiledRuleSet/AnalyzedRuleSet, ResolvedRule, RuleEngine, ConditionEvaluator, PredicateEvaluator, AstroStateSnapshot, prepare_predicate_snapshot, PreparedAstroState, PredicateEvaluationContext, context_canonical_projection, PredicateStatus, PredicateResult, ConditionResult, RuleMatch/RuleMatchStatus/RuleMatchError/RuleTraceReference, canonical helpers, ComponentIdentity, RuleRevisionIdentity, EvaluationVersionManifest, ResolvedEvaluationVersions, RuleVersionResolver, EvaluationRecord, and existing validator helpers. Do not add replacement result hierarchies, selectors, fact stores, or scoring APIs.

Restrict public direct rule execution only for graph-enabled authorities. Restrict graph constructors, replacement/copy/deserialization, caller source overrides, subplans, and caller prerequisite outcomes. Preserve existing graph-null signatures and behavior.

### 16.4 Required behavioral acceptance tests

| Test file | Required cases and concrete assertions |
|---|---|
| test_schema_and_membership.py | Valid strict JSON; exact field/duplicate-key/encoding/path handling; full bijection; roots; empty graph rejected; edgeless nonempty accepted; unknown ID; wrong revision/system/set version; multiple revisions of same ID; excluded member; duplicate/conflicting pair; self edge; cross-domain/system/set forbidden |
| test_planning_and_cycles.py | Synthetic DAG; exact Kahn example [1,2,0,3]; priority independence; multiple roots/leaves; disconnected components; all kinds in topology; self/multinode/optional cycles; SCC witness stable; blocked descendants not cycle members; no emitted partial plan |
| test_runtime_outcomes.py | All seven root statuses × all three kinds; absence only accepts unmatched; unavailable precedence; every dependency decision retained; zero condition calls on dependency skip; condition skip distinguished; roots/disconnected rules continue; optional failures do not gate; passing gates do not force condition truth; no predecessor evidence copied; inference semantics unchanged; complete ledger and existing order_matches |
| test_authority.py | Different and label-identical authorities; copied/replaced graph/plan/compiled rules; coordinated data-and-digest replacement; same-object issuance; forbidden graph deserialization/adoption; source change after resolution; graph-without-DSL; component/source/graph/plan mismatch; direct build_match/evaluate_compiled_rule/subplan bypass; no partial record after fatal failure |
| test_canonicalization_and_limits.py | Exact projections and hash dependency graph; no manifest circularity; JSON permutation/format invariance; position/declaration/condition sensitivity; fingerprint every implementation module and every locked limit; LF/CRLF equivalence; each numerical limit exact boundary and +1, empty lower boundary, diagnostics cap and cycle witness bounds |
| test_cache_replay.py | Disabled/cold/warm equality; capacity 1 eviction via formatting variants; hit reauthorization failure evicts and fails; authority-isolated identical labels; two graph versions in both orders; replay exact retained sources; missing/incompatible historical artifacts fail; production/deprecated rollback and archived rejection; lifecycle-only digest invariance |
| test_determinism_compatibility.py | Scenario bytes on Python 3.11/3.14, independent processes, PYTHONHASHSEED 0/1/12345, repository/alternate CWD, Windows/Linux where available, formatting variants; unchanged Prompt-07 DSL compilation/manifests; unchanged current v1 manifest/catalog/corpus; exact public Career/Yoga and 4,041-byte snapshot |
| test_architecture_scope.py | Sole graph compiler/RuleEngine/ConditionEvaluator/inference owners; no evaluation in compiler; no dependency syntax in DSL 1.0.0; no current-v1 graph imports; no global active graph, incremental API, new result cache, astrology migration, functional-package or Prompt-09 implementation |

Include multiple required prerequisites where one is unsatisfied and another unavailable, optional-only dependents for every outcome, long acyclic chains, cyclic SCCs with outgoing tails, and a graph whose source/priority/topological orders all differ. Verify authoritative objects cannot be recreated by supported constructors even when every visible byte/digest matches.

Tests of timeout use deterministic injected PredicateStatus.TIMEOUT, not elapsed timing thresholds. Cross-platform validation must report actual lanes; do not claim Linux execution from Windows evidence alone.

### 16.5 Non-mutating validator design

Future tools/validate_prompt08.py accepts `--mode focused|full`, default full, and executes under either supported interpreter. It does not install dependencies or create environments. Resolve ROOT from its own location; put generated files and pytest base directories outside the repository, disable bytecode and pytest cache writes, and use existing canonical helpers.

Before and after every mode, compare branch/HEAD/index state and byte hashes of all tracked files, all non-ignored untracked files, relevant ignored snapshots/personal exports/private tracker, and local exclusion rules. Tolerate inherited accepted dirty work; forbid new mutations. Do not rely only on status-path hashes, which miss changes within already-dirty files. Verify tracker ignored/untracked/unstaged; no broad exclude pattern may conceal implementation.

Focused mode runs:

1. Import/version smoke and exact component-source fingerprint checks.
2. tests/graph, tests/dsl, tests/versioning.
3. Existing Prompt-07 focused composition: Prompt-01 condition/predicate/definition tests, Prompt-02 RuleMatch tests, Prompt-03 inference, Prompt-04 AstroState, Prompt-05 domain, WP17 and Prompt-02–07 scenario-manifest gates.
4. Graph scenario manifest and subprocess hash-seed/CWD checks, cold/warm comparison, exact component/source/graph/plan projections, authorization and bypass negatives.
5. Current v1 manifest/catalog/corpus byte hashes and null future slots, exact Career/Yoga regression tests and strict approved snapshot generation into temporary storage.
6. Stage scope, no Prompt-09/FWP additions, private tracker and full byte-preservation comparisons.

Full mode adds complete `tests` and `systems/Parasara/tests` collection/execution, untouched legacy rule lint, and all predecessor validator-equivalent gates. It may compose helpers to avoid redundant full-suite runs, but cannot omit a gate.

scenario_manifest.py emits deterministic canonical data and SHA for positive and negative graphs, plan orders, edge decisions, skip provenance, diagnostic witnesses, and authority-safe logical replay. Lock its expected digest only after independent comparison of both Python lanes. Preserve the accepted Prompt-07 scenario SHA and all earlier protected identities. The validator returns nonzero on any mismatch, unavailable required lane/gate, failure, or unexpected mutation. It never blesses new hashes, approves snapshots, edits lifecycle, or treats missing coverage as success.

Commands from the repository, using its existing dependency-equipped environments:

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
& .\jyothishyam_env\prompt01-py311\Scripts\python.exe tools/validate_prompt08.py --mode focused
& .\jyothishyam_env\prompt01-py314\Scripts\python.exe tools/validate_prompt08.py --mode focused
& .\jyothishyam_env\prompt01-py311\Scripts\python.exe tools/validate_prompt08.py --mode full
& .\jyothishyam_env\prompt01-py314\Scripts\python.exe tools/validate_prompt08.py --mode full
git diff --check
git diff --cached --name-only
```

Equivalent dependency-equipped Python 3.11/3.14 paths are allowed on other platforms. Bare `py -3.11`/`py -3.14` select installed interpreters, which may lack project dependencies. No validator or Prompt-08 test is created or run in this specification session.

### 16.6 Finite implementation order, stop conditions, and review

1. Obtain user approval of this specification in a later session. Reverify accepted predecessor bytes, branch/HEAD/index, private tracker, personal exports and snapshot.
2. Add failing synthetic graph schema/membership/planning/authority/outcome tests within the exact list.
3. Implement bounded parser/models and pure graph analysis, deterministic topology/cycle diagnostics, canonical identities, resource constants and implementation fingerprint.
4. Extend versioning through the non-null graph component seam and temporary synthetic builder. Prove no digest cycles and current-v1/Prompt-07 exactness.
5. Implement sealing, exact plan issuance, single-entry instance cache and cache-hit reauthorization.
6. Add RuleEngine plan execution, typed dependency traces/skips and direct-entry guards using existing private result construction and condition evaluation.
7. Advance only the named historical absence guards. Complete serialization, replay/rollback, coexistence, limits, adversarial replacement and deterministic scenario coverage.
8. Run focused lanes, then full lanes and all protected-byte checks. Resolve findings only within listed files and scope.
9. Conduct an independent implementation review of authority bypasses, coordinated replacement, status/absence distinctions, canonicalization/cycle bounds, component fingerprints, cache reauthorization, regression evidence and mutation inventory. Review must include all production changes and adversarial tests, not just the validator summary. A separate reviewer/session may perform it; this specification session does not spawn or perform that future review.
10. Stop for explicit user acceptance. Do not advance architecture progress to 8/10 before acceptance. Do not start FWP work, Prompt-09/10, or GitHub delivery.

Stop and request approval before editing any unlisted file or changing a predecessor contract; changing current v1, DSL compiled identity semantics/component source, Career/Yoga/public output/snapshot, inference/scoring, astrology meaning or active corpus; adding cross-domain/system references, result expressions, nodes other than rules, incremental execution, cryptography or plugins; raising locked limits; substituting unavailable historical artifacts; weakening a valid predecessor assertion rather than the expressly identified historical scope guards; or updating any protected expected digest to make tests pass.

Implementation acceptance requires every specified behavior and both interpreter lanes, exact protected artifacts, zero unauthorized files, independent review, and user approval. Specification approval alone is not implementation acceptance.

