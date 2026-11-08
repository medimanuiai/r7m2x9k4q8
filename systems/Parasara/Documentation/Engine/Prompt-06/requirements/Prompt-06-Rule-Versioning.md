# Parāśara — Prompt‑06 Rule Versioning Specification

> **Current Python policy - 2026-11-06:** [Root policy](../../../../../../AGENTS.md) selects Python 3.11.9 only
> for development, tests, and CI and explicitly supersedes every dual-version
> requirement below. Retained Python 3.14 results/commands are historical, not
> current instructions. Run appropriate checks once on the selected runtime;
> keep correctness, regression, end-to-end, and same-runtime determinism checks.
> Missing second-version evidence is never a defect or blocker. Future specs,
> prompts, and handoffs must carry this policy; only an explicit user request
> can reinstate multiple Python versions.

**Document:** `Prompt-06-Rule-Versioning.md`  
**Repository-relative path:** `systems/Parasara/Documentation/Engine/Prompt-06/requirements/Prompt-06-Rule-Versioning.md`  
**Status:** Specification complete; implementation pending  
**Baseline:** `main` at `ec6b49a164389aada4e741561d75cb866527e6cf`  
**Scope:** Prompt‑06 only; specification, not implementation

## 1. Purpose and decision

Prompt‑06 shall add one engine-owned, deterministic rule-versioning boundary to the existing Parāśara evaluation path. A caller selects a concrete rule-set family and version through `EngineConfig`; `RuleVersionResolver` resolves that selection once into an immutable `ResolvedEvaluationVersions` authority containing the canonical `EvaluationVersionManifest`. The same authority is then passed through rule evaluation, inference, domain construction, Yoga construction, trace recording, and output assembly. It cannot be replaced during the run.

This design versions executable meaning without implementing a rule DSL, dependency graph, new astrology content, or a new public output schema. It uses the existing Prompt‑02 identity fields and trace hooks, Prompt‑03 inference ownership, Prompt‑04 immutable snapshot, and Prompt‑05 sealed same-run provenance. No predecessor contract needs to be redefined.

The default compatibility surface shall remain byte-for-byte compatible. Existing callers that do not yet provide `EngineConfig` may use one documented compatibility façade, which resolves the literal immutable selection `parashara/v1` in `EXPERIMENTAL` mode before evaluation begins. It is not an alias, is not “latest,” and does not imply subject-matter approval.

Normative terms **MUST**, **MUST NOT**, **SHALL**, **SHALL NOT**, **SHOULD**, and **MAY** are binding in this specification.

## 2. Governing baseline and constraints

The implementation shall preserve these accepted baselines unless the implementation review explicitly authorizes a deterministic successor manifest for an internal representation:

| Baseline | SHA-256 or identity |
|---|---|
| Branch / commit | `main` / `ec6b49a164389aada4e741561d75cb866527e6cf` |
| Prompt‑02 / WP17 manifest | `06330b43cac062239e0670d1e48ab00c328ee270af64023b2017b819dc7b3017` |
| Prompt‑03 manifest | `f57bc28504988ecf5ccfbf82de4bc495d2e69a91dfd476997cda5c89a563786e` |
| Prompt‑04 manifest | `440a459cc60e9575874341e7c6673e714585ae79123957c9c19ccd175cb7930b` |
| Prompt‑05 manifest | `f6d90db74309127e99d55e17c542214b05bb385b8ec62447c1baef53c393ba92` |
| Approved public snapshot | 4,041 bytes; `da2059ba3cfb92eed267f93d1e41585dac1422d68f685022c8609cfd04ad57af` |
| Supported Python | 3.11 and 3.14 |

Prompt‑06 shall preserve:

- the same normalized input, evaluation instant, engine contract, selected manifest, and output profile producing the same logical result;
- `RuleEngine` as the sole generic `RuleMatch` producer and `InferenceEngine` as the sole aggregation owner;
- the immutable Prompt‑04 `AstroStateSnapshot`; rule selection is bound beside the snapshot, never inserted into factual state;
- the Prompt‑05 Career ledger, Yoga evaluation record, domain factories, and serialization-only `OutputAssembler` authority boundaries;
- neutral insufficient-evidence behavior, missing-inference rejection, Career and Yoga ordering, and the protected public snapshot;
- offline canonical evaluation with no remote rule lookup;
- all historical Prompt‑01 through Prompt‑05 reports unchanged.

The approved execution order remains Prompt‑06, Prompt‑07, Prompt‑08, FWP‑01 through FWP‑05, Prompt‑09, then Prompt‑10. This specification deliberately creates extension slots for Prompt‑07 and Prompt‑08 but assigns no DSL or dependency-graph version yet.

## 3. Repository findings and existing integration points

Repository inspection establishes the following current facts that constrain the implementation.

### 3.1 Existing contracts to extend, not duplicate

- `systems/Parasara/engine/rules/rule_match.py` already carries `system`, `rule_id`, `rule_version`, `rule_family`, `rule_set_version`, canonical metadata/provenance, deterministic trace references, and strict logical serialization. These remain the per-match identity fields.
- `systems/Parasara/engine/rules/rule_engine.py` owns `ResolvedRule`, deterministic `RuleMatch` construction, trace identity, and rule ordering. It is the point at which a manifest-authorized rule becomes evaluated authority.
- `systems/Parasara/engine/rules/registry.py` exposes the frozen production predicate registry and its deterministic fingerprint. Prompt‑06 pins that fingerprint; it does not add a second registry.
- `systems/Parasara/engine/rules/evaluator.py` contains the current bounded predicate LRU and `PredicateCacheKey`. This is the only implemented rule-semantic cache that Prompt‑06 must change.
- `systems/Parasara/engine/rules/definition_validation.py` already computes canonical semantic/source digests and validates the production registry/catalog fingerprints. Prompt‑06 reuses those digest rules.
- `systems/Parasara/engine/inference/config.py` owns immutable `InferenceConfig` and the current module-relative loader; `systems/Parasara/config/inference/career_compat_v1.json` declares `career-compat-1.0.0`. The selected rule-set manifest shall pin both this identity and the file content digest.
- `systems/Parasara/engine/inference/engine.py` rejects mixed rule-set versions, owns contribution ordering and aggregation, and emits `InferenceResult.rule_set_version`, `inference_version`, and `trace_id`. It shall validate the selected authority before aggregating; `InferenceResult` does not need a replacement type.
- `systems/Parasara/engine/interpreters/career.py` currently hard-codes `v1`, creates active materialized rules, owns `_CareerRuleMatchLedger` and `_CareerInferenceEvaluation`, and loads the inference config at import. These private same-run authority objects are the correct place to retain the resolved manifest authority.
- `systems/Parasara/engine/enrichments/yoga_engine.py` currently uses the module-relative `v1/yogas.yaml`, constructs Yoga `ResolvedRule` values, and owns `YogaEvaluationRecord`. That record shall retain the same resolved authority.
- `systems/Parasara/engine/domain/factories.py` already rejects caller-manufactured `DomainPrediction` and `YogaDiagnostic` authority and reconciles them to same-run source records. It shall additionally reconcile their existing version fields to the selected authority.
- `systems/Parasara/engine/output_assembler.py` already validates domain/Yoga values against `EngineMetadata` and emits the protected output profile. It shall validate metadata against the selected authority without serializing new public fields.
- `systems/Parasara/tools/generate_snapshot.py` currently constructs hard-coded engine metadata. It shall create one compatibility `EngineConfig`, resolve it once, and pass the resulting authority to Career, Yoga, and output assembly.

