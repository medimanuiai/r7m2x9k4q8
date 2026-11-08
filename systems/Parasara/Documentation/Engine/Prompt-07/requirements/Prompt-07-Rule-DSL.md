# Parāśara — Prompt‑07 Rule DSL Specification

> **Current Python policy - 2026-11-06:** [Root policy](../../../../../../AGENTS.md) selects Python 3.11.9 only
> for development, tests, and CI and explicitly supersedes every dual-version
> requirement below. Retained Python 3.14 results/commands are historical, not
> current instructions. Run appropriate checks once on the selected runtime;
> keep correctness, regression, end-to-end, and same-runtime determinism checks.
> Missing second-version evidence is never a defect or blocker. Future specs,
> prompts, and handoffs must carry this policy; only an explicit user request
> can reinstate multiple Python versions.

**Document:** `Prompt-07-Rule-DSL.md`  
**Repository-relative path:** `systems/Parasara/Documentation/Engine/Prompt-07/requirements/Prompt-07-Rule-DSL.md`  
**Status:** Specification produced; user specification review pending; implementation not started  
**Baseline:** `main` at `ec6b49a164389aada4e741561d75cb866527e6cf`  
**Architecture progress:** 6/10 prompts accepted; Prompt‑06 complete and accepted  
**Scope:** Prompt‑07 specification only  
**Document version:** 1.0.0  
**Last updated:** 2026-09-07

## 1. Purpose and binding decision

Prompt‑07 shall add one deterministic, typed, declarative authoring and compilation boundary for Parāśara rules. A rule document is parsed and statically validated, macros are expanded, predicate calls are bound to the existing frozen predicate registry, and every valid declaration is lowered to the existing Prompt‑02 `ResolvedRule` plus the existing Prompt‑01 condition representation. The existing `ConditionEvaluator` evaluates that representation, and the existing `RuleEngine` remains the sole producer of `RuleMatch`.

The DSL is not a second rule evaluator, predicate registry, rule-set selector, result model, inference engine, or version authority. Parsing or constructing an AST confers no evaluation authority.

Prompt‑06's accepted `parashara/v1` manifest is immutable and continues to declare:

```json
"future_components": {
  "dsl": null,
  "dependency_graph": null
}
```

Prompt‑07 implementation shall therefore use only synthetic, non-astrology DSL fixtures and synthetic Prompt‑06 manifests. It shall not edit, relabel, migrate, or replace the current `parashara/v1` runtime or manifest. A governed DSL-backed astrology rule-set version is deferred to FWP‑03, where it will require a new rule-set identity, semantic-equivalence evidence, and astrology review. No predecessor contract, current public output, or astrology meaning must change for Prompt‑07.

Normative terms **MUST**, **MUST NOT**, **SHALL**, **SHALL NOT**, **SHOULD**, and **MAY** are binding.

## 2. Governing authority and reviewed repository evidence

Authority applies in this order:

1. `Documentation/AI-Prompt/Jyothishyam Master Architecture Specification v1.0.docx`;
2. `Documentation/AI-Prompt/Prompt-Plan.docx`;
3. accepted Prompt‑01 through Prompt‑06 contracts and implementations;
4. current architecture/current-state documentation;
5. `Documentation/AI-Prompt/Jyothishyam Architecture Consolidation.docx` as secondary historical material.

No separate approved Prompt‑06–10 Functional Completion Map is present locally. Its approved sequence is, however, recorded by the accepted Prompt‑06 specification and the private tracker:

```text
Prompt‑07 Rule DSL
→ Prompt‑08 Dependency Graph
→ FWP‑01 Core Input and Enrichment Closure
→ FWP‑02 Timing Systems Integration
→ FWP‑03 Governed MVP Rule Library
→ FWP‑04 Six-Domain Interpretation Completion
→ FWP‑05 Stable Public API and End-to-End Acceptance
→ Prompt‑09 Architecture Verification
→ Prompt‑10 Production Readiness and Release Certification
```

Repository inspection established these controlling facts:

- `systems/Parasara/engine/rules/models.py` owns immutable `PredicateResult`, `PredicateStatus`, `ConditionResult`, child disposition, errors, and traces.
- `systems/Parasara/engine/rules/registry.py` owns the frozen deterministic `PredicateRegistry`, `PredicateDefinition`, predicate versions, aliases, parameter schemas, capability requirements, and registry fingerprint.
- `systems/Parasara/engine/rules/parameters.py` owns executable predicate parameter validation. The current closed kinds are `house`, `planet`, and `role_collection`.
- The canonical predicate IDs are `ASPECT_EXISTS`, `FUNCTIONAL_ROLE`, `HOUSE_OCCUPANT`, `PLANET_EXALTED`, and `PLANET_IN_HOUSE`, all version `1.0.0`. `ASPECT` is a compatibility alias.
- `systems/Parasara/engine/rules/conditions.py` already owns deterministic `AND`, `OR`, and `NOT` evaluation, left-to-right short circuit, non-factual status precedence, evidence retention, trace construction, maximum depth 64, and maximum nodes 4,096.
- `systems/Parasara/engine/rules/definition_validation.py` already proves static predicate/parameter/capability binding for the current condition form and provides reusable source-identity and semantic-projection ideas. It is not a complete DSL parser or compiler.
- `systems/Parasara/engine/rules/rule_engine.py` owns immutable `ResolvedRule`, `RuleMatch` construction, trace identity, and result ordering. `ResolvedRule` deliberately contains rule metadata but not an evaluator.
- `systems/Parasara/engine/versioning.py` owns `EngineConfig`, `RuleVersionResolver`, sealed `ResolvedEvaluationVersions`, manifest canonicalization, source/rule authorization, component identity, lifecycle separation, and same-run rejection. `EvaluationVersionManifest.dsl` is already typed as `ComponentIdentity | None`, but the Prompt‑06 implementation intentionally rejects a non-null value until Prompt‑07.
- Career materializes current compatibility rules in `systems/Parasara/engine/interpreters/career.py`; Yoga loads, validates, evaluates, and projects current Yoga declarations in `systems/Parasara/engine/enrichments/yoga_engine.py`. Neither path may be redirected during Prompt‑07.
- `systems/Parasara/engine/rules/canonical.py` supplies the shared immutable value model, strict canonical JSON bytes, and SHA-256 projections. Prompt‑07 shall reuse it rather than introduce another JSON canonicalizer.
- Rule YAML currently uses PyYAML `6.0.3` through `yaml.safe_load`. Safe loading rejects arbitrary Python constructors, but the current calls do not reject duplicate mapping keys, anchors/aliases, or merge keys and use YAML implicit scalar resolution. The Prompt‑07 parser therefore needs a stricter, local loader boundary; current loaders remain unchanged for v1 compatibility.
- Existing validators compose focused tests, predecessor gates, full tests, cross-Python/hash-seed/CWD checks, protected snapshots, personal-export integrity, worktree integrity, and private-tracker exclusion. Prompt‑07 shall follow that pattern.

The Master Architecture lists broader future constructs such as count, exists, and reference. Repository evidence does not currently require them. This specification deliberately selects only predicate calls and `all`/`any`/`not`, which lower exactly to the existing condition evaluator.

## 3. Scope and invariants

Prompt‑07 implementation includes:

- one strict `.yaml` authoring format;
- exact document, rule, macro, expression, metadata, and value schemas;
- immutable source and expanded ASTs;
- static binding to the existing predicate registry and parameter schemas;
- finite hygienic macro expansion;
- canonical projections and source, DSL, expanded-AST, and compiled-semantic digests;
- lowering to existing `ResolvedRule` and existing condition mappings;
- sealed compiled artifacts bound to one Prompt‑06 resolved authority;
- a `RuleEngine` entry point that delegates condition evaluation to the existing `ConditionEvaluator` and alone constructs `RuleMatch`;
- typed deterministic diagnostics and bounded instance-local compilation caching;
- synthetic fixtures and tests only; and
- a composed future Prompt‑07 validator.

The following invariants are mandatory:

1. A predicate returns only `PredicateResult`.
2. Logical composition preserves all `PredicateStatus` distinctions; it never uses Python truthiness.
3. The compiler never reads astrology facts, an `AstroStateSnapshot`, current time, environment, network, or arbitrary filesystem paths and never invokes a predicate.
4. The existing `ConditionEvaluator` is the only owner of condition truth, short circuit, status precedence, predicate-result aggregation, and condition trace.
5. The existing `RuleEngine` is the only owner of evaluated `RuleMatch` creation.
6. Inference remains the sole owner of contributions, scoring, confidence, agreement, conflicts, and insufficient-evidence conclusions.
7. Prompt‑06 resolution precedes any authoritative load or compilation. Same labels or digests supplied by a caller do not substitute for the same sealed authority object.
8. `parashara/v1`, Career/Yoga outputs and order, Prompt‑01 through Prompt‑06 identities, and the approved 4,041-byte snapshot remain unchanged.
9. Cross-rule references, dependency resolution, scheduling, and graph cycles remain Prompt‑08 work.

## 4. Singular ownership and named versions

