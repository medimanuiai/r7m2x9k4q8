# Prompt-05 repository discovery

Status: COMPLETE — IMPLEMENTATION FILES NOT YET MODIFIED  
Authority: Prompt-05 — Typed Domain Models  
Starting commit: `c719a1bf686e1e37eb8542f9323fc279b670250e`  
Branch: `main`  
Discovery date: 2026-08-21

## Gate result

- Local `main`, `origin/main`, and the authorized starting commit are identical.
- The worktree has no tracked content change. `prepared_state.py` is reported by
  Git because of mixed line-ending/stat metadata, but its filtered worktree
  blob is exactly the `HEAD` blob (`e348e503ef84003ea76c6050fd6b821ac16ee4c2`)
  and `git diff` is empty. It will not be touched.
- Existing untracked Prompt-02/03 documentation, the empty Prompt-05 source
  placeholder, and the four personal exports are user-owned and preserved.
- The four personal exports were inspected only for name, length, and SHA-256:

  | File | Bytes | SHA-256 |
  |---|---:|---|
  | `Manohar-try1.json` | 8,009 | `8fb11c53cdf58ba2bc873baac03b6b8c6d41eabfd2b23b2776289a8b0b9367e7` |
  | `Manohar-try2.json` | 22,896 | `35f13863f39c44018184fea7a319e9c7e3d3a031eab176bd8df87b9f12f94c81` |
  | `Manohar-try3.json` | 7,220 | `b6e7123a5d4b638c217f911dad63d46a2535aabb5ea865a2474dba9ef37be8d4` |
  | `Manohar-try4.json` | 7,268 | `48a3ee18f44d4899114cc6c8d6f23ffb6e64fb5b5fdf090b0d7f1b2487da190a` |

No stop condition in Prompt-05 section 25 is present.

## Baseline

The authoritative Prompt-04 full validator passed on Windows Python 3.11.9
and 3.14.6 after supplying a process-local `--ignore=jyothishyam_env`. That
ignore is required only because the existing untracked environment directory
contains 171 stale, inaccessible pytest basetemp trees; clean CI does not have
that directory. No repository configuration was changed.

Each lane produced:

- 912 collected nodes; 910 passed and 2 skipped;
- Prompt-02 focused contract: 17 passed;
- Prompt-03 focused contract: 19 passed;
- Prompt-04 focused contract: 62 passed;
- WP17 integrity: 22 passed;
- Prompt-02/WP17 manifest:
  `75b65d2cd1420c6261aadbb8159d10fb8c641137ce08d29f2a651952e5cdfaf7`;
- Prompt-03 manifest:
  `f57bc28504988ecf5ccfbf82de4bc495d2e69a91dfd476997cda5c89a563786e`;
- Prompt-04 manifest:
  `440a459cc60e9575874341e7c6673e714585ae79123957c9c19ccd175cb7930b`;
- approved snapshot: 4,041 bytes,
  `da2059ba3cfb92eed267f93d1e41585dac1422d68f685022c8609cfd04ad57af`;
- protected artifacts and all four present personal exports unchanged.

## Career inventory and ownership

### Models and typed batches

- `engine/interpreters/career_models.py` owns `CareerPreparedFacts`,
  `CareerFactResult`, `CareerCandidateDefinition`,
  `CareerCandidateEvaluation`, and `CareerEvaluationBatch`.
- A batch owns fixed candidate source order, factual component rows, base facts,
  compatibility evidence, completeness input, and typed preparation errors.
- Component row identity and the legacy planet/house/occupant/weight detail are
  authoritative in `CareerEvaluationBatch.component_facts`; they are not
  inference scores.

### Producer path

`prepare_career_snapshot` queries one `AstroStateSnapshot`; then
`evaluate_career_batch` produces one immutable batch;
`career_inference_rule_matches` creates the ordered universal `RuleMatch`
collection, including the explicit compatibility-baseline match;
`infer_career` makes the only production `.aggregate(...)` call to the shared
`InferenceEngine`.

`InferenceResult` is the sole owner of final normalized score, confidence,
agreement, contributions, components, conflicts, completeness, errors,
versions, and inference trace.

### Presentation sources

- Candidate/indicator order: `CareerEvaluationBatch.candidates` source order.
- Indicator rule identity/version/status/trace: candidate `RuleMatch`.
- Indicator contribution: matching `InferenceResult.contributions` item.
- Indicator legacy context/evidence: immutable candidate definition/result.
- Component order/detail: `CareerEvaluationBatch.component_facts`.
- Summary text, rounding, formula, and compatibility trace:
  `config/inference/career_compat_v1.json` and the current compatibility
  projection. Prompt-05 may preserve these values but may not change policy.