### 3.2 Current selection gaps

There is no canonical `EngineConfig` or rule-set resolver. Career and Yoga independently hard-code `v1`; the Career inference config is loaded at import; the legacy Yoga loader has a working-directory-sensitive default; and the generic loader exposes mutable compatibility registry behavior. These cannot remain production selection mechanisms.

The predicate registry is deterministic and frozen after construction, but its identity is not bound to a complete evaluation manifest. The predicate cache correctly includes predicate, definition, prepared-state, parameter, and relevant-context digests, but it does not yet include the selected predicate/evaluator component fingerprint.

No compiled-rule, rule-evaluation, inference, Dasha, or transit result cache currently exists. Prompt‑06 shall define key requirements for those future caches but shall not create speculative cache implementations.

### 3.3 Current rule corpus

The baseline corpus is `systems/Parasara/rules/parashara/v1/`:

- `m1_rules.yaml`
- `derived_rules.yml`
- `primitives.yml`
- `yogas.yaml`
- `macros.yaml`
- `calibration.json`

The canonical active Career inventory is not every row in those files. It is:

1. `m1_rules.yaml:strong_planet_in_10`, materialized deterministically as `strong_in_10_<planet>` with revision `1.0`;
2. `derived_rules.yml:lord_status_10th`, materialized as `10th_lord_<lord>` with the existing compatibility revision token `legacy-unversioned`;
3. `yogas.yaml:rajayoga_naive`, revision `1`, evaluated for Career and Yoga projections;
4. the synthetic inference baseline `career.base_kendra_strength`, revision `1.0.0`.

The canonical Yoga order is the source order in `yogas.yaml`: `rajayoga_naive`, `dhana_naive`, `arishta_naive`, all revision `1` and all currently marked `sme_approved: false`.

Other seeded, duplicate, dormant, placeholder, and calibration rows are not silently promoted into the executable set. In particular, the `m1_rules.yaml` row also named `rajayoga_naive` is not the active Yoga source and shall be recorded as a non-executable shadowed seed, not copied or treated as a second canonical rule. `macros.yaml` remains a placeholder. Prompt‑06 does not decide their astrology validity.

The current v1 material is seed/compatibility content and lacks astrology-SME approval. Successful parsing, compilation, tests, or technical validation MUST NOT relabel it `PRODUCTION`.

## 4. Singular ownership model

### 4.1 Selection owner

`RuleVersionResolver` is the sole owner of version selection. It is called once at the engine/orchestration boundary, before any rule is loaded or evaluated. No loader, interpreter, evaluator, environment variable, global registry, working directory, or output serializer may select or replace a version.

The resolver returns a factory-sealed, immutable `ResolvedEvaluationVersions`. Its constructor is not a public authority path. It contains:

- the validated `EngineConfig` request;
- the canonical `EvaluationVersionManifest`;
- `manifest_fingerprint_sha256`;
- the selection purpose and lifecycle decision;
- immutable resolved rule, predicate, inference, table, output, and future-component bindings;
- deterministic warnings, if the lifecycle policy permits the selection with a warning.

Only objects carrying the exact same sealed authority may participate in one canonical run. Equality of caller-supplied strings is insufficient to substitute an authority object mid-run.

### 4.2 Version owners

| Entity | Identity and compatibility purpose | Named owner |
|---|---|---|
| Engine implementation | Package/release version plus evaluation-contract version; invalidates code-sensitive replay/cache entries | Parāśara engine release maintainer |
| Rule-set family | Stable namespace such as `parashara`; not itself a semantic version | Architecture owner |
| Rule-set version | Immutable selection unit and membership/order/dependency compatibility boundary | Rule-pack maintainer; production transition additionally requires astrology SME evidence |
| Individual rule identity | Stable `rule_id` within system + rule-set family; connects revisions and trace | Rule-pack maintainer |
| Individual rule revision | Immutable semantic definition revision, paired with a content digest | Rule author/reviewer; astrology changes require SME review evidence |
| Predicate library | Library contract version and registry fingerprint | Predicate subsystem maintainer |
| Condition evaluator | Evaluator contract version and implementation compatibility | Predicate/condition evaluator maintainer |
| Inference configuration | Existing `InferenceConfig.inference_version`, config schema, and content digest | Inference subsystem maintainer |
| Knowledge data | Per-table/bundle version and content digest for rule-affecting tables | Owning enrichment/data maintainer; astrology content requires SME evidence |
| Output schema/profile | Existing schema version and compatibility profile | Output contract owner |
| DSL | Absent in Prompt‑06; future manifest slot owned by Prompt‑07 | Future Prompt‑07 owner |
| Dependency graph | Absent in Prompt‑06; future manifest slot owned by Prompt‑08 | Future Prompt‑08 owner |
| Lifecycle state and approvals | Mutable governance metadata, separate from executable content | Governance/release maintainer with recorded technical and SME approvers |

There is no independent “configuration version” in addition to `InferenceConfig.inference_version`, and no aggregate knowledge version unless it maps to a concrete immutable bundle. A digest never replaces a human-readable owner-controlled version; both are retained where semantic content exists.

## 5. Canonical types and APIs

### 5.1 `EngineConfig`

`EngineConfig` is a frozen, keyword-only value accepted at the top-level evaluation boundary:

```text
EngineConfig
  config_schema_version: "1.0.0"
  system: "parashara"
  engine_version: exact expected engine implementation version
  rule_set_family: exact family
  rule_set_version: exact canonical version; aliases forbidden here
  mode: STRICT | EXPERIMENTAL
  purpose: NEW_EVALUATION | REPLAY | ROLLBACK
  evaluation_instant: normalized explicit instant
  output_schema_version: exact expected schema
  compatibility_profile: exact output profile
```

`EngineConfig` selects only the composed rule set. Predicate, inference, knowledge, evaluator, DSL, and graph identities are pinned by the referenced manifest, preventing callers from assembling unreviewed combinations. The explicit engine and output values are compatibility assertions: resolution fails if the manifest does not match them.

For current callers only, `compatibility_v1_config(evaluation_instant)` returns a fully populated literal config for `parashara/v1`, `EXPERIMENTAL`, `NEW_EVALUATION`, output schema `1.0.0`, and `parasara_snapshot_v1`. This function contains no lookup for “latest,” uses no environment state, and still enters the sole resolver. New production-facing code MUST provide `EngineConfig` explicitly and MUST NOT rely on this façade.