The sole compiler owner shall be `RuleDslCompiler` in `systems/Parasara/engine/rules/dsl/compiler.py`. It owns the finite pipeline, compilation outcome, macro expansion, canonical DSL/AST/compiled projections, and the optional compiled-artifact LRU. Parsing mechanics belong to the subordinate `dsl/parser.py`; immutable values and diagnostic contracts belong to `dsl/models.py`. These modules do not form another engine.

The initial identities are:

| Contract | Identity |
|---|---|
| Authoring schema | `parasara-rule-dsl@1.0.0` |
| Compiler component | identity `parashara-rule-dsl-compiler`, version `1.0.0` |
| Compiler compatibility contract | `resolved-rule+condition@1.0.0` |
| Canonicalization contract | `parasara-rule-dsl-canonical@1.0.0` |
| Macro expansion contract | `parasara-rule-macro-expansion@1.0.0` |
| Compiled artifact schema | `parasara-compiled-rule-set@1.0.0` |

Compiler **version** identifies the implementation release. The compiler **compatibility contract** identifies the observable lowering boundary. The compiler **content digest** fingerprints the implementation modules and locked parser/type/limit tables in the same repository-consistent manner used for other Prompt‑06 components. Changing grammar, type interpretation, expansion behavior, canonicalization, lowering, evidence behavior, or resource-limit semantics requires an appropriate schema/compiler/contract version and a new affected rule-set version. A code-only repair proven to preserve all canonical bytes may use a compiler patch version, but a manifest still pins its exact content digest.

Prompt‑06 remains the only owner of rule-set selection, manifest authority, lifecycle, approval, and rollback/replay. The DSL's optional `governance_ref` is only an opaque authoring reference; it cannot declare or change lifecycle or approval.

## 5. Canonical authoring format

### 5.1 File and text rules

The only Prompt‑07 authoring format is YAML with the exact lowercase extension `.yaml`. `.yml`, JSON, inline Python objects, and alternative DSL syntaxes are not supported. JSON remains the correct existing format for Prompt‑06 catalogs/manifests and other configuration; it is not a second rule-authoring language.

The source contract is:

- bytes decode as strict UTF‑8 without a BOM;
- line endings may be LF or CRLF and do not affect canonical DSL identity;
- every decoded string must already be Unicode NFC; non-NFC text is rejected rather than silently rewritten;
- tabs, if rejected by the YAML parser in structural positions, remain invalid YAML;
- exactly one YAML document is required;
- document root is one mapping;
- mapping keys are strings and must exactly match their schema spelling;
- duplicate keys are rejected at every depth before construction; first-wins and last-wins behavior are forbidden;
- mapping presentation order is not semantic;
- sequence order is semantic unless a field explicitly requires canonical sorted order;
- comments and whitespace are permitted but are excluded from canonical DSL and semantic digests;
- all explicit YAML tags, anchors, aliases, merge keys (`<<`), directives that change tag resolution, and complex mapping keys are rejected;
- block and flow collection presentation are equivalent after parsing;
- quoted scalars are strings;
- unquoted `true` and `false` are Booleans;
- unquoted integers match `0|-?[1-9][0-9]*`;
- unquoted decimals match `-?(0|[1-9][0-9]*)\.[0-9]+`;
- exponent notation, leading `+`, leading zeros, sexagesimal, hexadecimal, octal, `.inf`, `.nan`, timestamps, and implementation-specific implicit types are rejected;
- `null`, `~`, and empty scalar values are rejected everywhere; optional data is omitted or represented by the field's defined empty sequence/mapping;
- negative integer or decimal zero is rejected;
- scalar values not matching a Boolean or numeric token are strings, subject to field validation.

The strict parser shall be built on the already-pinned PyYAML 6.0.3 parser/scanner with a local loader/composer that detects forbidden events and constructs only the above scalar subset. It shall not use unsafe `yaml.load`, constructors selected by source tags, or a second YAML dependency. Pinning PyYAML in the implementation dependency boundary is required; relying only on an environment's incidental installation is insufficient.

### 5.2 Source identity

An authoritative source ID comes from the selected Prompt‑06 manifest's `ordered_source_artifacts[].path`, not from the caller's path spelling. It is a case-sensitive repository-relative POSIX path with no empty, `.`, or `..` segment, drive letter, backslash, URI scheme, or leading slash. Resolution is anchored to the sealed authority's repository root and must remain inside that root.

Diagnostics and canonical data contain only this logical source ID. Absolute paths are never serialized. A caller-provided file outside an authorized source record may be parsed only by an explicitly non-authoritative diagnostic API and can never produce a sealed executable artifact.

## 6. Document and rule schemas

### 6.1 Document schema

The root mapping has exactly these fields. DSL schema 1.0.0 permits exactly one DSL source artifact/document per rule-set manifest; this prevents macro-import and cross-file ordering semantics from leaking into Prompt‑07. A later demonstrated need for multi-file packs requires an explicit compiler/schema revision, not filesystem enumeration.

| Field | Required | Type and rule | Semantic role |
|---|---:|---|---|
| `dsl` | yes | exact string `parasara-rule-dsl` | schema identity |
| `dsl_version` | yes | exact string `1.0.0` | schema version |
| `system` | yes | lowercase ASCII identifier; must equal manifest system | executable association |
| `rule_set` | yes | exact mapping below | executable association |
| `macros` | yes | sequence, possibly empty | authoring/expansion input |
| `rules` | yes | non-empty sequence | ordered executable declarations |

`rule_set` has exactly `family` and `version`, both nonempty exact identifiers. They must equal the resolved Prompt‑06 manifest. Aliases such as `latest` are prohibited. Rule source order is the zero-based position in `rules`; a separately authored `source_order` field is prohibited because it would create two competing orders.

### 6.2 Rule schema

Each `rules` entry is a mapping with these exact fields:

| Field | Required | Type | Rule |
|---|---:|---|---|
| `id` | yes | string | current `ResolvedRule`/`RuleMatch` regex; unique with revision in the document and manifest |
| `revision` | yes | strict SemVer string | exact future rule revision; legacy tokens are not normalized into this DSL |
| `family` | yes | lowercase ASCII identifier | lowers to `ResolvedRule.rule_family` |
| `category` | yes | lowercase ASCII identifier | lowers to `ResolvedRule.category` |
| `domains` | yes | sequence of lowercase ASCII identifiers | unique and lexicographically sorted; empty only for explicit domain-neutral synthetic/diagnostic rules |
| `label` | yes | NFC string | human-readable, authoring-only; never condition truth |
| `priority` | yes | integer | lowers unchanged to `ResolvedRule.priority` |
| `base_weight` | yes | decimal | finite declared rule meaning; lowers once to exact validated Python float |
| `context` | yes | lowercase ASCII identifier | current bounded context, initially `natal` in Prompt‑07 fixtures |
| `quality` | no | decimal in `[0.0, 1.0]` | lowers to `ResolvedRule.quality`; omission lowers to `None` |
| `requires` | yes | ordered sequence of capability references | exact assertion of the expanded predicate requirement union |
| `evidence` | yes | exact evidence declaration | rule-level evidence policy |
| `when` | yes | expression | executable condition |
| `provenance` | no | exact mapping | trace/audit metadata, not executable truth |
| `presentation` | no | exact mapping | non-executable display metadata |
| `governance_ref` | no | opaque safe identifier | reference only; lifecycle remains Prompt‑06-owned |

The `requires` entries have exactly `id` and `version`, are unique and sorted by `(id, version)`, and must equal—not merely contain—the union of all capability ID/version pairs declared by bound predicate definitions after macro expansion. This assertion catches stale author knowledge; runtime readiness and missing-capability outcomes remain predicate/evaluator responsibilities. Conflicting versions for one capability are a compile error.

`evidence` has exactly:

```yaml
evidence:
  mode: predicate_trace_references
```

No other mode exists in schema 1.0.0. This lowers to the existing `RuleEngine` default evidence index (`root_result_id` and predicate trace IDs). It does not impose a match threshold, copy complete predicate evidence, or calculate inference strength.

`provenance` may contain only `source_ref`, `source_title`, `edition`, `chapter`, `section`, `verse`, `translation`, `interpretive_notes`, `tradition_profile`, `author_id`, and `reviewer_id`, each a bounded NFC string. It lowers to `ResolvedRule.provenance`. Omission is permitted for synthetic Prompt‑07 fixtures; future Production lifecycle validation remains responsible for required scholarship and SME evidence.

`presentation` may contain only `description`, `narrative_key`, and `tags`. `tags` is a unique lexicographically sorted string sequence. `label` and `presentation` lower to internal `ResolvedRule.metadata` for traceability but are excluded from executable condition truth. If a future public or narrative contract consumes one of them, Prompt‑06 change classification applies and the relevant semantic/output version must change.

Arbitrary metadata bags are not allowed. Rule lifecycle/status, approval Booleans, tests, score contributions, confidence, narrative text generation, output DTOs, and dependency declarations are not rule-schema fields.

### 6.3 Minimal example