- Score/confidence: `InferenceResult.normalized_score` and `.confidence` only.
- Completeness/errors: `InferenceResult.data_completeness` and `.errors`, with
  batch preparation errors mapped only as typed presentation issues.

### Existing entry points and callers

- `interpret_career(AstroState)` and
  `interpret_career_snapshot(AstroStateSnapshot)` are public compatibility
  wrappers.
- `project_career_compatibility` is called by Prompt-01/02/03 tests and the
  legacy wrappers.
- `tools/generate_snapshot.py` calls the snapshot wrapper and is the primary
  public snapshot path.
- `runner_api.py`, `surya_to_parasara.py`, snapshot tooling, determinism tests,
  and the frontend consume that public snapshot transitively.

Compatibility removal owner: Parāśara engine maintainers. Remove the Career
dictionary wrapper only after every supported consumer is migrated to an
approved versioned public schema and snapshots are explicitly approved.

## InferenceResult inventory

`engine/inference/engine.py` is the only production constructor/aggregator.
`engine/interpreters/career.py` is its only production domain consumer.
`engine/inference/models.py` owns canonical logical serialization and strict
round trip. Other references are tests, scenario manifests, and exports from
`engine/inference/__init__.py`. There is no competing score, confidence,
agreement, completeness, contribution, conflict, or inference-error owner.

## Yoga inventory and ownership

- `engine/enrichments/yoga_engine.py` owns `YogaRuleSource`,
  `YogaEvaluationRecord`, and `YogaEvaluationBatch`.
- `evaluate_yoga_snapshot`/`evaluate_yoga_batch` produce the typed batch.
- Every record contains one authoritative universal `RuleMatch`; the record
  additionally retains source order, name, definition disposition/issues, the
  condition result, and legacy compatibility evidence/houses.
- `project_yoga_compatibility` emits the locked eight-key row in source order.
- `evaluate_yoga_rules` is the mutable-AstroState compatibility caller and
  attaches an independent copy to `astro.enrichments`.
- Existing Yoga consumers are enrichment/rule/serialization tests and helper
  tooling. The primary snapshot currently emits `diagnostics.yogas: []` and
  does not run Yoga evaluation.

Prompt-05 can map each existing record to `YogaDiagnostic` without re-running
detection. Compatibility-only planets/houses/aspects/evidence can be retained
inside the diagnostic's frozen `evidence_summary` and serialized one way.

Compatibility removal owner: Parāśara engine maintainers. Remove the Yoga
wrapper only after all consumers accept `YogaDiagnostic` or an approved public
schema.

## Snapshot, schema, and public assembly

`systems/Parasara/tools/generate_snapshot.py` is the only active primary
snapshot assembler. It currently:

- reads snapshot diagnostics;
- calls the Career compatibility wrapper;
- constructs the Wealth placeholder directly;
- emits empty Dasha/transit arrays and skeletal explainability dictionaries;
- writes indented JSON with `sort_keys=True` and `generated_at: null`.

`schemas/parashara_output.schema.json` is a broad draft-07 compatibility
schema with no exposed schema-version field. Adding a public version key would
change protected output, so the Prompt-05 profile must keep the exact shape.

The approved outward top-level keys are `engine`, `meta`, `diagnostics`,
`domains`, `dasha_timeline`, `transits`, and `explainability`. Optional scalar
behavior is represented by `generated_at: null`; empty collections are arrays
or objects, never null. `generate()` sorts object keys in bytes; semantic array
order remains producer/source order.

The Wealth dictionary is compatibility-only and has no interpreter or typed
evaluated result. Its owner/removal criterion is separately approved
Wealth-domain/public-schema work.

The frontend page `frontend/app/(auth)/account/astro/page.tsx` consumes only
the existing Career `summary`, `score`, `confidence`, and ordered indicator
`rule_id`, `contribution`, and `evidence` keys. It explicitly treats other
domains as outside the release.

Primary call path:

```text
runner_api/surya_to_parasara/snapshot tools
  -> generate
  -> SuryaAdapter -> chart_to_astrostate -> freeze_astrostate
  -> AstroStateSnapshot
  -> Career batch -> RuleMatch[] -> InferenceResult
  -> legacy Career projection
  -> direct snapshot dictionary -> JSON
```

Prompt-05 will replace only the final two nodes with a typed
`DomainPrediction` and one serialization-only `OutputAssembler` while keeping
the public result exact.

## Public compatibility baselines

Compact UTF-8 JSON (`ensure_ascii=False`, separators `,` and `:`):