The resolved instant MUST equal the Prompt‑04 snapshot evaluation context when that context is present. A mismatch fails before rule evaluation. The instant does not participate in the content manifest fingerprint; it participates in the run identity and replay record.

### 5.2 Content identity values

The new module defines frozen diagnostic values `RuleRevisionIdentity`, `ComponentIdentity`, `KnowledgeDataIdentity`, and `EvaluationVersionManifest`. These values describe content; constructing one does not authorize evaluation. Authority comes only from the sealed `ResolvedEvaluationVersions` produced by `RuleVersionResolver` after catalog and content verification.

Each `RuleRevisionIdentity` contains:

```text
rule_id
revision
semantic_content_sha256
source_artifact_id
source_artifact_semantic_sha256
source_order
materialization_contract_id | null
materialization_bindings | null
execution_projections
```

Materialized current rules are explicitly enumerated for the supported planet/lord identifiers, or validated against a finite manifest-declared template plus a versioned materialization contract. Runtime values outside that finite authorization fail. A generated rule’s semantic digest covers the canonical source definition, materialization contract, normalized bindings, and resulting resolved semantics.

### 5.3 No replacement result hierarchy

Prompt‑06 shall not create parallel replacements for `RuleMatch`, `InferenceResult`, `DomainPrediction`, or `YogaDiagnostic`.

- A `RuleMatch` references its manifest through its existing system, family, rule-set version, rule identity, and rule revision. `RuleEngine` validates that tuple and the resolved rule content against the sealed authority before constructing the match.
- `InferenceResult` references the same selection through its existing `rule_set_version`, `inference_version`, and deterministic trace record. `InferenceEngine` receives the sealed authority, verifies every input match is an authorized member/revision, and records the manifest fingerprint in the engine-owned evaluation trace bundle.
- `DomainPrediction` already carries engine, rule-set, and inference versions and sealed source inference/batch authority. Its factory verifies those values against the same resolved authority.
- `YogaDiagnostic` already retains its authoritative `RuleMatch` and `YogaEvaluationRecord`; that record retains the resolved authority.
- The full manifest and its fingerprint are retained in an immutable `EvaluationRecord`, which is an audit/replay envelope, not a second inference or domain result. It contains the run identity, normalized input/snapshot reference, resolved authority, deterministic trace bundle, typed results, and output digest.
- Public output continues to expose only the existing engine and rule-set summary. The complete manifest remains internal in Prompt‑06.

Because the authority object is private-factory sealed and downstream factories require same-run source records, a caller-constructed manifest or a copied version string cannot create evaluated authority. The design prevents supported-API relabeling; it does not claim resistance to arbitrary malicious mutation of Python process memory or cryptographic authenticity.

## 6. `EvaluationVersionManifest`

### 6.1 Required content

The immutable manifest contains exactly these logical sections:

```text
manifest_schema_version
system
engine:
  implementation_id
  implementation_version
  evaluation_contract_version
rule_set:
  family
  version
  ordered_rule_revisions[]
  ordered_source_artifacts[]
predicate_library:
  identity
  contract_version
  registry_fingerprint_sha256
condition_evaluator:
  identity
  contract_version
inference:
  inference_version
  config_schema_version
  config_sha256
knowledge_data[]:
  identity
  version
  content_sha256
  compatibility_contract
output:
  schema_version
  compatibility_profile
future_components:
  dsl: null
  dependency_graph: null
```

`ordered_rule_revisions` defines canonical rule membership and order. Rule evaluation may use Prompt‑02 priority ordering where already required, but source/evaluation-plan position remains fixed and diagnostics expose both. `ordered_source_artifacts` uses repository-relative POSIX paths and canonical parsed semantic digests for executable sources. Comments, YAML/JSON formatting, dormant rows, placeholders, and non-authoritative calibration data are recorded in a separate migration-inventory section of the catalog/audit record; they do not enter the evaluation fingerprint or become rule members.

The knowledge list includes only data that can affect the evaluation represented by the manifest. For the current end-to-end compatibility run this includes the applicable `rules/parashara` tables/configuration and `systems/Parasara/enrichment_tables/functional_roles/*.yaml` bundle when raw input is enriched. Code-backed algorithms are identified by the engine/evaluator contract, not mislabeled as data tables. A replay starting from a canonical Prompt‑04 snapshot still retains these identities for provenance, while the snapshot digest binds the already-computed facts.

Lifecycle state, approver names, review dates, warnings, catalog aliases, release notes, and timestamps MUST NOT appear in the content manifest. They belong to the catalog/audit record and may change without changing executable content identity.

### 6.2 Canonical representation and fingerprint

The manifest logical form shall use the repository’s existing canonical JSON machinery. The rules are:

1. UTF‑8, Unicode NFC strings, sorted mapping keys, declared array order, no insignificant whitespace, and no platform paths.
2. No non-finite numbers. Manifest versions and SHA-256 values are strings; timestamps are absent.
3. Repository-relative artifact paths use `/` and are resolved from the module/repository anchor, never the working directory.
4. The fingerprint field itself is excluded from the hashed logical payload. Rule-source digests cover canonical parsed executable semantics rather than comments or presentation formatting.
5. `manifest_fingerprint_sha256 = SHA256(canonical_json_bytes(logical_manifest))`, lowercase hexadecimal.
6. Loading verifies the catalog’s expected file digest, schema, canonical reserialization, component digests, rule membership uniqueness, order, and embedded fingerprint before returning authority.

Identical manifest content MUST yield identical bytes and fingerprint under Python 3.11 and 3.14, Windows and CI. SHA-256 provides deterministic content addressing and diagnostics only; Prompt‑06 makes no signing or authenticity claim.

### 6.3 Immutability

Publishing a manifest makes the pair `(system, family, rule_set_version)` immutable. Changing any executable rule, revision, order, membership, predicate fingerprint, evaluator contract, inference config, relevant knowledge data, engine evaluation contract, or output compatibility binding requires a new rule-set manifest/version. Editing rule-affecting content in place under an existing version causes resolver failure; non-executable comments or authoring presentation do not change semantic identity.

Two manifests may coexist. They are loaded into separate immutable resolved authorities; no mutable process-global “active version” exists.

## 7. Rule-set catalog and selection

### 7.1 Catalog

`systems/Parasara/config/versioning/parashara_rule_sets_v1.json` is the local catalog. Each entry maps an exact family/version to:

- a module-root-relative manifest path and expected manifest-file SHA-256;
- lifecycle state;
- technical validation evidence identifier;
- astrology-SME approval evidence identifier or explicit `null`;
- compatibility/replay availability;
- deprecation/archival warnings;
- allowed selection purposes and modes.

The catalog is deterministic local configuration, not a network registry. Lifecycle metadata is mutable only through review, but catalog entry order and canonical bytes are deterministic. The resolver reads it through an explicit module-root path. A test catalog may be injected only by a test-only resolver constructor and must undergo identical schema/digest checks.