```yaml
dsl: parasara-rule-dsl
dsl_version: "1.0.0"
system: synthetic
rule_set:
  family: prompt07_fixture
  version: fixture-v1
macros: []
rules:
  - id: synthetic.mars_in_tenth
    revision: "1.0.0"
    family: synthetic
    category: placement
    domains: [synthetic]
    label: "Synthetic placement fixture"
    priority: 10
    base_weight: 0.25
    context: natal
    requires:
      - id: planets.house_placement
        version: "1.0.0"
      - id: planets.normalized
        version: "1.0.0"
    evidence:
      mode: predicate_trace_references
    when:
      predicate:
        id: PLANET_IN_HOUSE
        version: "1.0.0"
        arguments:
          planet: Mars
          house: 10
```

This example is non-astrology test data. Its labels and values do not authorize new production meaning.

## 7. Typed value and expression grammar

### 7.1 Value types

YAML scalar decoding produces the closed primitive types `string`, `boolean`, `integer`, and `decimal`. `decimal` is represented during compilation by an immutable canonical decimal value preserving a normalized base-10 string, never binary float or locale-sensitive formatting.

Predicate arguments are not typed by YAML appearance alone. The compiler resolves `PredicateDefinition.parameter_schema` and validates through the existing `ParameterSchema`. For DSL 1.0.0, the only predicate/macro parameter kinds are the repository's current kinds:

| Kind | Accepted DSL value | Canonical value |
|---|---|---|
| `house` | integer | integer 1–12 |
| `planet` | string | existing canonical planet name |
| `role_collection` | non-empty sequence of strings | unique lexicographically sorted tuple from the closed role vocabulary |

Predicate parameter aliases are rejected in DSL source. Predicate aliases are also rejected. Canonical IDs and names make the same source meaning unique. The underlying registry may retain aliases for current compatibility paths.

Adding a registry parameter kind requires an explicit compiler type-adapter addition and compiler semantic version review. The DSL never guesses types from Python annotations or calls arbitrary converters.

### 7.2 Expression grammar

Each expression is a single-key mapping and conforms to this grammar:

```text
Expression       ::= PredicateCall | All | Any | Not | MacroCall
PredicateCall    ::= { predicate: PredicateInvocation }
PredicateInvocation ::= {
  id: CANONICAL_PREDICATE_ID,
  version: SEMVER,
  arguments: ArgumentMapping
}
All              ::= { all: NonEmptySequence<Expression> }
Any              ::= { any: NonEmptySequence<Expression> }
Not              ::= { not: Expression }
MacroCall        ::= { macro: MacroInvocation }
MacroInvocation  ::= {
  id: MACRO_ID,
  revision: SEMVER,
  arguments: ArgumentMapping
}
ArgumentValue    ::= Literal | Sequence<Literal>
MacroBodyValue   ::= ArgumentValue | { parameter: MACRO_PARAMETER_NAME }
```

`Literal` is one permitted non-null scalar. Nested arbitrary mappings and nested collections are not argument values. A parameter reference is legal only in a macro body argument position. It is not a runtime expression and must be fully replaced during expansion.

The supported operators are intentionally only:

- `predicate`, producing one factual `PredicateResult` at runtime;
- `all`, lowering to existing `AND`;
- `any`, lowering to existing `OR`;
- `not`, lowering to existing `NOT`; and
- `macro`, which disappears before lowering.

There is no general comparison, count, exists, membership-expression, capability-check expression, reference expression, quantifier, variable, lambda, or user-defined function in 1.0.0. Current comparison-like needs are closed typed predicate arguments (for example house equality or `role_in` membership) and belong to registered predicate semantics. Adding a general operator without a demonstrated approved rule need would create a second factual engine and is forbidden.

### 7.3 Static and runtime result types

All expression nodes implement the static sum type `ConditionExpression`:

- `PredicateCallNode.static_result_type = predicate_result`;
- `AllNode`, `AnyNode`, and `NotNode.static_result_type = condition_result`;
- `MacroCallNode.static_result_type` is the expanded body's result type and is illegal in the expanded AST.

The common semantic outcome is not Boolean. It is one of the current statuses:

```text
matched
unmatched
missing_capability
invalid_parameters
error
timeout
skipped
```

Compile-time invalid arguments never reach runtime. Defensive runtime statuses remain possible and map through the existing RuleEngine to Prompt‑02 `RuleMatchStatus` without collapsing distinctions.

### 7.4 Logical semantics

Child order is authored sequence order and is preserved in AST, lowered conditions, evaluation, evidence, and trace.

Runtime behavior is exactly the existing `conditions.py` contract:

- `all` evaluates left to right and short-circuits after the first `unmatched`; later children are recorded as skipped with `and_short_circuit_unmatched`.
- `any` evaluates left to right and short-circuits after the first `matched`; later children are recorded as skipped with `or_short_circuit_matched`.
- `not` has exactly one child and inverts only `matched`/`unmatched`; every non-factual status propagates unchanged.
- If a logical result cannot be decided by a factual short circuit, non-factual precedence is `error > timeout > invalid_parameters > missing_capability > skipped`.
- For `all`, a non-factual status observed before a decisive unmatched child takes precedence; for `any`, a later matched child is decisive even after a non-factual earlier child, exactly as currently tested.
- Evaluated predicate results retain their factual evidence and trace in evaluation order. Unevaluated branches never receive fabricated `PredicateResult` objects.
- Missing capabilities remain unavailable evidence, never negative evidence.
- Compiler/configuration failure produces no `RuleMatch`; it is not an unmatched or neutral astrology result.
- `insufficient_evidence` is an inference/domain status owned by Prompts‑03/05 and does not exist in the AST or compiler.

## 8. Immutable canonical AST

### 8.1 Shared source types

All AST and compilation models are frozen, deeply immutable, keyword-only dataclasses using `FrozenMapping`, tuples, and the shared canonical value restrictions.

`SourceSpan` contains:

```text
source_id
start_line
start_column
end_line
end_column
```

Lines and columns are one-based Unicode-code-point positions; the end is exclusive. `source_id` is the logical repository-relative identity. Spans never use absolute paths and are excluded from semantic digests.

Every AST node contains `node_id` and `source_span`. `node_id` is a deterministic structural identity derived from document/rule position, such as `rules.000003.when.all.000001`. It is not user-authored and is excluded from semantic identity because it is derivable from ordered structure.

### 8.2 Source AST nodes

| Node | Required immutable fields | Child ordering and validation | Canonical logical form |
|---|---|---|---|
| `PredicateCallNode` | `node_id`, `source_span`, `predicate_id`, `predicate_version`, `arguments`, `binding`, `required_capabilities`, `static_result_type` | no child expressions; canonical predicate ID/version and validated normalized arguments required | `{kind:"predicate", predicate_id, predicate_version, arguments, binding_sha256, required_capabilities}` |
| `AllNode` | `node_id`, `source_span`, `children`, `static_result_type` | 1–256 children in authored order | `{kind:"all", children:[...]}` |
| `AnyNode` | same | 1–256 children in authored order | `{kind:"any", children:[...]}` |
| `NotNode` | `node_id`, `source_span`, `child`, `static_result_type` | exactly one child | `{kind:"not", child:...}` |
| `MacroCallNode` | `node_id`, `source_span`, `macro_id`, `macro_revision`, `arguments`, `static_result_type` | exact macro and typed argument binding | `{kind:"macro", macro_id, macro_revision, arguments}`; source AST only |

`binding` is a typed immutable projection of the existing `PredicateDefinition`: canonical ID/version, normalized parameter-schema metadata, required capabilities, system scope, and the definition fingerprint. It never contains a handler object, module repr, or callable identity. The selected Prompt‑06 predicate-library component separately pins the whole registry fingerprint.

Macro parameter references are immutable typed value nodes used only inside macro definitions. They cannot appear in a rule's expanded AST.

### 8.3 Expanded AST

Macro expansion creates a new immutable tree containing only `PredicateCallNode`, `AllNode`, `AnyNode`, and `NotNode`. Source nodes are not mutated. Every expanded node retains an expansion provenance tuple of source spans from outer call site through nested call sites to the definition node. Provenance is diagnostic/trace data and is excluded from the expanded semantic projection.

The expanded AST rejects:

- an unknown node kind;
- any remaining macro call or parameter reference;
- an unbound or version-mismatched predicate;
- an argument not equal to the registry-normalized immutable value;
- conflicting capability versions;
- depth greater than 64;
- more than 4,096 nodes in one rule; or
- more than 16,384 expanded nodes in one document.

### 8.4 Lowering

Expanded expressions lower without evaluation:

```text
PredicateCallNode -> {"type": predicate_id, "params": normalized_arguments}
AllNode           -> {"type": "AND", "children": [...]}
AnyNode           -> {"type": "OR", "children": [...]}
NotNode           -> {"type": "NOT", "children": [child]}
```

The result is a `FrozenMapping` accepted by `ConditionEvaluator`. Before publication, it is also passed through the reusable current condition-definition validation/binding boundary or a lossless shared helper extracted from it. The resulting semantic bytes must equal the compiler's independently specified lowering projection. No AST node contains `PredicateResult`, `RuleMatch`, inference data, domain output, or public-output values.

## 9. Predicate binding

For every predicate call, compilation shall:

1. require the selected Prompt‑06 authority and verify its predicate-library and condition-evaluator components against the current frozen production registry/evaluator;
2. require an uppercase canonical predicate ID; aliases such as `ASPECT` are rejected;
3. look up exactly one `PredicateDefinition` in the existing `PredicateRegistry`;
4. require exact `predicate_version` equality; no compatible-range or latest resolution exists;
5. require argument keys to be canonical parameter names and reject unknown names and aliases;
6. use the existing `ParameterSchema` for required/optional fields, defaults, normalization, duplicate collection values, closed vocabularies, and types;
7. retain the normalized arguments and the definition fingerprint in the binding;
8. collect the definition's capability requirements in registry order and reconcile their versions with the existing capability catalog; and
9. reconcile the rule's declared `requires` with the complete expanded union.

Defaults, if a future/current `ParameterSpec` declares one, come only from that exact predicate-version schema and are included in canonical arguments and all downstream digests. DSL-level defaults do not exist.

Runtime reconciliation repeats the security-sensitive component checks: the `PredicateEvaluator`, `ConditionEvaluator`, `RuleEngine`, compiled artifact, and manifest must carry the same `ResolvedEvaluationVersions` object. The evaluator invokes only the registered handler. Unknown predicates, versions, arguments, parameter kinds, capability IDs, or incompatible component fingerprints are fatal compile/authorization diagnostics.

## 10. Finite macro system

Macros are required by the Master Architecture as a duplication-control mechanism, but schema 1.0.0 keeps them purely lexical and finite.

Each macro declaration has exactly:

```text
id: lowercase ASCII identifier
revision: strict SemVer
parameters: ordered sequence of {name, type}
body: Expression
```

It may additionally have authoring-only `label` and `description`. Macro IDs/revisions are unique. Parameter names are unique lowercase ASCII identifiers. Parameter types are exactly `house`, `planet`, or `role_collection` for compiler 1.0.0 and use the same validation adapters as registered predicate parameters.

Expansion rules:

1. A macro reference pins exact ID and revision and supplies every declared argument exactly once; defaults and variadic arguments do not exist.
2. Arguments are typed and canonicalized before substitution.
3. Substitution is structural and hygienic. Only an explicit `{parameter: name}` value node is replaced; text interpolation, string templating, identifier construction, capture, and evaluation are forbidden.
4. Each call receives a fresh immutable copy of the expanded body. Shared Python object identity never leaks across call sites.
5. Expansion proceeds depth-first, left-to-right in the rule expression, with macro bodies traversed in authored child order.
6. A direct self-call is rejected as `P07E306`; an indirect cycle is rejected as `P07E307`. Cycle detection is solely over the macro call graph and is not Prompt‑08 dependency analysis.
7. Expansion depth counts nested macro calls; root call depth is 1 and maximum is 16.
8. Node counts are charged after substitution for every call, including repeated identical calls. Identical expansions are not coalesced because call-site order and trace provenance differ.
9. Expansion records immutable `MacroExpansionTrace` entries containing macro ID/revision, call node ID/span, definition span, canonical arguments digest, expansion ordinal, and expanded root node ID. Entries are in expansion order.
10. Macro trace is internal compilation evidence. It is not inserted into protected public output.

The canonical DSL digest includes all declared macros, including unused ones. The expanded AST digest includes only the actual expanded rule trees. The compiled semantic digest reflects the expanded result, not macro spelling or call provenance. Thus a meaningful expansion change changes expanded and compiled identities, while a semantics-preserving refactor may change source/canonical DSL identity without changing compiled semantics.

The existing `parashara/v1/macros.yaml` is comments-only placeholder material and remains non-executable. Prompt‑07 shall not parse, activate, or place it in an authoritative DSL manifest.

## 11. Compiler pipeline and outcomes

### 11.1 Authoritative ordering

The canonical authoritative pipeline is:

```text
Prompt‑06 EngineConfig resolution
→ manifest/lifecycle/component verification
→ authorized source location and byte-size check
→ bounded UTF‑8 load
→ YAML event safety scan and parse
→ scalar construction and source spans
→ document/rule/macro schema validation
→ source-AST construction and structural limits
→ macro declaration/type validation
→ predicate lookup/version/argument binding in source AST
→ macro call binding and cycle analysis
→ deterministic macro expansion
→ expanded-AST validation and predicate rebinding assertion
→ rule capability-union reconciliation
→ canonical projections and raw/semantic digests
→ lowering to existing condition mapping and `ResolvedRule`
→ Prompt‑06 canonical source/rule/compiler semantic authorization
→ sealed `CompiledRuleSet`
→ existing `RuleEngine.evaluate_compiled_rule`
→ existing `ConditionEvaluator` / `PredicateEvaluator`
→ existing `RuleEngine.build_match`
→ `RuleMatch`
```

The authority must therefore exist before authoritative compilation and is checked again after lowering. A non-authoritative lint/analysis entry point may stop after producing diagnostics and unsealed canonical projections; it must be separately named and cannot return `CompiledRule`/`CompiledRuleSet` or be accepted by RuleEngine.

The public compiler entry point is exact in responsibility:

```text
RuleDslCompiler(resolved_versions=authority).compile_authorized(
    source_id=manifest_source_id,
) -> CompilationSucceeded | CompilationFailed
```

It reads only the one manifest-authorized source. A separate `analyze_source(*, source_id, payload)` class-level diagnostic API may accept caller bytes, performs no filesystem access, has no resolved authority, returns only unsealed analysis/diagnostics, and is never accepted by `RuleEngine`.

### 11.2 Stage ownership

| Stage | Owner | Failure behavior |
|---|---|---|
| source resolution/authority | Prompt‑06 resolver and authority extensions | typed versioning/authorization diagnostic; no read outside authorized root |
| byte load/encoding/size | strict parser | one fatal source diagnostic |
| YAML feature/duplicate/parse checks | strict parser | deterministic parser diagnostics; no constructed executable document |
| schema and lexical value checks | compiler schema pass | collect bounded errors in schema traversal order |
| source AST and spans | parser + immutable models | no evaluation |
| predicate and parameter binding | compiler using existing registry/schema/catalog | collect deterministic binding errors |
| macro graph/expansion | compiler | all cycles/limits are compile errors |
| expanded validation/lowering | compiler plus reusable current validator | disagreement is compiler contract failure |
| semantic authorization/sealing | Prompt‑06 authority + compiler factory | all-or-nothing executable outcome |
| condition evaluation | existing `ConditionEvaluator` | existing typed outcomes |
| RuleMatch construction | existing `RuleEngine` only | existing Prompt‑02 validation |

### 11.3 Compile result types

Compilation returns a closed immutable union:

```text
CompilationSucceeded
  compiled_rule_set: CompiledRuleSet
  diagnostics: ()

CompilationFailed
  compiled_rule_set: None
  diagnostics: tuple[DslDiagnostic, ...]  # non-empty
```

No partial executable rule set is returned. A diagnostic-only analysis result is explicitly unsealed. AST construction and successful schema validation alone never create authority.

`CompiledRule` contains:

```text
compiled_rule_schema_version
resolved_rule: existing ResolvedRule
expanded_condition_ast
lowered_condition: FrozenMapping
predicate_bindings
required_capabilities
source_identity
source_file_sha256
canonical_dsl_sha256
expanded_ast_sha256
compiled_semantic_sha256
macro_expansion_trace
resolved_versions  # exact same sealed authority, private/noncanonical
compiler_seal      # private factory token, noncanonical
```

`CompiledRuleSet` contains the exact ordered tuple of `CompiledRule`, document-level digests and component identities, the same sealed authority, and a private compiler seal. It is deeply immutable. Its logical serializer omits the authority object's Python identity and private seal but includes the manifest fingerprint string.

### 11.4 Lowering to `ResolvedRule`

The compiler constructs the existing class with this exact mapping:

| DSL | `ResolvedRule` |
|---|---|
| document `system` | `system` |
| rule `id` | `rule_id` |
| rule `revision` | `rule_version` |
| rule `family` | `rule_family` |
| document `rule_set.version` | `rule_set_version` |
| `category` | `category` |
| canonical sorted `domains` | `domains` |
| canonical decimal converted after bounds check | `base_weight` |
| `priority` | `priority` |
| `context` | `context` |
| optional `quality` | `quality` |
| optional strict provenance | `provenance` |
| label/presentation/governance/source compiler metadata | `metadata` |
| Prompt‑06 manifest global ordered position | `evaluation_plan_position` |

There is no new rule-result model. `CompiledRule` is a pre-evaluation carrier because existing `ResolvedRule` intentionally does not own conditions; it is not a replacement for `ResolvedRule` and contains that exact existing object.

`RuleEngine.evaluate_compiled_rule` shall accept only a sealed `CompiledRule` bound to the engine's exact authority, call the existing `ConditionEvaluator` with its lowered condition, then call the existing `build_match`. For a manifest with non-null DSL, direct `build_match` using an unsealed/caller-created `ResolvedRule` shall be rejected. Existing v1 manifests with `dsl: null` retain their current paths and behavior.

### 11.5 Build-time, runtime, and cache policy

The same compiler implementation may run in validation/build tooling and at local runtime. Production deployment should precompile and validate governed packs, but runtime must re-verify source/component/compiled digests against the selected manifest before using cached or persisted artifacts. Persisted compiled Python objects are not trusted authority and are reconstructed through validation.

Only immutable successful compilation results may be cached. The compiler's optional instance-owned LRU has maximum 64 rule-set entries and no process-global active pack. Its key is the canonical tuple:

```text
manifest_fingerprint_sha256
source_file_sha256
canonical_dsl_sha256
dsl_schema_version
compiler identity/version/content_sha256/compatibility_contract
canonicalization_contract
macro_expansion_contract
predicate-library identity/version/content_sha256
condition-evaluator identity/version/content_sha256
ordered source artifact IDs/digests
```

Failures are not cached. Cache hits return the same immutable logical artifact, do not replace authority, and cannot cross manifest fingerprints. Cold and warm canonical bytes are identical. Cache capacity/eviction telemetry is noncanonical.

## 12. Canonicalization and semantic identity

All canonical projections use the existing `canonical_json_bytes`: UTF‑8, no BOM/newline, sorted mapping keys, preserved sequence order, compact separators, NFC strings already validated, finite values, and normalized negative zero. Decimal values are projected as normalized decimal strings with an explicit type wrapper, for example `{"$decimal":"0.25"}`, so binary float formatting never controls identity.

The identities are deliberately distinct:

| Identity | Payload | Changes when |
|---|---|---|
| `source_file_sha256` | exact original source bytes | any byte changes, including comment, whitespace, BOM, or line endings |
| `canonical_dsl_sha256` | full validated document logical form, excluding spans/comments/presentation order but including authoring metadata and macro declarations | any schema-visible content changes |
| per-rule `expanded_ast_sha256` | macro-free condition AST with normalized typed arguments and predicate bindings | executable condition or binding changes |
| rule-set expanded AST digest | ordered `(rule_id, revision, expanded_ast_sha256)` sequence | rule membership/order/expanded condition changes |
| per-rule `compiled_semantic_sha256` | compiler contracts + executable `ResolvedRule` projection + lowered condition + binding/capability/evidence policy | condition, normalized parameter/default, predicate version, capability contract, base weight, priority, family/category/domain/context/quality, evidence behavior, or source order changes |
| compiled rule-set digest | ordered per-rule compiled digests plus document/compiler/component associations | any compiled member/order/contract changes |
| Prompt‑06 rule revision identity | exactly the per-rule compiled semantic digest and its canonical `semantic_contract` | same as compiled rule semantics |
| Prompt‑06 manifest fingerprint | complete selected component/rule/artifact manifest excluding its own fingerprint and lifecycle metadata | any selected executable component or membership/order changes |
| lifecycle metadata | catalog/audit record only | review/approval/lifecycle changes; semantic digests do not change |

The executable `ResolvedRule` projection includes `system`, rule identity/revision/family/set/category/domains, canonical decimal base weight, priority, context, optional quality, evidence mode, and evaluation-plan/source position. It excludes label, presentation prose, governance labels, source spans, compiler trace, and lifecycle state. Predicate binding projections include canonical ID/version, normalized arguments, parameter schema fingerprint, required capabilities, and definition fingerprint. Handler objects and machine modules are not serialized; the Prompt‑06 predicate component digest binds implementation identity separately.

Comments, whitespace, line endings, mapping order, quoted-versus-plain spelling of an identical string, and block-versus-flow collection syntax do not affect canonical DSL or semantic identity. Rule and expression sequence order is semantic. Semantically unordered domains, tags, roles, and required-capability collections must already satisfy their canonical sorted/unique contract.

The source artifact record for a future DSL pack shall include its `canonical_dsl_sha256` as Prompt‑06's existing `semantic_content_sha256`, format `rule-dsl-yaml`, and ordered rule IDs. The raw `source_file_sha256` is retained in the compilation/audit record but excluded from rule, rule-set, and manifest semantic identity. This preserves Prompt‑06's rule that comment, whitespace, and line-ending-only edits do not require a new rule revision or rule-set version. The accepted v1 artifact records and digests are not rewritten.

## 13. Prompt‑06 integration and supported authority

### 13.1 Future manifest binding

A future synthetic or governed DSL-backed manifest pins a non-null `future_components.dsl` `ComponentIdentity`:

```json
{
  "identity": "parashara-rule-dsl-compiler",
  "version": "1.0.0",
  "compatibility_contract": "resolved-rule+condition@1.0.0",
  "content_sha256": "<compiler component digest>",
  "metadata": {
    "dsl_schema_version": "1.0.0",
    "canonicalization_contract": "parasara-rule-dsl-canonical@1.0.0",
    "macro_expansion_contract": "parasara-rule-macro-expansion@1.0.0",
    "compiled_artifact_schema_version": "1.0.0"
  }
}
```

The same manifest pins:

- predicate-library identity/version/registry content digest;
- condition-evaluator identity/version/content digest;
- ordered rule membership and source order;
- each rule's compiled semantic digest and canonical semantic contract;
- ordered DSL source artifacts with raw and canonical digests;
- rule-set family/version, engine contract, inference, knowledge, and output compatibility as already required by Prompt‑06; and
- `dependency_graph: null` throughout Prompt‑07.

Prompt‑07 implementation may relax the Prompt‑06-era `EvaluationVersionManifest` check only from “both future components must be null” to:

- `dsl` may be the exact supported `ComponentIdentity`;
- `dependency_graph` must remain null;
- current v1 must still have both null; and
- a DSL source format/rule semantic contract is invalid when `dsl` is null, while non-DSL current v1 formats remain invalid when an incompatible DSL-only execution route is attempted.

That is activation of an accepted extension slot, not a redefinition of Prompt‑06 ownership.

### 13.2 Authorization sequence

`RuleVersionResolver` verifies the catalog, manifest, compiler component, predicate/evaluator components, authorized source path, and resource boundary before compiler use. `RuleDslCompiler` is constructed with the exact returned authority. After canonical parsing and compilation, `ResolvedEvaluationVersions.authorize_compiled_rule_set` verifies:

- object seal and exact authority identity;
- document system/family/version;
- compiler and schema contracts;
- canonical DSL, expanded AST, and compiled rule-set digests; the raw source digest is retained for audit but is deliberately non-semantic;
- ordered source artifact membership;
- exact ordered rule ID/revision membership and positions;
- each per-rule compiled semantic digest against `RuleRevisionIdentity.semantic_content_sha256`; and
- each lowered `ResolvedRule` projection against its manifest semantic contract.

`RuleEngine.evaluate_compiled_rule` repeats exact authority/seal/rule membership verification immediately before evaluation. A caller-supplied source, parsed document, AST, copied `ResolvedRule`, copied manifest, matching digest string, or separately resolved but label-equal authority is rejected.

Same-run authority, mid-run replacement rejection, caller relabeling rejection, two-version isolation, deterministic replay, cache isolation, and lifecycle/content separation therefore continue unchanged. A replay must retain the exact compiler component and DSL artifacts or fail as historical content unavailable; it never downloads replacements.

### 13.3 Current v1 preservation

The file `systems/Parasara/rules/parashara/v1/rule-set-manifest.json` remains byte-identical with fingerprint `3e942f97cec7c24079faabc3db358b84177b752a8eb35a7b0d909f84a92d1220`. The catalog file digest and entry remain unchanged. No current Career or Yoga path imports or invokes the DSL compiler. No source under `systems/Parasara/rules/parashara/v1/` changes. Prompt‑07 tests assert all of these facts.

## 14. Deterministic diagnostics

`DslDiagnostic` is a frozen model with exactly:

```text
code
message
stage
source_id
source_span | None
rule_id | None
rule_revision | None
macro_id | None
node_id | None
field_path
details
severity = error
```

Messages are fixed by code; raw parser exceptions, source scalar contents, absolute paths, stack traces, object reprs, and secrets are not included. `details` uses the existing bounded safe canonical-value pattern and contains only stable expected/observed identifiers or counts.

Required codes are:

| Code | Meaning |
|---|---|
| `P07E001_INVALID_ENCODING` | source is not strict UTF‑8/NFC or has BOM |
| `P07E002_SOURCE_SIZE_LIMIT` | byte limit exceeded before parse |
| `P07E003_INVALID_YAML` | malformed YAML/event stream |
| `P07E004_DUPLICATE_KEY` | repeated mapping key |
| `P07E005_FORBIDDEN_YAML_FEATURE` | tag, anchor, alias, merge, or directive is forbidden |
| `P07E006_MULTIPLE_DOCUMENTS` | document count is not exactly one |
| `P07E007_INVALID_SCALAR` | null or unsupported scalar spelling/type |
| `P07E101_UNKNOWN_FIELD` | mapping contains a field outside its exact schema |
| `P07E102_MISSING_FIELD` | required field absent |
| `P07E103_INVALID_FIELD_VALUE` | identity, order, vocabulary, or bounded value invalid |
| `P07E104_INVALID_NUMERIC_VALUE` | numeric spelling/range/conversion invalid |
| `P07E105_DUPLICATE_RULE_REVISION` | duplicate `(id, revision)` |
| `P07E201_UNKNOWN_OPERATOR` | expression node kind unsupported |
| `P07E202_AST_DEPTH_LIMIT` | source/expanded expression too deep |
| `P07E203_AST_NODE_LIMIT` | source/per-rule/document node limit exceeded |
| `P07E211_UNKNOWN_PREDICATE` | canonical predicate ID absent |
| `P07E212_PREDICATE_VERSION_MISMATCH` | call version differs from registry/manifest |
| `P07E213_INVALID_ARGUMENT_NAME` | missing, unknown, or alias argument name |
| `P07E214_ARGUMENT_TYPE_MISMATCH` | argument does not satisfy registered parameter kind |
| `P07E215_PREDICATE_CAPABILITY_MISMATCH` | registry/catalog/rule capability contract differs |
| `P07E301_DUPLICATE_MACRO_REVISION` | duplicate macro `(id, revision)` |
| `P07E302_MACRO_NOT_FOUND` | exact macro identity absent |
| `P07E303_MACRO_ARGUMENT_MISMATCH` | missing/unknown macro argument |
| `P07E304_MACRO_ARGUMENT_TYPE_MISMATCH` | macro argument violates declared type |
| `P07E305_MACRO_PARAMETER_NOT_FOUND` | body references undeclared parameter |
| `P07E306_MACRO_DIRECT_RECURSION` | macro directly invokes itself |
| `P07E307_MACRO_CYCLE` | indirect macro expansion cycle |
| `P07E308_MACRO_EXPANSION_DEPTH_LIMIT` | nested-call depth exceeds 16 |
| `P07E309_MACRO_EXPANDED_NODE_LIMIT` | expanded node budget exceeded |
| `P07E401_COMPILER_VERSION_MISMATCH` | compiler/schema/contract differs from manifest |
| `P07E402_MANIFEST_AUTHORIZATION_FAILURE` | exact resolved authority does not authorize compilation/evaluation |
| `P07E403_SOURCE_DIGEST_MISMATCH` | canonical DSL source digest differs from the authorized manifest artifact |
| `P07E404_COMPILED_DIGEST_MISMATCH` | AST/rule/rule-set compiled digest differs from manifest |
| `P07E999_DIAGNOSTIC_LIMIT` | additional diagnostics were deterministically suppressed |

Invalid encoding, excessive bytes, malformed YAML, forbidden YAML construction, and multiple documents are fatal parser boundaries and yield only the earliest applicable diagnostic. Later stages cannot safely inspect an absent document. Schema/type/binding errors are collected in preorder: document fields in schema order, unknown fields lexicographically, macros in source order, rules in source order, expression nodes depth-first left-to-right, and arguments in registered parameter-schema order followed by unknown names lexicographically. Macro cycles are emitted by macro declaration order with cycle members in canonical call order.

Final diagnostics are sorted by `(stage ordinal, source_id, start line, start column, rule source order, macro source order, code, field_path, discovery ordinal)`. Missing spans sort after present spans at the same source/stage. At 255 ordinary diagnostics, compilation stops collecting; `P07E999_DIAGNOSTIC_LIMIT` is the 256th and final diagnostic. Compilation failure never produces an invalid/unmatched `RuleMatch`.

## 15. Resource and determinism bounds

| Resource | Limit | Repository-grounded reason |
|---|---:|---|
| source file bytes | 1,048,576 | far above the current rule corpus while bounding YAML parser memory |
| YAML documents | exactly 1 | one source identity and no hidden concatenation semantics |
| rules per document | 256 | ample for bounded governed packs; keeps diagnostics and manifest membership reviewable |
| DSL source artifacts per rule set | 1 | avoids cross-file macro/import/order semantics before a demonstrated need |
| macros per document | 128 | supports reuse without becoming a general program/module system |
| macro parameters | 16 | current predicate arities are at most four; 16 is a testable upper bound |
| mapping entries | 64 | all defined schemas are much smaller; prevents metadata bags |
| sequence elements | 256 | aligns with maximum rule/child collections |
| string length | 4,096 Unicode code points | enough for bounded provenance notes; prevents unbounded diagnostic/canonical payloads |
| identifier length | 128 (`source_id` 256) | aligns with current rule/source identity contracts |
| integer magnitude | signed 32-bit | bounds priority and generic integer construction; house schemas remain 1–12 |
| decimal significant digits | 38; scale at most 12 | deterministic exact authoring precision without arbitrary-size arithmetic |
| decimal magnitude | at most 1,000,000 | keeps float lowering finite and inference inputs bounded; not an astrology validity claim |
| source AST depth | 64 | exactly the existing condition evaluator depth |
| source AST nodes per rule | 4,096 | exactly the existing condition evaluator node limit |
| source AST nodes per document | 16,384 | bounds all rule and macro bodies before expansion |
| logical children per node | 256 | bounded left-to-right trace/evidence work |
| macro expansion depth | 16 | sufficient reuse while preventing recursive blow-up |
| expanded nodes per rule | 4,096 | existing evaluator boundary cannot accept more |
| expanded nodes per document | 16,384 | caps aggregate expansion independently of rule count |
| diagnostics | 256 | bounded complete-enough author feedback with stable truncation |
| compiler cache entries | 64 | bounded instance-local LRU; no hidden global authority |

Limits are compiler contract data and are included in its component fingerprint. A change to a limit that changes acceptance or expansion requires compiler compatibility review. Limits are checked iteratively where possible; Python recursion limits are never the contract.

No compiler wall-clock timeout participates in canonical behavior. The structural budgets above are the normative protection against unbounded work. A validator or host may impose an outer timeout as an operational safeguard, but that timeout cannot alter the compiler's diagnostics, identities, or canonical result and cannot convert an incomplete compilation into a valid one.

Canonical results must be byte-identical under Python 3.11 and 3.14, Windows and CI, different hash seeds, repository and alternate CWDs, repeated processes, cold/warm caches, CRLF/LF and equivalent non-semantic YAML formatting. No canonical ordering relies on set/dict iteration, locale, filesystem enumeration, object identity, wall-clock timing, randomness, or platform path spelling.

## 16. Security boundary

DSL source is untrusted configuration. The parser/compiler shall have no construct or code path for:

- embedded Python, `eval`, `exec`, lambdas, comprehensions, arbitrary functions, dynamic imports, reflection, attribute traversal, method selection, or object constructors;
- shell/subprocess execution;
- filesystem reads other than the exact Prompt‑06-authorized source path through the bounded loader;
- filesystem writes;
- network access or remote includes/imports;
- environment variables, process CWD selection, user/home expansion, current time, locale, randomness, or nondeterministic IDs;
- regex supplied by DSL source, unbounded regular-expression evaluation, loops, recursion outside bounded macro traversal, or arbitrary computation;
- YAML tags, aliases, anchors, merge keys, multi-document streams, or object graphs; or
- rule-set version selection, lifecycle transitions, approval claims, dependency resolution, or plugin loading.

Static architecture tests shall parse imports/calls in the DSL package and reject forbidden modules/APIs. This is the approved Python threat model: supported public operations and untrusted rule data are defended; arbitrary hostile mutation of process memory or monkeypatching private internals is not claimed.

## 17. Current corpus inventory and migration boundary

Prompt‑07 inventory, without changing files:

| Classification | Current material | Disposition |
|---|---|---|
| active source/materialization template | `m1_rules.yaml:strong_planet_in_10` | materializes `strong_in_10_<planet>`, revision `1.0`, for the finite current planet set |
| active source/materialization template | `derived_rules.yml:lord_status_10th` | materializes `10th_lord_<lord>`, revision `legacy-unversioned`, when a supported house lord is present |
| active Yoga and Career projection | `yogas.yaml:rajayoga_naive`, revision `1` | existing Yoga condition path plus current Career compatibility fact |
| active Yoga records | `yogas.yaml:dhana_naive`, `arishta_naive`, revision `1` | evaluated/diagnosed in source order; `dhana_naive` currently reports the known unknown `HOUSE_LORDS_COMBINATION` predicate rather than silently matching |
| active synthetic compatibility meaning | `career.base_kendra_strength`, revision `1.0.0` in Career Python/manifest | existing inference baseline; not DSL source |
| shadowed duplicate seed | `m1_rules.yaml:rajayoga_naive` | not the active Yoga source; remains inactive |
| dormant seeds | remaining `m1_rules.yaml` rows, remaining `derived_rules.yml` rows, all `primitives.yml` rows | no activation or migration |
| placeholder | `macros.yaml` comments/example | non-executable; Prompt‑07 syntax does not activate it |
| calibration data | `calibration.json` | non-authoritative for current execution; not a DSL document |
| non-executable metadata | README, comments, descriptions, Yoga fixture pointers, unconsumed seed metadata | does not become executable meaning |

No current corpus file migrates in Prompt‑07. Tests use clearly named `synthetic` systems/families/rules and do not assert astrology correctness. Optional analysis of current files may use an unsealed read-only equivalence tool only if it does not modify sources, manifest, runtime selection, or results; it is not required for acceptance.

FWP‑03 may later create a new, separately governed DSL-backed Parāśara rule-set version. That migration must:

1. preserve old v1 for replay;
2. author canonical `.yaml` documents without copying dormant or shadowed rows into active membership;
3. give every concrete/materialized rule an approved immutable identity/revision;
4. bind predicates/capabilities/compiler/source/AST/compiled digests in a new manifest;
5. prove rule-by-rule condition, status, evidence, base weight, priority, source order, RuleMatch, inference, Career/Yoga, and protected-output equivalence where equivalence is claimed;
6. record every intentional difference as a new astrology-semantic revision with SME review; and
7. pass Prompt‑06 lifecycle gates before any production selection.