| Output | Bytes | SHA-256 |
|---|---:|---|
| Career / `golden_chart_01.json` | 403 | `74442a0726173dcac3c521f1e67542443c16c43fbb39e7bded27f9e1601e3be3` |
| Career / `surya_test_chart.json` | 3,495 | `fee279260217eabb6a0f037d48d306888571fdf4c1c259630eca4337b5df9974` |
| Career / `surya_generated_chart.json` | 584 | `169cf5ce5ac9d8e678b160daf23293f365f2ab192a02a7aad90caab4da839dd9` |
| Yoga wrapper / `golden_chart_01.json` | 696 | `de21d839d01db93b50f5eceef745886a78a12da4ab44b892c8409f62077300f0` |

The approved snapshot byte baseline remains the governing integrated output
baseline stated above.

## Timing inventory

- `engine/dasha/vimshottari.py` returns mutable nested dictionaries and calls
  `datetime.utcnow()` when input time is absent. It is partial, tested in
  isolation, and not integrated into primary output.
- `AstroStateSnapshot.get_current_dasha()` and `.get_current_transits()` expose
  typed factual availability. In the current primary flow both are unavailable.
- No integrated transit calculator or typed transit producer exists.
- `tools/generate_snapshot.py` emits `[]` for both current public fields.

Prompt-05 will add availability-bearing output contracts only. It will not
import/call either calculator, read the clock, repair Dasha input, calculate
transits, or claim ready-empty output.

## Import graph and existing boundary findings

The current dependency direction is factual/rule/inference contracts into
Career, followed by a tool-level dictionary assembler. There is no backward
import from predicates/rules/inference to Career. The missing boundary is that
the tool imports the Career interpreter and owns both fact projection and
public dictionary construction. Prompt-05 will split orchestration from a
serializer whose imports stop at typed Prompt-05 contracts.

No raw Surya access occurs inside Career inference or Yoga evaluation after
snapshot construction. No second production `InferenceEngine` implementation
exists.

## Tests, manifests, workflows, and protected material

Relevant coverage includes `tests/inference`, `tests/astrostate`,
`tests/rules/test_career_typed_bridge.py`, `tests/enrichments` Yoga contracts,
`tests/wp17`, `systems/Parasara/tests` snapshot/characterization tests,
`tests/determinism_test.py`, and snapshot helper tests. Validators are
`tools/validate_prompt01.py` through `validate_prompt04.py`. Active CI is
`.github/workflows/ci.yaml`; exact snapshot comparison also runs through
`.github/workflows/parasara-snapshot-compare.yml` and
`systems/Parasara/tools/ci_snapshot_check.py`.

Prompt-01's 24 protected paths, Prompt-02/03/04 manifests, the approved
snapshot, the output schema, rule files, and the four personal exports must
remain unchanged.

## Proposed file classification

Required new source:

- `engine/domain/__init__.py` — public Prompt-05 type exports.
- `engine/domain/models.py` — universal frozen contracts, validation,
  canonical serialization, and logical digests.
- `engine/domain/factories.py` — inference/RuleMatch-to-presentation mapping
  factories only.
- `engine/output_assembler.py` — sole typed compatibility serializer.

Required modified source:

- `engine/interpreters/career.py` — typed build outcome and compatibility
  wrapper migration; no factual/inference semantics.
- `engine/enrichments/yoga_engine.py` and `enrichments/yoga.py` — diagnostic
  mapping and one-way compatibility projection; no Yoga detection change.
- `tools/generate_snapshot.py` — orchestration through typed inputs and the
  sole OutputAssembler.

Required tests/validation:

- `tests/domain/` — model, factory, interpreter, Yoga, timing, assembler,
  architecture, determinism, and compatibility contracts.
- `tests/domain/scenario_manifest.py` — cross-lane logical manifest.
- `tools/validate_prompt05.py` — composed Prompt-05 and predecessor gates.
- `.github/workflows/ci.yaml` — call Prompt-05 only after locally proven lanes.

Required documentation:

- Prompt-05 requirements, this report, final stopping report,
  `specifications/domain-prediction.md`, `architecture/current-state.md`, and
  `implementation/status.md`.

Compatibility-only:

- Career/Yoga projection functions and the legacy Wealth row inside the
  OutputAssembler compatibility profile.

Optional and not currently required:

- the broad public JSON schema, because changing it is unnecessary and could
  suggest a public migration;
- frontend source, because exact output compatibility leaves its contract
  unchanged.

Out of scope:

- all Surya Siddhānta, adapter, normalizer, AstroState, predicate, RuleMatch,
  inference, rule/config, astrology table, Dasha calculator, transit producer,
  and additional-domain interpreter files;
- protected fixtures, manifests, snapshots, personal exports, and Prompt-06+
  work.

## Locked implementation seam

All required owners are authoritative and available. The implementation may
proceed with one shared `DomainPrediction`, a thin Career mapping from one
`InferenceResult`, a `YogaDiagnostic` mapping from existing RuleMatches,
truthful unavailable timing contracts, and one logic-free compatibility
assembler. No astrology, inference, public schema, predecessor contract, or
version-governance change is required.