### 7.2 Resolution algorithm

For every run, the resolver shall:

1. Validate `EngineConfig` and reject missing/empty/alias values.
2. Locate exactly one catalog entry by `(system, family, version)`.
3. Enforce lifecycle policy for `mode` and `purpose`.
4. Load the exact manifest path anchored to the package/repository, verify its expected file digest, and canonicalize it.
5. Verify every referenced local artifact and component digest before any rule evaluation.
6. Verify engine, output, predicate registry, evaluator, inference, and knowledge compatibility.
7. Freeze the manifest and all resolved bindings.
8. Reconcile the explicit evaluation instant to the Prompt‑04 snapshot context.
9. Return one sealed `ResolvedEvaluationVersions` and deterministic warnings.

Unknown, unavailable, digest-mismatched, incompatible, non-canonical, or policy-disallowed selections fail with typed deterministic error codes before evaluation. Required codes include `UNKNOWN_RULE_SET_VERSION`, `RULE_SET_UNAVAILABLE`, `MANIFEST_DIGEST_MISMATCH`, `CONTENT_DIGEST_MISMATCH`, `INCOMPATIBLE_COMPONENT_VERSION`, `LIFECYCLE_SELECTION_FORBIDDEN`, `EVALUATION_INSTANT_MISMATCH`, and `HISTORICAL_CONTENT_UNAVAILABLE`.

### 7.3 Binding and supported call paths

Production selection occurs only through `EngineConfig` at the engine/orchestration boundary. The resolved authority is passed keyword-only into the existing stages. It is never accepted as independent version strings at lower layers.

- `RuleEngine` is constructed/bound with the resolved authority; per-call version selection is prohibited.
- Career and Yoga entry points accept an `EngineConfig` or an already resolved same-run authority from the top-level orchestrator. If a public compatibility call omits config, it calls `compatibility_v1_config(...)` and the same resolver exactly once.
- `InferenceEngine.aggregate` receives the authority and the manifest-pinned `InferenceConfig`; an independently loaded config is rejected.
- Domain and Yoga factories receive private evaluation records that already hold the authority.
- `OutputAssembler` receives the authority and validates `EngineMetadata` and every typed input against it. It remains serialization-only.

The resolver shall not mutate `RULE_REGISTRY`, infer a version from directory enumeration, use current time for selection, consult environment variables, resolve a “latest” alias during evaluation, or depend on import order. Administrative aliases, if ever added after Prompt‑06, must resolve to an exact version before `EngineConfig` is created and the canonical version must be recorded; aliases are never valid manifest identities.

Mid-run replacement is prevented structurally: each bound engine/evaluation record retains the sealed authority, and APIs reject a different authority even when strings happen to match. A result may be replayed or serialized; it may not be rebound to another manifest.

## 8. Lifecycle governance

The existing Master Architecture vocabulary is normative:

```text
DRAFT → REVIEWED → VALIDATED → PRODUCTION → DEPRECATED → ARCHIVED
```

`VALIDATED` means technical validation only. `PRODUCTION` additionally requires recorded astrology-content approval for every astrology-semantic rule/table change and compatible production predicates/configuration. No state name itself proves scholarship or correctness.

| State | Ordinary new experimental evaluation | Ordinary new strict production evaluation | Replay | Rollback use | Result |
|---|---:|---:|---:|---:|---|
| `DRAFT` | Yes, exact explicit selection | No | Yes if retained | No | Internal experimental marker |
| `REVIEWED` | Yes | No | Yes if retained | No | Internal experimental marker |
| `VALIDATED` | Yes | No | Yes | No | Internal experimental marker |
| `PRODUCTION` | Yes | Yes | Yes | Yes | No warning unless separately configured |
| `DEPRECATED` | Yes with deterministic warning | No ordinary new strict run | Yes | Yes only with explicit `ROLLBACK` purpose and recorded operator authorization; warning required | Deprecation warning retained in audit record |
| `ARCHIVED` | No | No | Yes only when executable artifacts are retained | No | New evaluation fails; replay is labeled historical |

“Retired” in acceptance criteria is implemented as `ARCHIVED`; no second synonym is stored.

Selection is requested by an application/operator, but the resolver—not the caller—decides whether policy permits it. Only governance maintainers may change catalog state. Required transitions are monotonic. A correction to executable content creates a new rule-set version rather than moving backward or editing an old manifest. Emergency withdrawal may move any non-archived state directly to `DEPRECATED` or `ARCHIVED`, with a reason. Reactivating archived content for new production is not an in-place reversal: it requires a new reviewed catalog/version decision and full gates.

Transition gates:

- `DRAFT → REVIEWED`: author metadata, source/reason, affected rules/components, semantic diff, and proposed tests exist.
- `REVIEWED → VALIDATED`: dual-Python deterministic tests, manifests, compatibility tests, and technical review pass.
- `VALIDATED → PRODUCTION`: astrology-SME approval evidence exists for content/meaning, technical approval remains valid, output compatibility is classified, and the release-compatible combination is complete.
- `PRODUCTION → DEPRECATED`: replacement/withdrawal reason and rollback consequences recorded.
- `DEPRECATED → ARCHIVED`: executable artifacts remain available for replay or the loss is explicitly recorded; no new evaluation is permitted.

A lifecycle-only catalog change does not alter manifest/content fingerprints and does not invalidate semantic caches. It does alter the selection audit record.

The initial `parashara/v1` entry shall be `VALIDATED`, `astrology_sme_approved: false`, selectable explicitly in `EXPERIMENTAL`, and used by the literal compatibility façade. It MUST NOT be presented as `PRODUCTION` merely to satisfy a production-selection test. Tests for `PRODUCTION` use a synthetic, non-astrology fixture catalog with explicit test approval evidence.

## 9. Compatibility and change classification

Every proposed change must be classified before editing. Semantic identity follows executable effect, not file extension or author intent.