Prompt‑07 does not define top-level rule materialization parameters. Existing materialized Career rules remain on their accepted compatibility path. FWP‑03 must either author finite concrete rules or separately approve a versioned finite materialization schema; it cannot infer this behavior from the Prompt‑07 macro system.

## 18. Prompt‑08 boundary

Schema 1.0.0 contains no rule reference or dependency field because no current approved rule needs one. Stable rule IDs and revisions are sufficient for Prompt‑08 to introduce a separately versioned dependency declaration later.

Prompt‑07 shall not implement dependency resolution, graph construction, topological sorting, cross-rule cycle analysis, scheduling, incremental recomputation, graph visualization, dependency-aware caching, rule-result references, or reference-driven execution. Macro expansion order is lexical and local to one document. Macro call-graph cycles are compiler errors; they are not cross-rule dependency cycles.

The Prompt‑07 manifest always retains `dependency_graph: null`. Any need for cross-rule output during implementation is a stop condition, not permission to anticipate Prompt‑08.

## 19. Public and predecessor compatibility

Prompt‑07 requires no public-output change. It shall preserve exactly:

- current `parasara/v1` identity and manifest fingerprint;
- current Career result fields, values, score, confidence, evidence, narrative, and ordering;
- current Yoga rows, firing behavior, evidence, trace, and source ordering;
- existing `RuleMatch` logical fields, status mapping, evidence ownership, trace references, deterministic ordering, and serializer;
- existing InferenceResult/domain values and ownership;
- output schema/profile and internal/public separation; and
- approved snapshot: 4,041 bytes, SHA‑256 `da2059ba3cfb92eed267f93d1e41585dac1422d68f685022c8609cfd04ad57af`.

DSL schema, ASTs, source spans, macro traces, compiler identities/digests, and diagnostics remain internal. They are not added to current DTOs or public JSON. An internal diagnostic serializer may expose them only through an explicitly requested internal operation and safe repository-relative identities.

Prompt‑01 through Prompt‑06 contracts are reused as written. The limited future modifications to `versioning.py` and `rule_engine.py` activate accepted extension points and add supported authority checks; they must leave all `dsl: null` code paths byte/logically exact. If implementation instead requires redefining `PredicateResult`, `RuleMatch`, inference/domain contracts, v1 identity, current public output, or astrology meaning, implementation must stop.

## 20. Bounded future implementation plan

### 20.1 Files to add

Production/compiler files:

```text
systems/Parasara/engine/rules/dsl/__init__.py
systems/Parasara/engine/rules/dsl/models.py
systems/Parasara/engine/rules/dsl/parser.py
systems/Parasara/engine/rules/dsl/compiler.py
```

Tests and synthetic fixtures:

```text
tests/dsl/__init__.py
tests/dsl/conftest.py
tests/dsl/fixtures/minimal.yaml
tests/dsl/fixtures/macros.yaml
tests/dsl/scenario_manifest.py
tests/dsl/test_parser_schema.py
tests/dsl/test_predicate_binding.py
tests/dsl/test_macro_expansion.py
tests/dsl/test_compiler_authority.py
tests/dsl/test_determinism_compatibility.py
tests/dsl/test_architecture_scope.py
tools/validate_prompt07.py
```

The two fixture files are the only checked-in rule documents added by Prompt‑07 and are visibly synthetic. Malformed/limit YAML should be built as bounded in-test strings or temporary files so the fixture directory does not become a second corpus.

### 20.2 Files to modify

```text
systems/Parasara/engine/versioning.py
systems/Parasara/engine/rules/rule_engine.py
tests/versioning/conftest.py
tests/versioning/test_compatibility_and_scope.py
tests/versioning/test_manifest.py
```

Purposes are limited to:

- allow and verify a non-null supported DSL component for non-v1 synthetic/future manifests while retaining `dependency_graph: null`;
- authorize DSL source and sealed compiled semantic identities;
- let the existing `RuleEngine` evaluate a sealed compiled condition through the existing `ConditionEvaluator` and prevent direct DSL-bound `build_match` bypass;
- extend the existing synthetic manifest builder for a DSL component/source/digests; and
- replace Prompt‑06's “no Prompt‑07 implementation” assertion with “current v1 has no DSL binding and no Prompt‑08 implementation,” while preserving all other Prompt‑06 scenarios/digests.

No current rule, Career, Yoga, predicate, inference, domain, output, snapshot, or Prompt‑06 manifest/catalog file is expected to change. If implementation requires another file, stop and obtain authorization before editing it.

### 20.3 Existing types to reuse

Reuse without duplicate ownership:

- `FrozenMapping`, `freeze_canonical`, `canonical_json_bytes`;
- `PredicateDefinition`, `PredicateRegistry`, its registry/definition fingerprints, and production bootstrap;
- `ParameterSchema`, `ParameterSpec`, `ParameterKind`, and validation outcomes;
- `CapabilityRequirement` and the production capability catalog;
- `ValidatedConditionDefinition` concepts/current validation helper and `ConditionEvaluator`;
- `PredicateResult`, `ConditionResult`, statuses, errors, and traces;
- `ResolvedRule`, `RuleEngine`, `RuleMatch`, and their existing order/serializer;
- `ComponentIdentity`, `RuleRevisionIdentity`, `EvaluationVersionManifest`, `ResolvedEvaluationVersions`, and `RuleVersionResolver`; and
- existing validator helpers for worktree, protected artifacts, snapshot, personal exports, subprocesses, and Python lanes.

### 20.4 New types and single owners

`dsl/models.py` owns `SourceSpan`, canonical decimal/value wrappers, source/expanded AST node variants, macro/rule/document declarations, predicate bindings, expansion traces, diagnostics, compiled artifacts, and success/failure unions. `dsl/parser.py` owns only strict YAML byte/event/node conversion with spans. `dsl/compiler.py` owns `RuleDslCompiler`, pipeline orchestration, schemas, type adapters, expansion, canonical projections/digests, lowering, sealing, and cache. `versioning.py` continues to own all authority. `rule_engine.py` continues to own evaluated rule execution orchestration and RuleMatch construction.

No public constructors may mint a sealed `CompiledRule` or `CompiledRuleSet`. `dataclasses.replace`, canonical deserialization, copying labels, or supplying a digest does not confer a compiler seal or Prompt‑06 authority.

### 20.5 Implementation sequence

1. Re-verify the exact accepted Prompt‑06 worktree and protected artifacts.
2. Write failing focused tests for strict parsing, models, binding, expansion, digests, and authority.
3. Implement immutable models and strict parser.
4. Implement schema/type/predicate binding and macro expansion.
5. Implement canonical projections, lowering, sealed results, and compiler cache.
6. Activate the non-null DSL extension in versioning for synthetic manifests only.
7. Add the RuleEngine compiled entry point and bypass rejection.
8. Run focused tests in Python 3.11 and 3.14 and record one cross-Python scenario digest.
9. Run the composed Prompt‑07 full validator only after focused correctness.
10. Conduct one independent review and stop for user acceptance; do not begin Prompt‑08.

### 20.6 Explicit implementation exclusions

Do not add or modify current rule sources, v1 manifest/catalog, Career/Yoga materialization, astrology predicates, weights, tables, inference configuration, public serializers, snapshots, functional work packages, frontend/API/mobile code, remote registries, signing, plugins, or dependency-graph code. Do not add a migration, remediation, review, release, or Prompt‑08 document by default.

## 21. Required future tests

Prompt‑07 implementation acceptance must cover at least:

1. valid minimal synthetic DSL compiles;
2. deterministic source AST, expanded AST, `ResolvedRule`, and compiled digest;
3. strict UTF‑8/NFC and safe YAML restrictions;
4. duplicate-key rejection at every depth;
5. exact unknown-field rejection;
6. static canonical predicate lookup/version binding;
7. required/unknown/alias argument and argument type validation;
8. `all`/`any`/`not` lowering and existing short-circuit parity;
9. preservation of matched, unmatched, missing-capability, invalid-parameters, error, timeout, and skipped distinctions;
10. typed hygienic macro expansion and trace;
11. direct and indirect macro recursion/cycle rejection;
12. source/expanded depth and node limits;
13. accurate safe source-span diagnostics;
14. stable multi-error ordering and diagnostic cap;
15. exact lowering into existing `ResolvedRule` plus current condition mapping;
16. existing `RuleEngine` remains sole RuleMatch producer and `ConditionEvaluator` sole condition evaluator;
17. caller DSL/document/AST/ResolvedRule/compiled copy cannot mint or replace authority;
18. Prompt‑06 resolver/compiler/source/rule binding for synthetic packs;
19. compiler/schema/canonicalization/macro contract mismatch rejection;
20. identical canonical bytes on Python 3.11 and 3.14;
21. hash-seed, process, line-ending, non-semantic YAML-format, and CWD independence;
22. cold/warm compiler and predicate cache equality and two-version isolation;
23. current v1 manifest, catalog, runtime selection, and public identity unchanged;
24. exact current Career public output;
25. exact current Yoga output and ordering;
26. approved 4,041-byte snapshot and SHA-256 exactness;
27. Prompt‑01 through Prompt‑06 focused/regression gates;
28. no dependency-graph/Prompt‑08 module, syntax, import, scheduling, or cache;
29. no current astrology rule/table/meaning changes;
30. private tracker remains ignored, untracked, and unstaged.