| Change | Required version action |
|---|---|
| Text/comments/authoring documentation not loaded or emitted | No rule revision and no rule-set version. Documentation evidence may change. |
| Rule label not used by evaluation, evidence, narrative, trace, or public output | No semantic revision; lifecycle/admin metadata only. |
| Rule label used in any logical/internal/public result | New individual rule revision and new rule-set version; output schema changes only if the public field contract changes, not merely its value. |
| Predicate logic/parameter semantics/capability interpretation | New predicate version/evaluator contract as applicable, new predicate registry fingerprint, and a new rule-set version. Revise consuming rules only if their declared condition/meaning changes. |
| Threshold stored in a rule | New rule revision and rule-set version. |
| Threshold stored in a knowledge/config table | New table/config version and new rule-set version; no artificial predicate version unless predicate logic also changes. |
| Rule base weight or priority | New rule revision and rule-set version. |
| Inference override, multiplier, rounding, normalization, aggregation, confidence, or conflict policy | New `inference_version`, new config digest, and new rule-set version. Change engine evaluation-contract version too when code—not data—implements the semantic change. |
| Evidence field shape only | New owning internal schema/contract version and rule-set version when replay/trace interpretation changes. |
| Evidence computation that can change match, quality, contribution, or narrative | New owning predicate/rule/inference revision(s) and rule-set version. |
| Rule ordering or evaluation-plan position | New affected rule revision when priority/order is rule data, and always a new rule-set version when canonical membership order changes. |
| Rule added/removed/enabled/disabled | New rule-set version; new/changed members carry their own revisions. A lifecycle state is not an enable switch. |
| Astrology lookup table value/membership | New table version/content digest and rule-set version, plus astrology-SME review. Predicate revision only if lookup semantics change. |
| Serialization field added/removed/renamed/type-changed internally | New owning schema version. Add a new public output schema/profile only if the protected public surface changes. |
| Backward-compatible serializer implementation with identical canonical bytes | Engine patch version as appropriate; no rule revision or output-schema change. |
| Future DSL syntax/schema or compilation semantics | Prompt‑07 DSL version plus new affected rule-set version; outside Prompt‑06. |
| Future dependency graph schema/planning semantics | Prompt‑08 graph version plus new affected rule-set version; outside Prompt‑06. |

Any change that can alter match truth, evidence, base weight, contribution, order, score, confidence, narrative choice, or astrology lookup is semantic and cannot be hidden in metadata, a patch comment, a lifecycle transition, or an unchanged version.

Every semantic version proposal shall retain: source and reason; old/new manifest fingerprints; machine-readable diff; affected rules/components; golden/snapshot impact; migration statement; technical reviewer; astrology-SME decision when applicable; and output-schema decision.

Prompt‑06 does not mandate SemVer syntax for legacy rule tokens. It mandates immutable, nonempty, exact tokens. New independently owned engine, predicate, inference, schema, and rule revisions SHOULD use SemVer. Current tokens `v1`, `1.0`, `1`, and `legacy-unversioned` are frozen compatibility identities; they are not normalized in place.

## 10. Traceability and anti-relabeling

For every supported evaluation the internal `EvaluationRecord` shall answer:

- exact system, rule-set family/version, manifest fingerprint, lifecycle decision, mode, purpose, and evaluation instant;
- engine implementation and evaluation-contract versions;
- ordered evaluated rule IDs, revisions, source positions, content digests, and resulting `RuleMatch.trace_id` values;
- predicate library version/fingerprint and condition evaluator contract;
- inference version/config schema/config digest;
- applicable knowledge-data versions/digests;
- output schema/profile and final logical/public output digest;
- deterministic warnings/errors and replay provenance.

The existing object propagation remains:

```text
EngineConfig
  → RuleVersionResolver
  → sealed ResolvedEvaluationVersions + EvaluationVersionManifest
  → RuleEngine / CareerEvaluationBatch / YogaEvaluationRecord
  → RuleMatch identity fields
  → InferenceEngine + InferenceResult version fields
  → Prompt‑05 private evaluation authority
  → DomainPrediction / YogaDiagnostic existing version fields
  → OutputAssembler validation
  → unchanged public compatibility projection
```

Before aggregation, `InferenceEngine` verifies that every match’s `(system, rule_set_version, rule_id, rule_version)` is a member of the selected manifest, that ordering satisfies the existing Prompt‑02 contract, and that the private ledger/evaluation record is bound to the same authority. Mixed manifests or relabeled versions fail; they are not converted to neutral evidence.

Before domain construction, the factories verify the `InferenceResult` versions and trace membership against the authority. Before Yoga construction, the factory continues exact `RuleMatch` reconciliation and also verifies the record’s authority. Before serialization, `OutputAssembler` verifies `EngineMetadata`, all domains, and all Yogas against the authority. These checks use supported engine provenance and do not attempt to defend against arbitrary hostile code executing inside the process.

## 11. Public-output compatibility

Prompt‑06 requires **no public-output change**.

The existing `parasara_snapshot_v1` shape, field order, Yoga order, Career values, engine metadata fields, schema version, and 4,041-byte approved snapshot remain exact. No manifest fingerprint, lifecycle state, approval field, component digest, warning, DSL field, or graph field is silently added.

Full Prompt‑06 version detail is internal trace/audit data. A future consumer may receive it only through a separately requested internal diagnostic operation or a future explicitly versioned public output schema. Prompt‑06 does not define that public schema.

The existing public `engine_version` and `rule_set_version` values remain the compatibility summary. The assembler validates them against the resolved authority; it does not allow them to select or relabel authority.

## 12. Cache isolation

### 12.1 Current cache

`PredicateEvaluator`’s instance-owned LRU remains bounded and non-global. `PredicateCacheKey` shall add `predicate_component_fingerprint_sha256`, computed from the selected predicate-library identity/version/registry fingerprint, condition-evaluator contract, and incompatible engine/preparation contract versions. It shall not use the whole evaluation manifest.

The existing key parts—system scope, predicate ID/version, definition digest, normalized parameters, prepared-state digest, context relevance, and relevant-context digest—remain. Consequently a rule weight or lifecycle-only change does not flush factual predicate results, while changed predicate/evaluator semantics cannot collide.

An evaluator instance is bound to one resolved authority or uses the full new key. Mid-run rebinding is prohibited. Cache-hit and cache-miss results remain logically equal and deterministic.

### 12.2 Required keys for future caches

Prompt‑06 defines, but does not implement, these contracts:

| Cache | Required semantic identity in addition to input/context |
|---|---|
| Normalization / `AstroState` | normalization/producer contract, input digest, relevant knowledge-data digests |
| Enrichment / prepared state | snapshot/input digest, enrichment contract, exact table/component digests |
| Compiled rule plan | rule-set content fingerprint, ordered rule revisions/content digests, predicate/evaluator fingerprint, and future DSL/graph identities when present |
| Rule evaluation | snapshot digest, relevant context/instant, exact rule ID/revision/content digest, predicate/evaluator fingerprint |
| Inference | ordered logical `RuleMatch` digests, inference version/config digest, domain, completeness/timing identity, incompatible engine contract |
| Dasha / transit | snapshot digest, evaluation instant/range, algorithm version, and applicable table/config digests |
| Final evaluation/output | manifest fingerprint, normalized input/snapshot digest, instant, output schema/profile, engine contract |

Lifecycle state, approver identity, warning text, and catalog timestamps MUST NOT be semantic cache keys. A manifest/content, engine-contract, schema, predicate, table, inference, future DSL, or future graph incompatibility MUST prevent reuse of affected values.

Cross-version isolation is tested with two intentionally different synthetic manifests evaluated in one process in both orders, using the same input and shared eligible cache instance. Each result must match its cold-cache result; keys and cache statistics must show no cross-version hit.

## 13. Deterministic replay, comparison, and rollback

### 13.1 Minimum replay record

A replayable `EvaluationRecord` shall retain or content-address all of:

1. canonical normalized input, or canonical Prompt‑04 snapshot bytes plus snapshot digest and capability data;
2. evaluation instant/context;
3. canonical `EvaluationVersionManifest` bytes and fingerprint;
4. exact immutable canonical executable rule definitions and their verified semantic digests, including materialization contract/bindings; original authoring bytes may also be retained for audit but are not required when canonical semantics are complete;
5. predicate registry/evaluator artifact compatible with the pinned identity;
6. inference config bytes and digest;
7. relevant knowledge-data bytes and digests when replay begins before snapshot creation;
8. compatible engine artifact/version and evaluation contract;
9. output schema/profile;
10. mode, purpose, deterministic warnings, and expected logical/public output digests.

Repository paths are locators, not identity; content digests are verified. Replay performs a fresh evaluation with `purpose=REPLAY`, the exact canonical version, exact instant, and retained local artifacts. It never selects by lifecycle default or “latest,” never downloads content, never mutates the old record, and never changes an old result’s labels.

Old rule packs remain immutable and executable for replay while their compatible engine artifacts are retained. `ARCHIVED` means replay-only, not migration-only. If exact content is missing, fail `HISTORICAL_CONTENT_UNAVAILABLE`. If content exists but the compatible engine/runtime cannot execute it, fail `INCOMPATIBLE_REPLAY_ENVIRONMENT`. Neither failure falls back to a nearby version.

### 13.2 Version comparison

`compare_manifests(old, new)` is a pure diagnostic operation over canonical manifests. Its deterministic output reports added/removed/changed/reordered rules, old/new revisions and content digests, predicate/evaluator changes, inference config changes, knowledge-data changes, engine/output compatibility changes, and future component changes. It makes no automatic claim that an astrology change is correct or equivalent.

### 13.3 Rollback

Rollback is an explicit new evaluation configuration, never mutation of emitted results:

1. choose an exact earlier `PRODUCTION` version, or a `DEPRECATED` version with `purpose=ROLLBACK` and recorded operator authorization;
2. verify the complete compatible combination—engine, pack, predicates, evaluator, inference config, tables, schemas, and output profile;
3. run the full dual-Python deterministic and protected-output gates;
4. update the deployment/configuration pin atomically outside an in-flight run;
5. retain both old and rollback evaluation records and record the reason.

`ARCHIVED`, unavailable, digest-mismatched, unapproved, or component-incompatible versions cannot be rollback targets. Rollback criteria are: current selected version produces a verified determinism, compatibility, astrology-correctness, or governing-contract blocker; a compatible earlier approved artifact exists; and its gates pass. A rollback never edits catalog content identity, old manifests, or historical output.

## 14. Finite v1 migration

Prompt‑06 migration is an inventory-and-binding operation, not an astrology rewrite.

1. Create one v1 manifest that references the existing corpus; do not copy rules to a second directory.
2. Hash and classify every v1 source artifact as executable, source-for-materialization, dormant seed, shadowed duplicate, placeholder, or non-authoritative calibration data.
3. Preserve active emitted rule IDs, revisions, priorities, source/evaluation order, weights, conditions, and inference behavior exactly.
4. Enumerate/authorize `strong_in_10_<planet>` at revision `1.0`, `10th_lord_<lord>` at frozen revision `legacy-unversioned`, `rajayoga_naive` at revision `1`, and `career.base_kendra_strength` at revision `1.0.0`. Retaining `legacy-unversioned` as an exact immutable baseline token preserves Prompt‑02/05 output; the next semantic change receives a new proper revision.
5. Authorize `dhana_naive@1` and `arishta_naive@1` for the existing Yoga evaluation in source order. Treat Career and Yoga uses of `rajayoga_naive@1` as projections of the same source rule, while preserving their existing RuleMatch family/domain compatibility fields.
6. Record the inactive `m1_rules.yaml:rajayoga_naive@1.0` row and all other inactive rows without making them executable. Resolve future duplicate semantics only in governed rule-library work, not Prompt‑06.
7. Pin `career-compat-1.0.0` and its exact config digest, the production predicate registry fingerprint, current evaluator contracts, relevant current table/config versions and digests, engine `0.1.0` compatibility identity, output schema `1.0.0`, and `parasara_snapshot_v1`.
8. Add the v1 catalog entry as `VALIDATED`, technically validated, `astrology_sme_approved: false`, experimental/compatibility-selectable, and replayable.
9. Route Career, Yoga, inference, and snapshot generation through one resolved v1 authority. Remove import-time/CWD/mutable-global selection behavior from canonical paths; retain bounded legacy inspection APIs only where existing tests require them.
10. Prove exact Career, Yoga, order, predecessor semantics, and public snapshot compatibility on Python 3.11 and 3.14.

No rule is promoted because it parses, compiles, matches a fixture, or passes software tests. Prompt‑07 may later encode the same governed identities in a DSL; FWP‑03 later governs the MVP astrology library.

## 15. Error and compatibility rules

Resolution and binding failures occur before evaluation and are non-neutral. They are configuration/governance errors, not missing astrology evidence. At minimum:

- unknown/forbidden/unavailable selections raise typed versioning errors;
- content or manifest digest mismatch is fatal;
- mixed authorities, rule sets, or inference configurations are fatal;
- caller version strings that disagree with authority are fatal;
- a rule absent from the selected manifest or carrying the wrong revision is fatal;
- absence of historical content is explicit and never substituted;
- ordinary predicate missing-capability behavior remains the Prompt‑01/02 typed result behavior after a valid selection;
- ordinary no-match inference remains Prompt‑03 neutral `0.5` score / `0.0` confidence behavior;
- missing inference remains rejected by Prompt‑05 domain construction.

The compatibility façade is a migration aid, not a second selector. Its literal config and expected manifest fingerprint are tested. Changing what it resolves requires a deliberate API/config change and new compatibility evidence; it never follows catalog order.

## 16. Required acceptance tests

All tests use supported public operations or test-only resolver fixtures. They do not require cryptographic signing or arbitrary in-process attacker defenses.

1. **Approved selection:** a synthetic `PRODUCTION` catalog entry with technical and SME test evidence resolves in `STRICT/NEW_EVALUATION` and produces the expected fingerprint.
2. **Unknown rejection:** an absent family/version raises `UNKNOWN_RULE_SET_VERSION` before loader/evaluator invocation.
3. **Retired rejection:** `ARCHIVED` selected for `NEW_EVALUATION` raises `LIFECYCLE_SELECTION_FORBIDDEN` with no partial result.
4. **Historical replay:** an exact retained `PRODUCTION`, `DEPRECATED`, and `ARCHIVED` fixture can resolve for `REPLAY`; output equals its recorded digest.
5. **Cross-Python fingerprint:** v1 and synthetic manifest canonical bytes/fingerprints are identical under Python 3.11 and 3.14 and in subprocesses with varied hash seeds and CWDs.
6. **Same input/version determinism:** repeated cold/warm and subprocess evaluations with the same snapshot, instant, and manifest are logically identical.
7. **Two-version coexistence:** two intentionally different synthetic packs run in both orders in one process and retain their own results/authorities.
8. **Cache isolation:** shared eligible predicate cache cannot return a result created under an incompatible predicate/evaluator fingerprint; each warm result equals its cold reference.
9. **No mid-run replacement:** passing a different resolved authority to any later stage is rejected before that stage produces output.
10. **No caller relabeling:** copying a supported value and changing rule-set/revision/engine/inference labels cannot pass RuleEngine, inference, domain/Yoga factory, or assembler reconciliation.
11. **Exact rule revision trace:** every active v1 `RuleMatch` resolves to one manifest member and expected semantic/source digest; materialized bindings are exact.
12. **Ordering:** v1 Career Prompt‑02 ordering and `rajayoga_naive`, `dhana_naive`, `arishta_naive` Yoga source order are unchanged.
13. **Career exactness:** existing Career characterization, typed bridge, inference integration, and domain tests are unchanged in public/logical behavior.
14. **Yoga exactness:** existing Yoga output, diagnostics, authoritative RuleMatch reconciliation, and order remain exact.
15. **Snapshot exactness:** protected output is exactly 4,041 bytes and retains SHA-256 `da2059ba3cfb92eed267f93d1e41585dac1422d68f685022c8609cfd04ad57af`.
16. **Predecessor gates:** current Prompt‑02/03/04/05 manifests remain exact. If and only if an internal trace representation unavoidably changes, implementation review must document and authorize one deterministic successor while all predecessor contract tests and public bytes remain exact; no silent hash update is permitted.
17. **No hidden selection:** AST/behavior tests reject `latest`, environment-controlled selection, CWD-dependent canonical loads, directory-order selection, import-time selection, and mutable process-global active versions.
18. **No Prompt‑07:** file/import/AST inventory proves no DSL parser/compiler/schema or dependency graph implementation was added.
19. **No astrology changes:** the v1 source artifact hashes, resolved rule semantics, weights, order, table values, Career/Yoga goldens, and SME flags are unchanged except for the new external manifest/catalog files.
20. **Private tracker:** after each implementation milestone, validator/read-only checks confirm `systems/Jyothishyam-Systems-and-Subsystems-Status.md` contains the truthful required stage, is absent from `git ls-files`, is unstaged, and is excluded from any commit/PR manifest.
21. **Content/lifecycle separation:** changing only a synthetic catalog lifecycle state leaves the manifest and semantic cache fingerprints unchanged but changes the selection decision.
22. **Digest enforcement:** in-place changes to a manifest, rule source, predicate fingerprint, inference config, or table fail before evaluation.
23. **Alias/default discipline:** the compatibility façade always resolves literal `parashara/v1`; no catalog reordering changes it.
24. **Replay failure:** missing exact historical content fails `HISTORICAL_CONTENT_UNAVAILABLE` without fallback.
25. **Rollback policy:** exact Production succeeds; Deprecated requires `ROLLBACK` and records a warning; Archived and unapproved targets fail.
26. **Semantic diff:** two fixture manifests produce stable, complete, ordered diff output.

## 17. Bounded implementation plan

### 17.1 Required types and ownership

Add to `systems/Parasara/engine/versioning.py`:

- `EngineMode`, `SelectionPurpose`, `RulePackLifecycle` enums;
- frozen `EngineConfig`;
- frozen diagnostic `RuleRevisionIdentity`, `ComponentIdentity`, `KnowledgeDataIdentity`, and `EvaluationVersionManifest`;
- private-factory-sealed `ResolvedEvaluationVersions`;
- immutable `EvaluationRecord` and versioning error values/codes;
- sole `RuleVersionResolver`;
- canonical manifest loader/fingerprint, component verification, lifecycle policy, and pure `compare_manifests`;
- literal `compatibility_v1_config(evaluation_instant)`.

No other module may resolve a version. Existing result classes are preserved.

### 17.2 Exact production/configuration files expected to change or be added

Add:

```text
systems/Parasara/engine/versioning.py
systems/Parasara/config/versioning/parashara_rule_sets_v1.json
systems/Parasara/rules/parashara/v1/rule-set-manifest.json
tools/validate_prompt06.py
```

Modify only these existing production/tool files:

```text
systems/Parasara/engine/rules/rule_engine.py
systems/Parasara/engine/rules/evaluator.py
systems/Parasara/engine/rules/loader.py
systems/Parasara/engine/rules/yoga_loader.py
systems/Parasara/engine/inference/config.py
systems/Parasara/engine/inference/engine.py
systems/Parasara/engine/interpreters/career.py
systems/Parasara/engine/enrichments/yoga_engine.py
systems/Parasara/engine/domain/factories.py
systems/Parasara/engine/output_assembler.py
systems/Parasara/tools/generate_snapshot.py
```

Purpose of modifications:

- bind/verify `ResolvedRule` and `RuleMatch` membership in `rule_engine.py` without changing `RuleMatch` schema;
- add the predicate component fingerprint to the existing cache key in `evaluator.py`;
- restrict legacy loaders to explicit, module-root-anchored, manifest-authorized content and remove CWD/mutable active-selection behavior;
- require the manifest-pinned inference config/digest and authority in inference;
- resolve/pass one authority through Career/Yoga private same-run records and factories;
- validate, but do not serialize, the authority at output assembly;
- create one v1 authority in snapshot generation.

No edits are prescribed for `rule_match.py`, `inference/models.py`, `domain/models.py`, `astrostate_api.py`, rule source files, astrology table values, public schema files, or snapshots. If implementation evidence shows one is unavoidable, implementation stops and returns for user approval because that would exceed this specification’s locked boundary.

### 17.3 Exact test files expected to be added

```text
tests/versioning/__init__.py
tests/versioning/conftest.py
tests/versioning/scenario_manifest.py
tests/versioning/test_manifest.py
tests/versioning/test_selection_lifecycle.py
tests/versioning/test_propagation_authority.py
tests/versioning/test_replay_rollback.py
tests/versioning/test_cache_isolation.py
tests/versioning/test_compatibility_and_scope.py
```

Modify only these existing tests where the new explicit authority argument or cache-key assertion is necessary:

```text
tests/rules/test_rule_match_contract.py
tests/rules/test_rule_match_integrations.py
tests/rules/test_predicate_evaluator_cache.py
tests/inference/test_inference_engine.py
tests/inference/test_career_inference_integration.py
tests/domain/test_career_yoga.py
tests/domain/test_output_assembler.py
tests/domain/test_yoga_contract_reconciliation.py
tests/determinism_test.py
```

Existing fixtures, snapshots, rule YAML/YML, inference JSON values, and Prompt‑01–05 historical reports remain unchanged. Tests needing alternate versions build synthetic non-astrology manifests in temporary directories; they do not add a second production corpus.

### 17.4 Existing APIs