Additional required negative coverage includes forbidden tags/anchors/aliases/merge keys/multiple documents/null/implicit timestamp/non-finite/exponent numbers, source traversal, source digest mismatch, expanded/compiled digest mismatch, unbound macro parameter, duplicate macro/rule revision, wrong rule capability assertion, non-null dependency graph, direct DSL-bound `RuleEngine.build_match` bypass, and absence of filesystem/network/environment/time/random/subprocess imports in the DSL package.

Tests must stay within supported public operations and the approved Python threat model. They do not need to simulate arbitrary memory corruption or hostile monkeypatching of private seals.

## 22. Required future validator

Add `tools/validate_prompt07.py`, following the current validator style. It accepts `--mode focused|full`, records worktree/protected/personal-export signatures before execution, and always compares them afterward.

Focused mode composes:

1. import/smoke gate;
2. `tests/dsl`;
3. `tests/versioning`;
4. focused Prompt‑01 condition/predicate/definition tests;
5. Prompt‑02 RuleMatch tests;
6. Prompt‑03 inference tests;
7. Prompt‑04 AstroState tests;
8. Prompt‑05 domain tests;
9. Prompt‑06 scenario manifest;
10. Prompt‑07 `tests/dsl/scenario_manifest.py` expected digest;
11. subprocess comparisons across hash seeds and alternate CWD;
12. canonical source/DSL/AST/compiled/manifest comparison;
13. current v1 manifest fingerprint and byte digest;
14. protected snapshot size/hash and exact Career/Yoga checks;
15. private tracker exclusion and Prompt‑08 absence.

Full mode additionally runs the complete `tests` and `systems/Parasara/tests` collections, existing rule lint for the untouched legacy corpus, the approved snapshot generator/check, and all Prompt‑01 through Prompt‑06 validator-equivalent gates. The validator runs in both supported Python environments and records one identical Prompt‑07 scenario-manifest SHA only after both lanes match.

The validator is non-mutating. Temporary catalogs, manifests, DSL packs, alternate-CWD files, and generated invalid inputs live only in validator-managed temporary directories. It shall not rewrite expected digests, approve snapshots, update lifecycle state, touch personal exports, or treat pre-existing accepted Prompt‑06 work as a failure.

Do not run this validator during the specification-only session.

## 23. Stop conditions and acceptance gate

Implementation must stop for user decision if:

- any Prompt‑01 through Prompt‑06 public/logical contract must be redefined instead of extended through the identified seam;
- `parashara/v1`, its catalog entry, manifest bytes/fingerprint, rule files, current runtime, Career/Yoga values/order, or approved snapshot must change;
- current astrology meaning, weights, thresholds, evidence, priorities, IDs, revisions, or activation state must change;
- a production astrology rule must be migrated or created to test the compiler;
- a new predicate/operator is required without an approved current rule need;
- Prompt‑08 dependency resolution or cross-rule scheduling is needed;
- deterministic identity needs a network service, current time, environment, CWD, or an unavailable artifact;
- a file outside the exact implementation list in Section 20 is required; or
- compiler failure would need to be represented as astrology evidence or a RuleMatch.

Prompt‑07 is implementation-complete only when:

- `RuleDslCompiler` is the single compiler owner;
- `.yaml` is the single strict authoring format;
- schemas, grammar, AST, predicate typing, macro expansion, limits, canonicalization, and diagnostics match this document;
- compilation lowers to existing `ResolvedRule` and current condition representation;
- the existing `ConditionEvaluator` and `RuleEngine` retain sole evaluation/RuleMatch ownership;
- a sealed Prompt‑06 authority is required before authoritative compilation/evaluation;
- synthetic DSL packs pass all required tests on Python 3.11 and 3.14;
- current v1 and all public compatibility evidence remain exact;
- Prompt‑08 is absent;
- independent review and user acceptance occur; and
- the private tracker remains local and the architecture count is not advanced before acceptance.

## 24. Specification-session worktree record

The specification session began on `main` at exact HEAD `ec6b49a164389aada4e741561d75cb866527e6cf`, with no staged files. The complete relevant tracked/untracked/private set contained 34 files and had pre-session signature:

```text
2b2ded9dcf908a5c48e903f482c5c9ed3854e0ea23025f1e5f94acc8558b07d0
```

This signature is SHA-256 over the branch, HEAD, staged state, and sorted SHA-256 records for all tracked modifications, all non-ignored untracked files, and the private tracker. It records but does not modify the accepted Prompt‑06 cumulative work, predecessor specifications, or four personal exports.

Additional preservation evidence at session start:

```text
Prompt‑06 specification SHA-256:
bb09a93af73c3c6125c70ceb3b74db913b55acc9fec7f63785a3bfdbef6dcc2c

Prompt‑06 v1 manifest file SHA-256:
687c7bb19ce03671882e989db267d588a3c9beace1c42df25390ab643ebae265

.git/info/exclude SHA-256:
7cf3f2dc7f8ba559150be7c20c7a582efd69c4d5d05cbd2bf50cc3aa38166d51

prepared_state.py working-file SHA-256:
a2fca2dd17edd7092e8bee1cc8431891400d09f979a90f4f44d17b71c9466970
```

`git diff` and `git diff --ignore-all-space` showed no logical content difference for `prepared_state.py`; its worktree status is line-ending-only. `.git/info/exclude` contains one project-specific exclusion, `systems/Jyothishyam-Systems-and-Subsystems-Status.md`, and conceals no source, tests, specifications, or other project files. No Prompt‑08 implementation exists.

The accepted, uncommitted Prompt‑06 semantic change set present at session start is:

```text
systems/Parasara/Documentation/Engine/Prompt-06/requirements/Prompt-06-Rule-Versioning.md
systems/Parasara/config/versioning/parashara_rule_sets_v1.json
systems/Parasara/engine/versioning.py
systems/Parasara/rules/parashara/v1/rule-set-manifest.json
systems/Parasara/engine/domain/factories.py
systems/Parasara/engine/enrichments/yoga_engine.py
systems/Parasara/engine/inference/config.py
systems/Parasara/engine/inference/engine.py
systems/Parasara/engine/interpreters/career.py
systems/Parasara/engine/output_assembler.py
systems/Parasara/engine/rules/evaluator.py
systems/Parasara/engine/rules/loader.py
systems/Parasara/engine/rules/rule_engine.py
systems/Parasara/engine/rules/yoga_loader.py
systems/Parasara/tools/generate_snapshot.py
tests/versioning/__init__.py
tests/versioning/conftest.py
tests/versioning/scenario_manifest.py
tests/versioning/test_cache_isolation.py
tests/versioning/test_compatibility_and_scope.py
tests/versioning/test_manifest.py
tests/versioning/test_propagation_authority.py
tests/versioning/test_replay_rollback.py
tests/versioning/test_selection_lifecycle.py
tools/validate_prompt06.py
```

The line-ending-only `prepared_state.py` worktree entry, untracked Prompt‑02/03 documentation, and four personal MVP JSON exports are inherited preserved state, not silently folded into the Prompt‑06 semantic inventory. All remain untouched by this specification session.

---

```text
PROMPT07_SPECIFICATION: COMPLETE
PROMPT07_SPECIFICATION_RECOMMENDED: YES

PROMPT06_ACCEPTANCE_RECORDED: YES
ARCHITECTURE_PROGRESS: 6/10

CANONICAL_AUTHORING_FORMAT_DEFINED: YES
DSL_SCHEMA_DEFINED: YES
TYPED_EXPRESSION_GRAMMAR_DEFINED: YES
IMMUTABLE_AST_DEFINED: YES
PREDICATE_BINDING_DEFINED: YES
MACRO_SYSTEM_BOUNDED: YES
COMPILER_PIPELINE_DEFINED: YES
CANONICALIZATION_DEFINED: YES
DETERMINISTIC_DIAGNOSTICS_DEFINED: YES
RESOURCE_LIMITS_DEFINED: YES
PROMPT06_VERSIONING_INTEGRATION_DEFINED: YES
CURRENT_V1_IMMUTABILITY_PRESERVED: YES
PROMPT08_BOUNDARY_PRESERVED: YES
PUBLIC_COMPATIBILITY_PRESERVED: YES
FUTURE_IMPLEMENTATION_SCOPE_BOUNDED: YES

PREDECESSOR_CONTRACT_CHANGE_REQUIRED: NO
CURRENT_V1_MANIFEST_CHANGE_REQUIRED: NO
PUBLIC_OUTPUT_CHANGE_REQUIRED: NO
ASTROLOGY_SEMANTICS_CHANGE_REQUIRED: NO

READY_FOR_USER_PROMPT07_SPECIFICATION_REVIEW: YES
READY_FOR_PROMPT07_IMPLEMENTATION: NO
READY_FOR_GITHUB_DELIVERY: NO
RECOMMENDED_NEXT_ACTION:
REVIEW AND APPROVE THE PROMPT‑07 RULE DSL SPECIFICATION BEFORE IMPLEMENTATION
```