- **Extend:** Career/Yoga top-level calls, `RuleEngine`, `PredicateEvaluator`, `InferenceEngine.aggregate`, domain/Yoga factory internal producer methods, and `OutputAssembler` with a keyword-only resolved authority.
- **Restrict:** lower-layer version strings, independently loaded inference configs, CWD Yoga defaults, mutable global active-pack selection, and loaders acting as selection owners.
- **Preserve:** current public compatibility call signatures through the literal v1 façade; all existing model schemas, logical serializers, ordering contracts, neutral semantics, and public output.
- **Do not add:** a second rule engine, inference engine, registry, result hierarchy, AstroState rule fields, DSL compiler, graph planner, plugin API, or network fetcher.

### 17.5 Validation commands

From repository root, implementation validation shall run in clean isolated Python 3.11 and 3.14 environments:

```powershell
py -3.11 tools/validate_prompt06.py --mode focused
py -3.14 tools/validate_prompt06.py --mode focused
py -3.11 tools/validate_prompt06.py --mode full
py -3.14 tools/validate_prompt06.py --mode full
```

`validate_prompt06.py` shall compose the Prompt‑01/WP17 and Prompt‑02 through Prompt‑05 validators, execute `tests/versioning`, full repository tests, rule lint, subprocess/hash-seed/CWD checks, protected manifest/snapshot checks, no-mutation checks, and the private tracker exclusion check. It records the Prompt‑06 scenario manifest SHA only after both Python versions produce identical bytes. It must compare worktree/protected signatures before and after validation and tolerate only pre-existing user changes without modifying them.

### 17.6 Documentation and private status tracker

The only required tracked Prompt‑06 document is this specification at its intended governed path. Existing canonical architecture/current-state documentation is updated only if the completed implementation would otherwise make a specific statement false; no broad cleanup or historical report edits are authorized. No remediation, review, migration, Prompt‑07, release, or FWP document is created by default.

The private local file `systems/Jyothishyam-Systems-and-Subsystems-Status.md` is mandatory but MUST remain untracked, unstaged, uncommitted, unpushed, absent from PRs, and absent from GitHub. The implementation workflow updates it truthfully:

```text
Specification complete:
Prompt‑06 specification approved; implementation pending.

Implementation validated:
Prompt‑06 implementation validated; independent review pending.

Accepted:
6/10 architecture prompts accepted; Prompt‑06 complete; Prompt‑07 not started.
```

The accepted line is written only after independent review acceptance and user acceptance—not merely after code/tests pass. Existing subsystem assessments are preserved unless verified evidence requires a change.

### 17.7 Independent review and stop conditions

After deterministic validation, one independent review shall verify version ownership, lifecycle/content separation, manifest canonicalization, supported-API authority, cache isolation, migration completeness, predecessor/public compatibility, astrology-content non-change, and exclusion compliance. Do not create an R1/R2/R3 chain unless that review finds a genuine blocker in determinism, compatibility, astrology correctness, or a governing predecessor contract.

Implementation must stop for user decision if:

- a Prompt‑02–05 contract must be redefined rather than used through an existing extension point;
- protected public bytes/schema/order cannot remain exact;
- current astrology rule/table meaning must change;
- the v1 corpus cannot be uniquely inventoried without renaming a protected identity;
- deterministic replay requires unavailable content or a network dependency;
- implementation needs files outside the locked list above;
- Prompt‑07 DSL or Prompt‑08 graph work becomes necessary.

## 18. Explicit exclusions

Prompt‑06 shall not implement or authorize:

- Prompt‑07 rule DSL or compilation;
- Prompt‑08 dependency graph;
- new astrology rules, weights, Yogas, Doshas, thresholds, tables, or SME claims;
- Vimshottari integration, transit computation, or new interpretation domains;
- FWP‑01 through FWP‑05;
- public API endpoints or iPhone functionality;
- Prompt‑09 architecture certification or Prompt‑10 release certification;
- public output fields/schema changes;
- cryptographic signing, remote rule downloads, network registries, or plugin architecture;
- broad refactoring, documentation cleanup, historical report edits, snapshot rewrites, or corpus duplication;
- a branch, commit, push, PR, merge, release, or separate documentation PR during specification work.

GitHub delivery of this functional map/specification and cumulative implementation remains deferred to the final governed delivery associated with Prompt‑10.

## 19. Acceptance and handoff

Prompt‑06 implementation is accepted only when all required tests pass on Python 3.11 and 3.14, the independent review accepts it, the user accepts it, the private tracker is truthfully updated and remains untracked, no astrology meaning or protected public output changed, and Prompt‑07 remains unstarted.

The intended workflow is:

```text
Specification
→ One user review
→ Bounded VS Code implementation
→ Deterministic validation
→ One independent review
→ Local status update
→ Prompt‑07
```

GitHub delivery remains deferred.

---

```text
PROMPT06_SPECIFICATION: COMPLETE
SPECIFICATION_RECOMMENDED: YES

VERSION_OWNERSHIP_DEFINED: YES
CANONICAL_VERSION_MANIFEST_DEFINED: YES
RULESET_SELECTION_DEFINED: YES
LIFECYCLE_GOVERNANCE_DEFINED: YES
CHANGE_CLASSIFICATION_DEFINED: YES
DETERMINISTIC_REPLAY_DEFINED: YES
ROLLBACK_DEFINED: YES
CACHE_ISOLATION_DEFINED: YES
TRACE_PROPAGATION_DEFINED: YES
LEGACY_MIGRATION_DEFINED: YES
PUBLIC_COMPATIBILITY_PRESERVED: YES
IMPLEMENTATION_SCOPE_BOUNDED: YES

PREDECESSOR_CONTRACT_CHANGE_REQUIRED: NO
PUBLIC_OUTPUT_CHANGE_REQUIRED: NO
ASTROLOGY_SEMANTICS_CHANGE_REQUIRED: NO
PROMPT07_STARTED: NO

REQUIRED_DOCUMENT_CREATED:
Prompt-06-Rule-Versioning.md
OTHER_DOCUMENTS_CREATED: NONE
REPOSITORY_FILES_MODIFIED:
ADDED LOCALLY (UNTRACKED, UNSTAGED): systems/Parasara/Documentation/Engine/Prompt-06/requirements/Prompt-06-Rule-Versioning.md
UPDATED PRIVATE LOCAL (UNTRACKED, UNSTAGED): systems/Jyothishyam-Systems-and-Subsystems-Status.md
GITHUB_WRITES_PERFORMED: NO

PRIVATE_STATUS_UPDATE_REQUIRED_DURING_IMPLEMENTATION: YES
PRIVATE_STATUS_FILE_MUST_REMAIN_UNTRACKED: YES
FUNCTIONAL_MAP_GITHUB_DELIVERY_DEFERRED: YES
CUMULATIVE_GITHUB_DELIVERY_DEFERRED_TO_PROMPT10: YES

READY_FOR_USER_SPECIFICATION_REVIEW: YES
READY_FOR_PROMPT06_IMPLEMENTATION: NO
RECOMMENDED_NEXT_ACTION:
REVIEW AND APPROVE THE PROMPT-06 RULE VERSIONING SPECIFICATION
```
