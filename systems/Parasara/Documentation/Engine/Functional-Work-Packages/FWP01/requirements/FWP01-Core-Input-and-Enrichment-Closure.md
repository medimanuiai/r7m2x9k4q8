# FWP01 — Core Input and Enrichment Closure

> **Current Python policy - 2026-11-06:** [Root policy](../../../../../../../AGENTS.md) selects Python 3.11.9 only
> for development, tests, and CI and explicitly supersedes every dual-version
> requirement below. Retained Python 3.14 results/commands are historical, not
> current instructions. Run appropriate checks once on the selected runtime;
> keep correctness, regression, end-to-end, and same-runtime determinism checks.
> Missing second-version evidence is never a defect or blocker. Future specs,
> prompts, and handoffs must carry this policy; only an explicit user request
> can reinstate multiple Python versions.

Status: BOUNDED FINAL SPECIFICATION CORRECTION COMPLETE

Specification date: 2026-10-26

Bounded correction date: 2026-10-27; producer precision and explicit strict/legacy routing

Implementation status: NOT STARTED

Governing architecture progress: 8/10; Prompt-08 accepted
Scope owner: Parāśara factual construction and enrichment boundary

2026-11-06 bounded amendment: the [Aspect Contract V2 Addendum](FWP01-Aspect-Contract-v2-Addendum.md) defines the selected, exact predecessor-contract exception for the remaining aspect-projection finding. It preserves V1 and requires a separate instruction to begin implementation. This documentation task does not implement V2 or introduce another specification-review stage. Earlier dates, audit/status rows and test counts below remain historical evidence.

## 1. Decision and purpose

FWP01 closes the deterministic factual foundation used by later Parāśara work. It does not add predictions, rules, timing interpretation, domain narratives, scoring, or a public API. Its required pipeline is:

```text
Surya Siddhānta astronomical values
  -> validated Parāśara input contract
  -> canonical normalization and construction-only AstroState
  -> factual enrichment producers
  -> immutable AstroStateSnapshot with typed capability readiness
  -> protected PreparedAstroState projection for governed predicates
```

The implementation is deliberately divided into four ordered sub-work-packages because the repository combines a strong immutable query boundary with legacy best-effort producers and unapproved astrology approximations:

1. **FWP01-A — Input and normalization closure.** Make one strict, deterministic Surya-to-Parāśara boundary and preserve all accepted factual input.
2. **FWP01-B — Structural enrichment closure.** Close house ownership/occupancy, functional-role compatibility, whole-sign aspects, conjunction representation, and approved varga exposure.
3. **FWP01-C — Strength and condition truthfulness.** Separate legacy composite/proxy values from approved facts; preserve public compatibility and make unsupported facts explicitly unavailable.
4. **FWP01-D — Snapshot, determinism, and compatibility acceptance.** Prove immutable publication, typed unavailability, Python 3.11.9 determinism, protected-artifact preservation, and exact public compatibility.

The sequence is mandatory. A later sub-package must not compensate for an invalid earlier boundary. This pipeline describes the explicitly selected strict factual route. Existing compatibility entry points retain their current behavior under §9.1; FWP01 does not silently migrate them.

## 2. Repository and governance baseline

The specification audit used the actual repository rather than documentation status labels.

| Baseline item | Verified value |
|---|---|
| Branch | `main` |
| HEAD | `ec6b49a164389aada4e741561d75cb866527e6cf` |
| Staged files at specification start | none |
| Deterministic starting worktree inventory | 609 files; SHA-256 `27e9c22d1ceffa97158138ab51a747c15797552e04e11d1d834c982b08ce16e8` |
| Prompt-08 | accepted; zero remaining blockers/highs/mediums |
| Architecture progress | 8/10 |
| Prompt-09 / Prompt-10 | not started |
| FWP implementation | not started |
| GitHub delivery | deferred until Prompt-10 |
| `prepared_state.py` protected baseline | 51,241 bytes; SHA-256 `a2fca2dd17edd7092e8bee1cc8431891400d09f979a90f4f44d17b71c9466970` |
| Public snapshot protected baseline | 4,041 bytes; SHA-256 `da2059ba3cfb92eed267f93d1e41585dac1422d68f685022c8609cfd04ad57af` |
| v1 manifest fingerprint | `3e942f97cec7c24079faabc3db358b84177b752a8eb35a7b0d909f84a92d1220` |

The worktree already contains intentional cumulative Prompt-06, Prompt-07, and Prompt-08 source, test, validator, documentation, configuration, DSL, graph, and versioning changes. Four local `Manohar-try*.json` exports are personal artifacts. All are predecessor/user-owned work and are outside FWP01 mutation scope.

No separately approved functional-completion-map file exists locally. The accepted Prompt-06 specification, Prompt-07 statement of that absence, Prompt-08 §14 package sequence, and private local tracker together establish the current program sequence. No existing governed `Functional-Work-Packages` hierarchy conflicts with this path.

### 2.1 Evidence read for this specification

The audit covered current architecture/implementation/gap documents; the MVP current-state plan; Prompt-01 audit, requirements, reports, tests, and protected baselines; Prompt-04 and Prompt-05 requirements and accepted implementation; Prompt-06 through Prompt-08 specifications, manifests, validators, tests, and local implementation; Surya source and contracts; Parāśara adapter/models/schema/normalizer; mutable AstroState and immutable AstroStateSnapshot; prepared state and capability contracts; enrichment producers/tables; Dasha implementation; fixtures, snapshots, scenario manifests, and integration tests.

On 2026-10-26, the focused input/enrichment/AstroState evidence set completed with **49 passed** under Python 3.11 and **49 passed** under Python 3.14. This confirms the tested compatibility behavior, not untested classical correctness. Several current varga, aspect, and strength tests assert only structure or presence; one aspect test contains an unconditional `or True`. Those tests cannot promote a partial implementation to `VERIFIED_COMPLETE`.

### 2.2 Bounded correction evidence and preservation limitation

The completed independent specification review reported zero blockers, one high producer-precision finding and one medium entry-point-routing finding. This 2026-10-27 documentation-only correction addresses those two findings and their direct consequences; it is a targeted correction self-check, not another independent review or a new approval stage. No applicable `AGENTS.md` was found in the workspace hierarchy during this correction.

The review's separate focused evidence set passed **45 tests per Python lane**. Its composed tests, scenario checks and protected snapshot generation passed, but both complete composed validator commands exited unsuccessfully during their final inventory read. Windows denied access to `Documentation/AI-Prompt/Jyothishyam Architecture Consolidation.docx`. The review verified all 609 readable inventory entries and Git state against its baseline; it did not verify that DOCX's preservation. The DOCX is still unreadable at correction start. This limitation is not evidence that the document changed. Do not skip it in validators, weaken the inventory, terminate applications, delete locks, move it, or edit it.

The correction baseline is `main` at the HEAD in §2, with nothing staged and specification SHA-256 `ae70d7be506e38ab9b1409c9e0c8455191e336c7aef22d2c78338a153e0d1e94`. A fresh before-edit inventory records readable tracked, untracked and specifically protected ignored files, plus Git references/index and the unreadable path. Only this specification and the ignored private status tracker may change in this session. Final comparison must report any unreadable path separately; full worktree preservation cannot be claimed while it remains unverified. No full dual-Python suite is rerun solely for this documentation correction.

### 2.3 Current baseline reconciliation — 2026-11-06

The starting parent hash for this amendment is `15f33b50d3449710ef13d30d49aa0c0e8b6e356294093df36e9ac248b6257456`, matching the policy-adjusted hash observed previously. The earlier `c379506cccc3ba9d3ba2ea9b5af55bcd31b80dc37f4253f95e7c710cce094f70` is historical. Root AGENTS.md and `.python-version` govern Python 3.11.9 only. Inspected CI/runtime-selection and governance edits are policy evidence; inherited FWP01 and predecessor implementation changes are functional work, and the earlier 93 changed paths are not all attributed to policy.

A new readable-worktree inventory establishes preservation from this documentation session onward only. Earlier temporary reports/original inventory are unavailable. The DOCX is now readable and matched its prior session-start hash, but historical preservation remains UNVERIFIED. This supersedes only the current-access/status assertions in the historical §2.2 narrative, not its recorded historical errors. Continuing external edits must be reported and prevent a stable-baseline claim. Overall implementation validation is not asserted PASS here.

Findings 1, 3, 4 and 5 passed targeted independent confirmation; do not reopen them without new concrete evidence. Finding 2 remains unresolved pending the separately instructed V2 implementation and verification. Architecture remains 8/10; FWP01 is not accepted.

## 3. Locked boundaries

### 3.1 FWP01 owns

- strict validation of the Parāśara-facing chart through the named opt-in entries in §9.1, alongside preserved compatibility entries;
- narrowly scoped opt-in factual conversion/serialization precision in `systems/Parasara/tools/surya_to_parasara.py` under §5.5;
- canonical identity, unit, range, ordering, contradiction, and missing-data rules;
- deterministic mutable construction followed by one immutable snapshot publication;
- factual houses, house lords, occupants, placements, approved aspects, approved roles, approved vargas, and explicitly scoped strength facts;
- typed unavailable/malformed/version-mismatch behavior for every exposed capability;
- exact provenance sufficient to explain how a fact was derived;
- compatibility characterization and deterministic validation.

### 3.2 FWP01 does not own

- a rewrite of Surya Siddhānta astronomy;
- Vimshottari, antar/pratyantar, transit calculation, or time-window orchestration (FWP02);
- production rule-corpus migration, new interpretive rules, or dependency-graph activation (FWP03);
- Career expansion or Wealth, Marriage, Children, Health, Safety, cross-domain interpretation, or narrative generation (FWP04);
- public API, mobile/iPhone work, authentication, billing, frontend completion, or deployment (FWP05);
- Prompt-09 certification, Prompt-10 GitHub delivery, PR/CI orchestration, release tags, or branch cleanup.

### 3.3 Predecessor authority

FWP01 must consume the same Prompt-06 resolved authority object where a governed run already carries it. The actual repository type is `engine.versioning.ResolvedEvaluationVersions`; “resolved rule-set authority” denotes that object, not a new `ResolvedRuleSetAuthority` class. It must not select or change a rule set, lifecycle state, catalog entry, or manifest. Prompt-07 retains ownership of immutable DSL AST, compiler identity, predicate ownership, diagnostics, and limits. Prompt-08 retains ownership of dependency planning, same-authority enforcement, dependency lineage, inference-evidence separation, and complete-ledger atomicity. `RuleEngine` remains the sole owner of `RuleMatch`.

The current v1 catalog, rule-set manifest, Prompt-06/07/08 manifests, rule corpus, Career/Yoga ordering and public bytes are immutable inputs to FWP01. FWP01 facts may support later rules, but FWP01 does not authorize or activate those rules. The addendum permits only separately selected V2 component contracts and synthetic non-production fixtures within its exact scope; it preserves the same Prompt-06 authority, Prompt-07 ownership and Prompt-08 execution contracts.

## 4. Current implementation-status audit

The status vocabulary is exact: `VERIFIED_COMPLETE`, `IMPLEMENTED_WITH_GAPS`, `PARTIAL`, `SCAFFOLD_ONLY`, `UNAVAILABLE_BY_DESIGN`, `NOT_IMPLEMENTED`, `SME_DECISION_REQUIRED`, and `OUT_OF_SCOPE`.

| Subsystem | Status | Production evidence and existing tests | Verified behavior | Exact gap / MVP effect / SME | FWP01 action or exclusion |
|---|---|---|---|---|---|
| Surya Siddhānta input contract | IMPLEMENTED_WITH_GAPS | `systems/SuryaSiddhanta/ndastro_engine/{core.py,models.py,enums.py,ayanamsa.py}`; `systems/Parasara/tools/surya_to_parasara.py`; Surya and MVP boundary tests | Tropical longitudes/speeds and nodes are produced; the web boundary applies Lahiri, derives sign/degree/nakshatra/pada/whole-sign house, emits nine bodies, and represents node motion as unknown | Parāśara consumes a derived JSON shape rather than a versioned Surya export; flags are hard-coded false; absolute sidereal longitude is implicit; `build_planet_record` and `build_lagna_record` round degree to four decimals while sign/nakshatra/pada/house use unrounded longitude, allowing degree 30 or contradictory boundary records. No astronomy change is needed | Add only the explicit `precision="strict_factual"` producer option in §5.5; retain unrounded `sidereal_longitude`, validate all derived fields against it, preserve legacy defaults and keep node motion unavailable |
| Adapter | IMPLEMENTED_WITH_GAPS | `engine/adapter/surya_adapter.py`, `schemas/surya_input.schema.json`, `engine/models.py`; `test_validator_and_adapter.py` | `load()` applies Draft-07 validation then Pydantic construction | `load_many()` bypasses equivalent schema validation; JSON/file errors are not bounded; schema omits strict identity/enums/ranges and allows contradictory data. MVP blocker because invalid facts can enter construction | One shared strict validator for the proposed mapping/file/single/batch APIs in §9.1; separate strict schema/models; safe typed failures. Preserve existing `validate`, `load` and `load_many` compatibility semantics |
| Normalization | PARTIAL | `engine/normalizer.py`, `enrichments/{canonical_ids.py,precision.py}`; phase-1/phase-2 and MVP boundary tests | Converts exact `Kethu` to `Ketu`, filters Lagna pseudo-planets, creates whole-sign houses when absent, normalizes some degrees, and attaches enrichments | Uses truthiness where zero is valid; silently defaults invalid Lagna lookup to Aries; may reinterpret supplied `house` as Aries sign index; drops nakshatra, motion, and flags from `PlanetState`; broad exceptions fabricate fallback output; degree normalization rounds to two decimals. MVP blocker. No doctrine needed | Add `chart_to_astrostate_strict` and `build_strict_snapshot` under §9.1: zero-safe, full-precision factual construction with no fallback. Keep `chart_to_astrostate(chart: Chart)` on its compatibility route |
| Prepared state | VERIFIED_COMPLETE | `engine/rules/prepared_state.py`, `rules/snapshot_adapter.py`; `test_prepared_astrostate.py`, capability and Prompt-01/07/08 suites | Exact seven predicate capabilities, deep immutability, deterministic canonical bytes/digest, typed readiness, mutation isolation, and strict query semantics are protected | It intentionally projects only the predicate contract and is not a general enrichment store. Not an MVP gap | Preserve `prepared_state.py` byte-for-byte. Adapt only through the existing one-way `snapshot_adapter.py` if required; no eighth prepared capability in FWP01 |
| AstroStateSnapshot | IMPLEMENTED_WITH_GAPS | `engine/astrostate_api.py`; `tests/astrostate/*`, Prompt-04 validator/manifest | Deep immutable core, deterministic ordering/serialization, capability inspection, factual queries, typed absent/unavailable/malformed/version mismatch, Dasha/transit placeholders | Publication faithfully freezes producer data, including weak legacy facts; the capability catalog labels strengths as legacy composite/partial proxy; no direct combustion/retrograde capability exists. API mechanics are complete; producer closure is not | Preserve existing IDs, versions, query meaning, logical bytes for protected fixtures, and typed states. Tighten producer inputs without changing protected scenarios; stop if a catalog/schema version change is unavoidable |
| Planet identity, including Kethu/Ketu | IMPLEMENTED_WITH_GAPS | `engine/identities.py`, `enrichments/canonical_ids.py`, normalizer; identity, snapshot, predicate, MVP boundary tests | Canonical internal order is Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu; `normalize_planet_id` accepts case variants and `Kethu` | Two normalization helpers differ; `canonical_ids.py` does not explicitly list `Kethu`; normalizer accepts only exact-case `Kethu`; unknown values can degrade to arbitrary lowercase IDs before the snapshot rejects them. MVP blocker | Make `engine/identities.py` the single authority; accept `Kethu` only as an input alias; emit `Ketu`; reject unknown/duplicate bodies; preserve Surya-facing `Kethu` compatibility |
| Sign and house placement | IMPLEMENTED_WITH_GAPS | boundary tool, schema/models, normalizer, `astrostate_api.py`; MVP, derived-state, snapshot tests | Lahiri sign/degree and ascendant-relative whole-sign house are tested; snapshot validates signs and houses 1–12 | Supplied and generated house semantics are not distinguished strongly; missing/partial house arrays are accepted; sign-degree-house contradictions are not comprehensively rejected; 0° boundaries are under-tested. MVP blocker | Require all nine placements and Lagna in the strict route; derive from unrounded longitude and reject disagreement; publish 12 houses. Preserve three-planet, partial-house and legacy-numbering inputs only through the explicit compatibility route |
| House lords | IMPLEMENTED_WITH_GAPS | `planet_strengths.SIGN_LORD`, normalizer-generated houses, snapshot `houses.lords`; derived/snapshot/Career tests | Deterministic classical seven-planet sign ownership is used for 12 whole-sign houses | Duplicate ownership maps exist; supplied lords are not always reconciled; nodes have no house ownership; summary availability can be ready-empty even when houses exist. MVP blocker for Career/later rules; doctrine is already pinned for v1 | One internal ownership mapping reused by construction; require exact agreement; nodes never become sign lords; retain v1 values |
| Functional roles | PARTIAL | `enrichments/functional_roles.py`; 12 files in both table roots; role tests, Yoga integration; v1 manifest pins `systems/Parasara/enrichment_tables/functional_roles/*` | All ascendants have compatibility tables; current Yoga path can publish `roles.functional`; table-root lookup is repository anchored for the preferred root | Fallback heuristic invents weights/thresholds; table tests do not prove doctrinal correctness; natural benefic/malefic simplification ignores conditions; duplicate roots are ambiguous. Current v1 compatibility needs the pinned table, but authoritative astrology needs SME approval | Preserve current pinned overrides and legacy heuristic results on compatibility calls. Strict variants use manifest-pinned rows only with no heuristic fallback; validate all 12×9 rows, ownership consistency, allowed labels and order; unavailable/malformed rows stay typed unavailable/malformed |
| Varga D9 | SME_DECISION_REQUIRED | `enrichments/varga.py`; D9 and integration tests | Deterministic data is emitted and snapshot can expose `vargas.positions` | Two incompatible implementations coexist; current tests check shape, not classical mappings. The `(sign_index * 3 + part) % 12` mapping is not sufficient evidence for classical Navāṃśa. Not required by current v1 public output; required before later D9 rules | Do not certify current D9. Add authority-backed boundary vectors only after SME approval; otherwise publish D9 unavailable in the strict FWP01 factual path while leaving compatibility bytes unchanged |
| Varga D3 | SME_DECISION_REQUIRED | `enrichments/varga.py`; `test_varga_more.py` | Generic deterministic D3 structure exists | Generic equal-division mapping is not an approved Drekkāṇa doctrine; tests are structural only. Not a current MVP blocker | Same policy as D9; exact tradition/table and boundary vectors required before availability |
| Varga D7 | SME_DECISION_REQUIRED | same | Generic deterministic D7 structure exists | Generic mapping is not approved Saptāṃśa doctrine; structural tests only. Not a current MVP blocker | Same policy as D9 |
| Varga D30 | SME_DECISION_REQUIRED | same | Generic deterministic D30 structure exists | Equal 1° division is not evidence for an approved Triṃśāṃśa scheme; boundary/tradition policy absent. Not a current MVP blocker | Same policy as D9 |
| Parāśara aspects | PARTIAL | `enrichments/aspects.py`, `rules/parashara/aspects.yaml`; aspect/snapshot/Yoga tests; v1 manifest pins the table | Seven classical planets have whole-sign offsets; Mars/Jupiter/Saturn special aspects are represented; graph contains source/target trace; empty targets are retained as sign traces | Three overlapping APIs produce different shapes; config lookup is CWD-sensitive; node aspects are unapproved; one test is vacuous; graph order/duplicates and directionality are not fully contracted. Current Yoga compatibility needs the pinned graph | Keep manifest-pinned offsets; anchor path; define directed source→target-sign facts, stable ordering/deduplication and evidence; node aspects remain legacy-only/unavailable for new factual use pending SME |
| Planet strength / full Shadbala | PARTIAL | `enrichments/planet_strengths.py`, `shadbala.py`, strength tables/tests; snapshot scopes values as `legacy_composite` and `legacy_partial_proxy` | Deterministic payloads contain named components and traces on tested fixtures | Formulas are explicitly naïve/config-weighted proxies; motion facts are dropped; aspect direction is used incorrectly for received influence; table loading is CWD-relative; total is not demonstrated classical Shadbala; current tests largely assert keys/ranges. Current Career compatibility uses the 0–1 composite, so removal would break MVP | Preserve compatibility output exactly but never label it classical. Strict factual path reports approved components only and typed unavailability for the rest. No new formula/weight/threshold without SME |
| Naisargika Bala | PARTIAL | both strength modules and `naisargika_bala.yaml` | Stable table/proxy values exist | Competing normalized and table units; no approved unit/authority validation | Legacy partial proxy only; classical capability unavailable pending SME |
| Uchcha Bala | PARTIAL | `_uccha_bala`, `compute_sthana_bala`, exaltation table | Proximity-shaped value is produced when data exists | Uses within-sign degree against a table without a complete sign/absolute-longitude contract and mixes flags; formula/units not approved | Preserve dignity facts separately; classical Uchcha Bala unavailable pending SME |
| Dig Bala | PARTIAL | both strength modules, `dig_bala.yaml` | House lookup/proxy output exists | Implementations disagree and do not establish the continuous classical calculation | Legacy partial proxy only; unavailable as classical pending SME |
| Kāla Bala | PARTIAL | both strength modules | Day/night bonus exists | Full Kāla Bala constituents are absent; `is_day=None` is treated as night in one path | Do not fabricate; unavailable as classical. A later approved formula may consume explicit temporal facts |
| Cheṣṭā Bala | PARTIAL | both strength modules; Surya speed/retrograde source | Base/retrograde/speed proxy exists | Normalizer drops motion; node speed is unsupported; scaling and formula are unapproved | Preserve motion fact in FWP01-A; legacy proxy remains; classical component unavailable pending SME |
| Dṛk Bala | PARTIAL | both strength modules; aspect graph | Sums configured aspect weights | Uses outgoing edges, unapproved default weights, and no benefic/malefic received-influence doctrine | Aspect facts close in FWP01-B; classical Dṛk Bala remains unavailable pending SME |
| Saptavargaja Bala | NOT_IMPLEMENTED | only a generic varga-count bonus in `planet_strengths.py` | No classical component is implemented | Proxy counts any stored varga and is not Saptavargaja Bala | Remove this claim from strict factual output; unavailable pending approved vargas and SME formula |
| Ojha-Yugma Bala | NOT_IMPLEMENTED | no authoritative producer/test | none | Formula, inputs, and tests absent | Typed unavailable; not required by current v1 MVP |
| Kendra Bala | NOT_IMPLEMENTED | no authoritative producer/test | none | Absent as a distinct strength capability | Typed unavailable; later SME decision if required by FWP03 corpus |
| Drekkana Bala | NOT_IMPLEMENTED | no authoritative producer/test | none | Absent; D3 itself is unapproved | Typed unavailable; depends on approved D3 and SME formula |
| House conditions | PARTIAL | `compute_house_summaries`, `derived/{models.py,builder.py}`, snapshot house queries; derived/Career/snapshot tests | Ownership, occupants, lord strength, `aspected_by`, pressure fields and a 0–1 score are shaped for compatibility | Pressure and score blend legacy role/strength proxies; builder can return an unvalidated dictionary; aspect source differs; missing facts may become zeros. Ownership/occupancy/lord placement are MVP facts; scores are not | Add strict factual house-condition assembly containing ownership, occupancy, lord placement, approved aspects, and explicitly available strength facts only. Keep legacy score/pressure solely in compatibility projection |
| Combustion | PARTIAL | Surya `combustion.py`; input schema flags; boundary/strength code | A standalone Surya date-range calculator exists and the schema can carry a Boolean | MVP boundary hard-codes false; normalizer drops flags; orbs/exceptions are not approved for Parāśara; false currently means placeholder, not established fact. Not used by current v1 rules | Never publish hard-coded false as fact. Preserve an explicitly supplied validated flag only with source provenance; otherwise typed unavailable. Automatic calculation requires separate SME approval and must not alter Surya silently |
| Retrogression | IMPLEMENTED_WITH_GAPS | Surya speeds/`retrograde.py`; boundary derives non-node Boolean; schema; strength code; MVP node test | Non-node speed sign is available at the boundary; nodes honestly emit `{}` | Normalizer drops motion; standalone period algorithm uses a longitude comparison vulnerable at wrap and is unnecessary when signed speed exists. Current v1 does not require it | Preserve boundary non-node Boolean and provenance; node state unavailable; no new period computation in FWP01 |
| Exaltation/debilitation | PARTIAL | schema flags; strength modules; exaltation/debilitation YAML; snapshot dignity/exaltation queries/tests | Explicit flags and metadata facts can be frozen; tables exist and are v1-manifest-pinned | Boundary hard-codes flags false; dignity placeholder currently returns elements; exaltation tables omit sign identity in the value; debilitation table is unused; exact degree/range semantics conflict. Current MVP only needs legacy compatibility values | Remove placeholder element-as-dignity from strict path; preserve explicit source facts; reject contradictions; keep classical computed dignity unavailable until SME approves tables, degree convention, exact-point vs sign policy, and node policy |
| Conjunctions | PARTIAL | `compute_basic_aspects`; snapshot basic representation/tests | Deterministic directed pairs are emitted for same-sign planets and sometimes degree proximity | Same-sign and 1° orb are blended; degree values may be within-sign or absolute, allowing cross-sign mistakes; orb has no authority; duplicate-direction semantics are implicit | Define compatibility `basic_conjunction_list` as current legacy representation only. Strict conjunction fact requires same canonical sign; any degree-orb subtype requires a separately approved policy. Deterministically sort directed edges |
| Dasha capability | OUT_OF_SCOPE | `engine/dasha/vimshottari.py`, Dasha tests; snapshot `dasha.current`; Prompt-05 timing models | Standalone partial implementation and typed unavailable snapshot/output state exist | Not integrated; wall-clock fallback and Moon-longitude concerns remain | FWP02 only. FWP01 guarantees Moon longitude/nakshatra/pada prerequisites and preserves `dasha.current` unavailable without an explicit FWP02 supply |
| Transit capability | OUT_OF_SCOPE | input model/schema field, snapshot `transits.current`, Prompt-05 model/output | Typed unavailable/empty contract exists | No governed transit producer or interpretation | FWP02 only. FWP01 preserves capability semantics and does not consume input `current_transits` as trusted facts |
| Missing/unavailable facts | VERIFIED_COMPLETE | `engine/capability.py`, `astrostate_api.py`, `rules/capabilities.py`, prepared state; capability/snapshot tests | Missing, ready-empty, malformed, version mismatch, unsupported and absent entity are distinct, immutable, deterministic states | Legacy producers sometimes fabricate neutral/false/zero before the typed boundary can report absence | Preserve the contracts; change producers so unknown never becomes neutral/false/zero; add field-level evidence where a broad legacy capability contains partial facts |
| Deterministic validation | IMPLEMENTED_WITH_GAPS | Prompt-01 through Prompt-08 validators/manifests; current fixtures/snapshots; focused audit passed 49 tests in each lane | Strong predecessor gates, dual-Python support, hashes, CWD/hash-seed scenarios and protected public snapshot exist | No FWP01 validator/manifest; current enrichment tests lack invalid/contradictory/boundary vectors and classical oracles; CWD-sensitive tables remain | Add FWP01 focused suites, deterministic scenario manifest and composed single-runtime validator without updating predecessor hashes |

### 4.1 MVP and SME disposition index

This index makes the MVP-blocking and astrology-authority disposition explicit for every audit row. “Conditional” means the existing compatibility behavior is retained, but promotion to a new authoritative factual use requires the listed SME decision.

| Subsystem | Blocks current Parāśara MVP if left as-is? | Astrology SME decision required for FWP01 disposition? |
|---|---:|---:|
| Surya Siddhānta input contract | Strict closure needs the bounded Parāśara producer precision remedy in §5.5; legacy MVP stays compatible | No; no astronomy or doctrine change |
| Adapter | Yes | No |
| Normalization | Yes | No |
| Prepared state | No | No |
| AstroStateSnapshot | No; producer closure is the gap | No |
| Planet identity | Yes | No |
| Sign and house placement | Yes | No |
| House lords | Yes | No; preserve pinned v1 ownership |
| Functional roles | No for v1 compatibility; yes before new authoritative role rules | Yes, `SME-FWP01-01` |
| D9 | No for current v1 | Yes, `SME-FWP01-02`, or remain unavailable |
| D3 | No for current v1 | Yes, `SME-FWP01-03`, or remain unavailable |
| D7 | No for current v1 | Yes, `SME-FWP01-04`, or remain unavailable |
| D30 | No for current v1 | Yes, `SME-FWP01-05`, or remain unavailable |
| Parāśara aspects | No for pinned v1 classical-planet offsets; new node use is blocked | Conditional, `SME-FWP01-06` |
| Planet strength / full Shadbala | No while legacy compatibility is preserved; yes for any new classical-strength rule | Yes, `SME-FWP01-10` |
| Naisargika Bala | No | Yes, `SME-FWP01-10`, or remain unavailable |
| Uchcha Bala | No | Yes, `SME-FWP01-08` and `SME-FWP01-10`, or remain unavailable |
| Dig Bala | No | Yes, `SME-FWP01-10`, or remain unavailable |
| Kāla Bala | No | Yes, `SME-FWP01-10`, or remain unavailable |
| Cheṣṭā Bala | No | Yes, `SME-FWP01-10`, or remain unavailable |
| Dṛk Bala | No | Yes, `SME-FWP01-06`, `SME-FWP01-10`, and `SME-FWP01-11`, or remain unavailable |
| Saptavargaja Bala | No | Yes, approved vargas plus `SME-FWP01-10`, or remain unavailable |
| Ojha-Yugma Bala | No | Yes, `SME-FWP01-10`, or remain unavailable |
| Kendra Bala | No | Yes, `SME-FWP01-10`, or remain unavailable |
| Drekkana Bala | No | Yes, approved D3 plus `SME-FWP01-10`, or remain unavailable |
| House conditions | Yes for ownership/occupancy/lord placement; no for proxy scores | Conditional, `SME-FWP01-11` only for benefic/malefic influence |
| Combustion | No for current v1 | Yes, `SME-FWP01-09`, or remain unavailable |
| Retrogression | No for current v1; preservation is factual closure | No for signed-speed fact; node policy remains unavailable |
| Exaltation/debilitation | No for current v1 compatibility | Yes, `SME-FWP01-08`, or remain unavailable |
| Conjunctions | No for current v1 | Conditional, `SME-FWP01-07` for any orb subtype |
| Dasha capability | No; FWP02 owns it | No FWP01 decision; explicitly out of scope |
| Transit capability | No; FWP02 owns it | No FWP01 decision; explicitly out of scope |
| Missing/unavailable facts | Yes if producers continue fabricating values | No |
| Deterministic validation | Yes | No |

## 5. Definitive input contract

### 5.1 Required chart values

The proposed `SuryaAdapter.from_mapping_strict`, `load_strict`, `from_mappings_strict` and `load_many_strict` APIs alone enforce this full strict contract. Existing `validate`, `load` and `load_many` do not acquire it. A strict record requires:

- `metadata.birth_datetime_utc`: ISO-8601 timestamp containing an offset; canonicalized to UTC;
- `metadata.birth_location.latitude`: finite decimal degrees in `[-90, 90]`;
- `metadata.birth_location.longitude`: finite decimal degrees in `[-180, 180]`;
- `metadata.birth_location.timezone_offset_minutes`: integer in `[-840, 840]`, retained as source metadata, not used to reinterpret the already-UTC instant;
- `metadata.ayanamsa == "lahiri"`, `metadata.sidereal is true`, `metadata.house_system == "whole_sign"`, and `metadata.house_numbering == "ascendant_relative"` for the active MVP boundary;
- `lagna.sidereal_longitude`, `lagna.sign` and `lagna.degree`, with nakshatra/pada checked when supplied;
- exactly one record for Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, and Ketu/Kethu;
- each planet's original finite `sidereal_longitude` in `[0, 360)`, sign, within-sign degree, ascendant-relative house, nakshatra name/index/pada, and motion object (which may omit `retrograde` only for unsupported nodes);
- `houses` either empty, meaning “construct all twelve whole-sign houses,” or a complete twelve-house set that exactly agrees with Lagna and planet placements.

`aspects`, `vargas`, flags, strength values, Dasha and transit values supplied by an unversioned Surya-shaped document are not trusted enrichment authority. They may be retained for diagnostics/compatibility only when validated and reconciled; strict FWP01 producers compute or mark their own capabilities unavailable.

### 5.2 Units and canonical representation

- Surya core tropical longitude and speed remain in degrees and degrees/day.
- The Parāśara boundary uses Lahiri sidereal longitude in `[0, 360)`.
- Planet and Lagna `degree` is within-sign degrees in `[0, 30)`; it is never treated as absolute longitude.
- Strict producer records carry the original canonical `sidereal_longitude`; do not reconstruct a lost value from rounded degree. For a supplied strict record, `sign_index * 30 + degree` must agree with that longitude under the same binary64 arithmetic used in §5.5. Preserve the validated value through normalization and publication; display rounding is not factual normalization.
- House is an integer 1–12 relative to the whole-sign Lagna.
- Nakshatra index is 1–27 and pada is 1–4. Name/index/longitude must agree under the existing Surya enumeration; aliases are an explicit adapter concern.
- Canonical planet spelling is title-case `Ketu`; `Kethu` is accepted only at the Surya/input edge. Serialized canonical facts never contain both.
- Planet order is the existing `CANONICAL_PLANETS` order. Houses are 1–12. Varga IDs and capability IDs sort canonically. Aspect order is source planet order, aspect offset/order, target kind, target identity.

### 5.3 Missing, invalid, and contradictory behavior

- Invalid JSON, schema/type/range errors, unknown/duplicate planets, missing required bodies, non-finite numbers, invalid signs, partial house sets, or contradictory sign/degree/house/nakshatra data fail construction before enrichment.
- Error output uses stable safe codes and paths; it contains no local path, raw exception, or private input.
- Optional unsupported facts remain absent and become typed capability unavailability. They never become `False`, `0`, `neutral`, an empty list meaning “none,” or a guessed default.
- No `except Exception` fallback may convert an invalid required strict fact into a successful AstroState. Strict entry points never call compatibility entries after a failure.
- Strict batch loading applies the identical strict per-record validator as strict single loading and returns deterministic record-indexed failures; it never validates one strict code path less strictly than another. Existing legacy batch behavior is preserved explicitly in §9.1, not described as strict closure.

### 5.4 Mutation and publication

Strict input mappings, lists, models and table values are defensively copied. Mutation after strict adapter load, normalization, enrichment or snapshot publication cannot change the snapshot or any digest. The mutable `AstroState` exists only within construction. Proposed `build_strict_snapshot` assembles all strict producers before its one call to `freeze_astrostate`; invalid required input fails before enrichment and does not freeze. Projection/evaluation of that snapshot does not freeze it again.

Existing compatibility wrappers retain their current freeze boundaries: `generate_snapshot.generate`, `prepare_career_facts` for mutable input, and `build_yoga_snapshot` each publish once for their own completed construction run. A Yoga wrapper's defensive copy is a separate compatibility construction run; this does not authorize a second freeze of a completed strict run. Evaluation never traverses mutable AstroState or raw input.

### 5.5 Producer precision remedy and historical rounded payloads

**Observed source flow.** `generate_chart(lat, lon, dt, timezone_offset_minutes=0, *, timezone_name="UTC", place_label="")` obtains unchanged Surya tropical positions and Lahiri ayanamsa. `to_lahiri_sidereal(tropical_longitude, ayanamsa_degrees)` calls `normalize_longitude` on their difference. The current `build_planet_record(name, sidereal_longitude, ascendant_longitude, *, retrograde)` and `build_lagna_record(sidereal_longitude)` use that unrounded normalized longitude for `longitude_to_rashi`, `_nakshatra_record` and `whole_sign_house`, but serialize `round(longitude % 30.0, 4)` as degree. `_nakshatra_record` uses the existing `Nakshatras` enumeration and `Nakshatras.current_pada` on unrounded longitude. Thus `29.99996` becomes Aries degree `30.0`, and `13.33334` becomes degree `13.3333` while retaining the unrounded value's Bharani/index-2 record. The same loss affects Lagna degree. Metadata ayanamsa is rounded only after the full value has been used for conversion.

**One proposed remedy; no implementation in this correction.** Add the keyword-only `precision: Literal["legacy_v1", "strict_factual"] = "legacy_v1"` to those three producer functions, passing it explicitly from `generate_chart` to both record builders. Existing arguments, defaults, CLI calls and public callers remain compatible; an unsupported option fails with a controlled error rather than choosing another route. Only an explicit `precision="strict_factual"` call emits the strict internal shape with `sidereal_longitude` on both planet and Lagna records. This option selects conversion/serialization precision, not an astrology algorithm or rule set.

1. **Canonical source:** use the already-computed finite binary64 value `L = normalize_longitude(tropical_longitude - ayanamsa_degrees)` and the corresponding unrounded ascendant value `A`. Do not round either before deriving or serializing facts. For direct record-builder calls, normalize the supplied absolute longitude identically. Preserve the actual binary64 result through ordinary round-trip-safe JSON numeric serialization; this promises preservation of supplied factual precision, not additional astronomical precision.
2. **Degree and sign:** derive `sign_index = int(L // 30.0)` and `degree = L - 30.0 * sign_index`. The published strict degree is finite and satisfies `0 <= degree < 30`, including exact zero. Both adjacent sides of every transition use their actual unrounded values: `29.99996` remains Aries degree `29.99996`; exact absolute `30.0` is Taurus degree `0.0`. Normalize an absolute source `360.0` to `0.0` before derivation. This is never permission to accept a supplied within-sign degree of `30.0`; strict payload longitude must already be canonical.
3. **Other derived fields:** derive sign, nakshatra name/index/pada and ascendant-relative house from the same unrounded `L` and `A`, using the current helpers/enumeration and unchanged Lahiri/whole-sign formulas. Validate each strict record against its original `sidereal_longitude`; no epsilon or rounding tolerance may conceal contradictory evidence. Strict Lagna's supplied nakshatra and house-1 values must agree as well.
4. **Factual versus display output:** strict numeric facts keep full source precision. Display rounding may occur only on a separate presentation/compatibility copy and never feeds strict validation, enrichment or publication. Default `legacy_v1` continues emitting exactly the current shape and four-decimal degrees, including historical boundary limitations. `runner_api.generate_response` and the producer CLI keep that default; this correction does not migrate their public `surya_chart`, Career/Yoga or snapshot output.
5. **Historical precision:** existing rounded files remain eligible only for deliberately selected compatibility calls. Calling a strict entry with a missing original longitude, degree `30.0`, or inconsistent nakshatra/pada produces a safe `StrictInputError` (or its record-indexed batch issue). Do not clamp, guess, roll a within-sign 30 into the next sign, derive a replacement nakshatra from the rounded degree, or overwrite the supplied evidence. A caller with genuine original source values may explicitly produce a new strict record; the adapter never silently regenerates astronomy. If original precision is unavailable, report `source_longitude_missing`, `within_sign_degree_out_of_range` or `derived_position_mismatch` as applicable and construct no strict snapshot for that record.
6. **Scope and conflict rule:** §10.1 authorizes only this opt-in Parāśara-facing precision branch and its argument propagation in `surya_to_parasara.py`. No Surya engine/public-contract, ayanamsa, doctrine, orbital formula, node policy, default public output or unrelated producer refactoring is permitted. If strict and protected public behavior cannot coexist with these explicit defaults, stop and record the conflict; do not update protected outputs. The executable route split is specified in §9.1, not deferred to an inferred data heuristic.

Future coverage is assigned to `tests/fwp01/test_producer_precision.py`, `tests/fwp01/test_input_contract.py`, `tests/fwp01/test_entry_point_routing.py` and `tests/fwp01/test_compatibility_and_boundaries.py`, plus additive default-path characterization in `systems/Parasara/tests/test_mvp_chart_boundary.py`. Cover planet and Lagna `29.99996`, both representable sides and exact points of sign transitions including 360/0, values rounding across nakshatra and pada boundaries (including `13.33334`), exact valid zero, invalid within-sign 30, consistent sign/degree/longitude/house/nakshatra/pada, missing original precision and unchanged default public output. No fixture or expected protected bytes are rewritten.

## 6. Enrichment completion contracts

These completion contracts apply to the explicit strict route unless a paragraph names legacy compatibility. Existing producer names/defaults keep current compatibility behavior; new strict variants are reached only through `build_derived_state_strict`. They cannot import legacy fallback facts as approved strict evidence.

### 6.1 Houses and house conditions

One shared sign-ownership table supplies the existing seven-planet rulership. For every house, strict factual output contains house number, sign, lord, sorted occupants, lord's natal house when available, approved incoming aspect facts, and references to separately typed available strength facts. Nodes are occupants/aspect sources where approved; they are never sign lords.

`benefic_pressure`, `malefic_pressure`, `house_score`, and similar aggregates are legacy compatibility values, not factual house conditions. They must not be used by new governed rules unless a later approved rule/SME contract explicitly defines them. Missing lord placement, aspect or strength input produces typed unavailability for that facet and does not zero-fill it.

### 6.2 Functional roles

The strict role producer uses only the 12 manifest-pinned tables under `systems/Parasara/enrichment_tables/functional_roles/`. Each table is validated for nine canonical planets, permitted labels, owned-house consistency, numeric compatibility score bounds, and deterministic explanation fields. The second table root and heuristic scoring are not strict fallback authorities. Existing compatibility role producers retain their present pinned-override and legacy heuristic behavior solely on the compatibility route in §9.1; publishing those values does not confer new factual authority.

The FWP01 fact is ascendant-specific and traceable to table identity/version/digest and owned houses. If the pinned row is absent, malformed, or contradicts ownership, `roles.functional` is malformed/unavailable; no score heuristic fills it. The pinned compatibility values are preserved but remain `astrology_sme_approved: false` under the current v1 manifest.

### 6.3 Vargas

For D9, D3, D7, and D30 the required source is canonical absolute sidereal longitude. Boundaries use half-open intervals: the lower bound belongs to the new division, exact `360°` normalizes to `0°`, and floating-point comparisons use the repository's deterministic numeric policy rather than epsilon-based tradition changes.

A varga may be `READY` only when:

1. one named approved tradition/algorithm is documented;
2. an SME-approved table/formula and version are available;
3. exact boundary vectors cover every sign class and all transition degrees;
4. output uses canonical planet identity, varga ID, target sign, part number, and source longitude;
5. construction and serialization are deterministic on Python 3.11.9.

The current generic implementations do not meet these conditions. Until approval, the strict capability is unavailable, while existing compatibility-only data remains isolated and cannot satisfy a new governed predicate. D1/D10/D12/D60 and all other vargas are excluded unless a later rule-library requirement is separately approved.

### 6.4 Aspects and conjunctions

The v1 whole-sign graph preserves the manifest-pinned offsets: all seven classical planets have the seventh; Mars additionally has fourth/eighth, Jupiter fifth/ninth, and Saturn third/tenth. An aspect is a directed source-planet to target-sign factual edge; matching target planets are derived references, not a replacement for the sign edge. Evidence includes source sign/house, offset, target sign/house, table identity/version/digest, and any matched canonical planets.

Node aspects are not promoted beyond legacy behavior without SME approval. Absence of an occupant does not mean absence of an aspect-to-sign. Duplicate edges are rejected, and serialization order is fixed. Strength/applicability/interpretive weights are excluded.

The legacy `basic_conjunction_list` remains compatible. The strict same-sign conjunction is a symmetric relationship represented as two deterministically ordered directed query edges because the existing snapshot API is directed. Degree-orb conjunction is a separate unsupported subtype until an orb, longitude basis, and boundary rule are approved.

### 6.5 Strength and dignity

The existing 0–1 planet strength and named Shadbala payload remain available only under their existing `legacy_composite` and `legacy_partial_proxy` factual scopes. No field, UI, rule, or document may call the current aggregate “full classical Shadbala.”

The current MVP Career/Yoga compatibility path may continue reading exactly the existing values to preserve public output. New governed rules may consume only a component explicitly marked ready under an approved formula/version. Naisargika, Uchcha, Dig, Kāla, Cheṣṭā, Dṛk, Saptavargaja, Ojha-Yugma, Kendra, and Drekkana status is as listed in §4. Unsupported components remain typed unavailable. No total is computed from a mix of ready and unavailable classical components.

Explicit supplied combustion, retrogression, exaltation, or debilitation facts must include source provenance and pass contradiction checks. Hard-coded boundary flags are not facts. Non-node retrogression from signed sidereal longitudinal speed may be preserved; node retrogression stays unavailable. Computed combustion and dignity require the SME decisions below.

## 7. Capability and evidence semantics

FWP01 preserves the Prompt-04 general capability IDs and versions and the Prompt-01 seven-capability prepared projection. Construction route is selected by the called entry point, never by capability readiness. A strict snapshot is newly assembled from strict inputs and approved/explicitly unavailable producers; it is not a relabeled compatibility snapshot. Legacy roles, node aspects, vargas, placeholder flags and strength/house proxies cannot become authoritative merely by copying them into that snapshot. `READY_EMPTY` means a valid calculation found no members; `MISSING` means no supply; `MALFORMED` means supplied content violated the contract; `VERSION_MISMATCH` and `UNSUPPORTED` retain their existing meanings. `ABSENT_ENTITY` is never used to mask capability unavailability.

Every ready enrichment includes deterministic evidence sufficient to reproduce the factual transformation: input identity/value, producer identity/version, exact knowledge artifact digest where applicable, formula/table key, boundary decision, and output identity/value. This is factual inference evidence. Prompt-08 dependency lineage remains separate and must not be copied into or substituted for it.

The implementation must not expand the exact seven prepared capability IDs. The addendum is the selected bounded exception: a separate V2 prepared profile, `aspects.whole_sign_graph@2.0.0` and `ASPECT_EXISTS@2.0.0`, with explicit source support and unchanged PredicateResult fields/statuses. V1 defaults, meanings, bytes and replay remain protected. No new predicate ID, node doctrine or production rule activation is permitted. Any predecessor-contract change beyond that exception remains a stop condition.

## 8. Astrology SME decision table

| Decision ID | Topic | Current behavior | Required decision | Downstream impact | Safe interim behavior |
|---|---|---|---|---|---|
| SME-FWP01-01 | Functional-role authority | Pinned tables plus an ungoverned heuristic fallback | Approve/correct the 12×9 table, allowed role labels, yogakāraka policy, and natural-role conditions | FWP03 role predicates and FWP04 interpretations | Retain existing v1 compatibility projection and `astrology_sme_approved: false`; strict lookup has no heuristic fallback and missing/unapproved facts stay unavailable |
| SME-FWP01-02 | D9 Navāṃśa | generic formula, shape tests | Select exact tradition and approve every sign-class/boundary vector | Marriage/dharma rules later | Strict D9 unavailable |
| SME-FWP01-03 | D3 Drekkāṇa | generic equal division | Select exact mapping and boundary rules | Sibling/courage rule prerequisites later | Strict D3 unavailable |
| SME-FWP01-04 | D7 Saptāṃśa | generic equal division | Select exact odd/even or other authorized mapping and boundaries | Children-domain prerequisites later | Strict D7 unavailable |
| SME-FWP01-05 | D30 Triṃśāṃśa | generic 30-way equal division | Select tradition, unequal/equal segments, ruler/sign output and boundaries | Adversity/condition prerequisites later | Strict D30 unavailable |
| SME-FWP01-06 | Node aspects | default/configurable seventh in current table/API | Approve whether Rahu/Ketu aspect, which offsets, and direction | Yoga and later governed rules | Preserve legacy v1 compatibility only; new factual node aspects unavailable |
| SME-FWP01-07 | Conjunction orb | same sign OR arbitrary 1° proximity | Decide whether conjunction is sign-based, degree-based, or both; approve orb and inclusive boundary | Aspect predicates and house influence | Strict same-sign only; degree-orb subtype unavailable |
| SME-FWP01-08 | Exaltation/debilitation | hard-coded false at boundary; mixed tables/flags/proxies | Approve signs, exact degrees, sign-vs-exact-point dignity semantics, nodes, and contradiction priority | Dignity and strength predicates | Preserve explicit sourced flags only; computed dignity unavailable |
| SME-FWP01-09 | Combustion | standalone Surya orbs; boundary false placeholder | Approve geocentric separation basis, planet orbs, retrograde exceptions and inclusive boundaries | Strength/condition rules | Unavailable unless an explicit authoritative source fact is supplied |
| SME-FWP01-10 | Classical Shadbala | weighted proxy components and aggregate | Approve component formulas, units, subcomponents, thresholds, benefic/malefic treatment and total | Any strength threshold rule | Expose existing values only as legacy proxy; classical components/total unavailable |
| SME-FWP01-11 | Natural benefic/malefic influence | fixed Moon/Mercury classifications | Approve waxing/waning Moon, Mercury association and any contextual conditions | House influence and Dṛk Bala | Do not compute new influence/pressure; keep legacy compatibility projection |

SME approval is required before any listed interim-unavailable capability is promoted to authoritative readiness. FWP01 implementation may still complete by proving deterministic typed unavailability and preserving compatibility; it must not guess the missing doctrine.

## 9. Compatibility and migration strategy

This is a parallel hardening of construction and factual publication, not a public migration.

- Preserve exact Career output, Yoga rows/order, v1 catalog and manifest, rules, rule revisions, weights, knowledge artifacts, Prompt-06/07/08 manifests, and snapshot bytes/hash.
- Preserve existing compatibility calls through the literal v1 authority and the exact defaults listed in §9.1. New strict construction uses separate named APIs, schema and models; neither data inspection nor strict-validation success silently migrates a caller.
- Do not edit pinned aspect, functional-role, or strength table bytes. An SME-approved semantic replacement requires a new governed artifact/version in a later separately approved change; it cannot silently rewrite v1.
- Preserve current general snapshot capability IDs/versions and all V1 prepared-state bytes for existing protected fixtures. Only the addendum's explicit V2 profile/component versions are exempted; other version changes remain a stop condition.
- Use Windows-first Python 3.11.9 only for development, tests, and CI.
- Frontend/TypeScript validation is not required because FWP01 is forbidden to change frontend-consumed output or TypeScript contracts. If evidence proves such a change necessary, stop for separate approval.

### 9.1 Explicit entry points, callers and route selection

The following table distinguishes **existing symbols** from **proposed** additions. `P/` below means `systems/Parasara/`. “Unchanged file” names a caller that may be read/tested but is not authorized for modification. Only the files in §§10.1–10.5 may be edited during a later implementation.

| Function/method and actual current callers | Route and input requirements | Error behavior | Authority handoff | Snapshot/projection behavior | Allowed implementation files |
|---|---|---|---|---|---|
| Existing `surya_to_parasara.generate_chart`, `build_planet_record`, `build_lagna_record`; called by `runner_api.generate_response`, producer `main`, MVP tests and `generate_chart` itself | Existing calls/defaults are compatibility. Proposed explicit `precision="strict_factual"` emits full-precision internal records under §5.5; the full chart still needs strict adapter validation | Default behavior unchanged; strict option rejects invalid numeric source/options, never retries legacy | Astronomy conversion selects no rule set and creates no authority | Emits chart mappings only; no freeze | `P/tools/surya_to_parasara.py` only; `runner_api.py` unchanged |
| Existing `SuryaAdapter.validate(data: Any) -> None`, `load(path: str) -> Chart`, `load_many(path: str)`; callers include `generate_snapshot.generate`, `varga_dump.main`, historical/normalizer tests and predecessor scenario manifests | Compatibility only. Keep `surya_input.schema.json`, existing `Chart` and batch `input` wrappers/current metadata handling. Three planets, partial houses and legacy numbering remain supported exactly as before | Current validation/Pydantic/file-error behavior retained; these APIs are not claimed to supply strict safe diagnostics | Loading alone neither resolves nor replaces authority | Returns compatibility models, not snapshots | Add strict siblings in `P/engine/adapter/surya_adapter.py` and separate models in `P/engine/models.py`; legacy schema and caller files unchanged |
| **Proposed** `SuryaAdapter.from_mapping_strict(data: Mapping[str, Any]) -> StrictChart`, `load_strict(path: str) -> StrictChart`; no current callers | Explicit strict selection; §5's nine-body, original-longitude, metadata and complete-or-empty-house contract; `load_strict` parses then invokes the same mapping validator | `StrictInputError(ValueError)` with ordered safe code/path issues; bounded file/JSON/schema/semantic failures, no private input/path leakage and no compatibility retry | Takes no rule-set selection parameter; does not resolve authority | Returns a defensively copied strict model only; no freeze | `P/engine/adapter/surya_adapter.py`, `P/engine/models.py`, new `P/schemas/surya_input_strict.schema.json` |
| **Proposed** `SuryaAdapter.from_mappings_strict(records: Sequence[Mapping[str, Any]]) -> StrictChartBatchResult`, `load_many_strict(path: str) -> StrictChartBatchResult`; no current callers | Explicit strict batch of plain chart mappings; each record uses `from_mapping_strict`'s exact validator. Historical wrapper objects belong to `load_many`, not implicit batch unwrapping here | Ordered per-record successes/issues retain zero-based indices. Top-level invalid JSON/file/batch shape raises `StrictInputError`; a failed record never becomes a legacy success | Same no-selection rule as strict single loading | No freeze during batch loading; build each successful strict chart deliberately | Same three files as strict single loading |
| Existing `chart_to_astrostate(chart: Chart) -> AstroState`; called by `generate_snapshot.generate`, `varga_dump.main`, compatibility fixtures/tests and predecessor manifests | Compatibility only. Preserve current partial-chart/house behavior and Aries-index-to-Lagna conversion for absent houses; do not infer a new route from metadata/count | Existing compatibility outcome retained; do not impose §5 on these calls | Normalization does not select or replace authority | Mutable compatibility construction; current enrichment/derived producers run before its caller freezes | Add siblings in `P/engine/normalizer.py`; existing legacy semantics preserved |
| **Proposed** `chart_to_astrostate_strict(chart: StrictChart, *, resolved_versions: ResolvedEvaluationVersions \| None = None) -> AstroState` and `derived.builder.build_derived_state_strict(astro: AstroState, *, resolved_versions: ResolvedEvaluationVersions \| None = None) -> dict[str, Any]`; no current callers | Strict construction only. Validate the strict model, preserve original longitude and source facts, use ascendant-relative houses directly and invoke strict producers; do not call the legacy normalizer/derived orchestration | Safe fatal required-fact issues; unsupported enrichments use typed unavailability. No broad fallback, legacy producer retry or legacy score substitution | Governed producer artifact checks use the caller's already selected manifest; no resolver call or authority replacement | Construction only; neither function freezes. Strict producers omit unapproved compatibility-only claims | `P/engine/normalizer.py`, `P/engine/derived/builder.py`, plus only the models/enrichment files in §§10.1–10.2 |
| **Proposed** `build_strict_snapshot(chart: StrictChart, *, resolved_versions: ResolvedEvaluationVersions \| None = None) -> AstroStateBuildOutcome` in `normalizer.py`; no current callers | Strict orchestration; caller must explicitly load a strict model first. No rule evaluation, domain output or public MVP migration | Required input/construction errors become existing `AstroStateBuildFailure` safe issues before publication; never return a successful legacy snapshot instead | With authority: keep that exact object, use its evaluation instant, call its existing `authorize_snapshot` on success and retain it for any later consumer. No authority: factual construction only, no implicit v1 resolution or governed evaluation | Passes the same `resolved_versions` to strict normalization, which calls `build_derived_state_strict` once with that object; after all producers complete, calls existing `freeze_astrostate` exactly once; returns existing success/failure types. Never freezes after evaluation | `P/engine/normalizer.py`; publication mechanics only in allowed `P/engine/astrostate_api.py`; `versioning.py` unchanged |
| Existing `freeze_astrostate(construction_state, *, capability_supplies=None, versions=None, evaluation_context=None) -> AstroStateBuildOutcome`; callers include `generate_snapshot.generate`, `assemble_output`, `prepare_career_facts`, `build_yoga_snapshot`, tests | Shared immutable publication of whichever construction the caller deliberately supplied; no automatic strict validation/promotion of legacy data | Existing typed `AstroStateBuildFailure` and readiness semantics preserved | Freeze itself selects no rule set and takes no resolved-authority argument; its caller retains that object | One freeze per completed construction run; preserve legacy logical bytes and strict route's separate facts/unavailability | Limited `P/engine/astrostate_api.py` producer-input validation/publication only; caller files otherwise unchanged |
| Existing `prepare_predicate_snapshot(snapshot, *, versions=None) -> PreparationOutcome`; called by `RuleEngine.evaluate_plan`, Yoga's `prepare_predicate_state` bridge, snapshot tests/manifests | Shared one-way seven-capability projection; this function is not a route selector and does not manufacture unavailable strict facts | Existing typed preparation/readiness results; no strict-to-legacy construction retry | Has no authority parameter: enclosing evaluation retains the same `ResolvedEvaluationVersions`, source bindings and predicate-version contract | Reads the immutable snapshot only; no producers or refreeze; exact existing compatibility projections remain protected | `P/engine/rules/snapshot_adapter.py` only if needed; `prepared_state.py` and graph/DSL owners unchanged |
| Existing Career `prepare_career_facts(astro)`, `prepare_career_snapshot(snapshot)`, `interpret_career(astro, *, engine_config=None, resolved_versions=None)`, `interpret_career_snapshot(snapshot, *, engine_config=None, resolved_versions=None)`; called by domain/output assembly, tools and tests | Existing compatibility/domain consumers remain on their current input route. FWP01 does not redirect public Career to strict facts or make legacy strengths classical | Current typed domain rejection/public-wrapper errors retained | Existing `resolved_versions` handoff remains exact; keep current v1 selection behavior when no authority was supplied to existing wrappers | Mutable wrapper publishes once for its own construction; snapshot form reads existing immutable facts and does not rebuild | Career files unchanged; compatibility characterized from the allowed test files |
| Existing Yoga `build_yoga_snapshot(astro, source)`, `evaluate_yoga_snapshot(snapshot, source=None, *, engine_config=None, resolved_versions=None)`, `evaluate_yoga_diagnostics(astro, *, engine_config=None, resolved_versions=None)`, `evaluate_yoga_rules(astro)`; called by domain/output assembly and tests | Compatibility wrappers retain current isolated role/aspect preparation. FWP01 strict construction must not call `build_yoga_snapshot` to acquire legacy facts; later explicit snapshot consumption cannot promote their authority | Existing build/preparation/diagnostic outcomes retained; strict failures never enter this wrapper as recovery | Typed diagnostics/snapshot evaluation carry the same supplied authority; legacy wrapper's current default selection remains unchanged | `build_yoga_snapshot` publishes its isolated compatibility construction once; `evaluate_yoga_snapshot` reads without producers/refreeze | `P/engine/enrichments/yoga_engine.py` unchanged; strict sibling producers live only in allowed enrichment files |
| Existing `generate_snapshot.generate(input_path: str, out_path: str)`, `assemble_output(astro)`, `assemble_snapshot_output(snapshot)`, `evaluate_snapshot_record(snapshot, *, engine_config=None, resolved_versions=None, replay_of_manifest_sha256=None)`; called by MVP, CLI, replay and tests | Public compatibility generation stays `load -> chart_to_astrostate -> freeze`; no strict substitution. Direct snapshot consumers retain current contracts and are not activated for new strict rule interpretation by FWP01 | Existing build errors and evaluation/replay contracts retained | `generate` uses current `_resolve_snapshot_versions`; consumers with supplied authority keep its exact object through Career/Yoga/assembly | Existing public bytes/order and predecessor snapshot identities unchanged | `P/tools/generate_snapshot.py` unchanged |
| Existing `runner_api.generate_response(birth: ValidatedBirth)`, private `_legacy_engine_chart(public_chart)`, `run_request(data: Any)`; called by the MVP runner and boundary tests | Public MVP stays default producer -> copied `_legacy_engine_chart` -> compatibility `generate_snapshot.generate`. The copy's `aries_sign_index_for_protected_normalizer` house numbering never enters the strict adapter/normalizer | Current public request/error envelope retained | Existing downstream v1 authority selection/handoff unchanged; no new selection in the runner | Public `surya_chart`, Career projection and output snapshots stay exact; no strict construction occurs in this public route | `P/tools/runner_api.py` unchanged; additive tests in existing `test_mvp_chart_boundary.py` and new §10.4 tests |

**Deliberate strict use after implementation:** call `generate_chart(..., precision="strict_factual")` (or supply genuinely sourced original longitudes), then `SuryaAdapter.from_mapping_strict(payload)`, then `build_strict_snapshot(chart, resolved_versions=already_resolved_versions)`. A file caller chooses `load_strict`; a batch caller chooses `load_many_strict` or `from_mappings_strict` and constructs only successful records. Compatibility callers continue calling their existing symbols unchanged. No dispatch may depend on planet count, absent metadata, an exception, CWD, environment variables, readiness, or whether a record happens to pass strict validation.

`StrictChart`, `StrictChartBatchResult` and their ordered issue/result value types are proposed additions in `engine/models.py`, separate from existing `Chart`, `Planet`, `Lagna` and `Metadata` contracts. `StrictInputError` is proposed in the adapter. The new strict JSON schema is repository-anchored and never replaces `SuryaAdapter.SCHEMA_PATH` or the existing schema's legacy meaning. New strict models retain `house_numbering`, original longitude, nakshatra and motion facts rather than losing them through the current legacy model's ignored extra fields.

Strict producer variants/branches are opt-in through `build_derived_state_strict`, not changes to existing enrichment defaults. Unsupported doctrine remains typed unavailable; existing role/strength/varga/node compatibility projections stay on legacy constructions and cannot satisfy new strict readiness. Prepared-state projection does not bypass this boundary. A governed caller retains one exact `ResolvedEvaluationVersions` object throughout; standalone strict construction never resolves a rule set. Prompt-07 compiler/predicate ownership, Prompt-08 dependency lineage and same-authority/atomic-ledger ownership, and `RuleEngine`'s sole `RuleMatch` ownership remain unchanged. No new rule execution is authorized.

Future `tests/fwp01/test_entry_point_routing.py` proves strict success with all nine bodies; deterministic strict single/batch failures; explicit continued support for the unchanged three-planet/two-house golden, partial legacy houses and MVP Aries-index copies; absence of automatic strict-to-legacy fallback; one freeze per strict run; immutable projection; and unchanged supplied authority identity. `test_compatibility_and_boundaries.py` and existing public characterization tests prove exact Career/Yoga order, default producer/MVP output, snapshot and predecessor scenario bytes. The same historical payload failing strict validation and succeeding through an explicitly called compatibility API is expected, not a recovery strategy.

The addendum separately defines the proposed authority-bound `prepare_predicate_snapshot_v2(snapshot, *, resolved_versions)` entry and versioned evaluator/compiler path. The existing §9.1 table describes V1 and retains its signatures, default routes and public callers. No implicit migration or production graph/corpus activation follows from adding V2.

## 10. Bounded implementation plan

### 10.1 Authorized production files expected to change

Only the following existing production/configuration files are authorized, and each change must be attributable to a requirement above:

```text
systems/Parasara/tools/surya_to_parasara.py
systems/Parasara/engine/models.py
systems/Parasara/engine/adapter/surya_adapter.py
systems/Parasara/engine/astrostate.py
systems/Parasara/engine/identities.py
systems/Parasara/engine/normalizer.py
systems/Parasara/engine/enrichments/canonical_ids.py
systems/Parasara/engine/enrichments/precision.py
systems/Parasara/engine/enrichments/functional_roles.py
systems/Parasara/engine/enrichments/varga.py
systems/Parasara/engine/enrichments/aspects.py
systems/Parasara/engine/enrichments/planet_strengths.py
systems/Parasara/engine/enrichments/shadbala.py
systems/Parasara/engine/derived/models.py
systems/Parasara/engine/derived/builder.py
systems/Parasara/engine/astrostate_api.py
systems/Parasara/engine/rules/snapshot_adapter.py
```

`surya_to_parasara.py` changes are limited to the precision option, unrounded strict record fields and option propagation in §5.5. Existing default/CLI behavior and public shapes remain exact; no astronomical/ayanamsa/doctrine change or unrelated refactoring is authorized. `models.py` and `surya_adapter.py` add separate strict models/APIs rather than tightening existing compatibility classes/calls. `normalizer.py` and `derived/builder.py` add the named strict orchestration while keeping legacy defaults. The existing `schemas/surya_input.schema.json` is protected; strict validation uses the new schema in §10.2. `astrostate_api.py` changes are limited to validating/publishing existing capability IDs and preserving existing queries/versions. `snapshot_adapter.py` preserves V1 output and may add only the separately named V2 entry defined by the addendum. These original lists do not widen the remaining V2 task: its exact modify/add list is solely in addendum §5. No executable edit is authorized during this documentation session.

### 10.2 Exact production files expected to be added

```text
systems/Parasara/schemas/surya_input_strict.schema.json
systems/Parasara/engine/enrichments/house_conditions.py
tools/validate_fwp01.py
```

`surya_input_strict.schema.json` owns only the additive opt-in §5 contract; it must not change the existing schema, public chart default or Surya engine contract. Strict model/adapter APIs stay in existing allowed files; no additional entry-point module is needed. `house_conditions.py` owns the non-interpretive strict house fact assembly described in §6.1. It must not calculate a life-domain score. The validator is repository-root anchored, read-only except for OS temporary directories, and leaves no repository artifacts.

### 10.3 Protected and forbidden production changes

Do not modify:

```text
systems/Parasara/schemas/surya_input.schema.json
systems/Parasara/tools/runner_api.py
systems/Parasara/tools/varga_dump.py
systems/Parasara/engine/rules/prepared_state.py
systems/Parasara/engine/rules/dsl/**
systems/Parasara/engine/rules/graph/**
systems/Parasara/engine/versioning.py
systems/Parasara/config/versioning/**
systems/Parasara/rules/parashara/v1/rule-set-manifest.json
systems/Parasara/enrichment_tables/functional_roles/**
rules/parashara/aspects.yaml
rules/parashara/strength_tables/**
systems/SuryaSiddhanta/**
systems/Parasara/engine/dasha/**
systems/Parasara/engine/domain/**
systems/Parasara/engine/inference/**
systems/Parasara/engine/interpreters/**
systems/Parasara/engine/output_assembler.py
systems/Parasara/tools/generate_snapshot.py
frontend/**
```

The cumulative Prompt-06–08 modifications to some forbidden files remain untouched. Personal exports and unrelated documents remain byte-identical. The sole V2 exceptions to this forbidden-path list are the listed integration changes in `engine/versioning.py` and addition of `engine/rules/dsl/compiler_v2.py`, governed by addendum §5 after a separate implementation instruction. V1 DSL files, `prepared_state.py`, `canonical_predicates.py`, graph files, production catalogs/manifests, corpus and knowledge artifacts remain unchanged. The addendum also lists the exact registry, adapter, evaluator, test and validator scope; no wildcard exception is granted.

### 10.4 Exact tests expected to be added

```text
tests/fwp01/scenario_manifest.py
tests/fwp01/test_input_contract.py
tests/fwp01/test_producer_precision.py
tests/fwp01/test_entry_point_routing.py
tests/fwp01/test_normalization_and_identity.py
tests/fwp01/test_house_facts.py
tests/fwp01/test_functional_roles.py
tests/fwp01/test_vargas.py
tests/fwp01/test_aspects_and_conjunctions.py
tests/fwp01/test_strength_and_conditions.py
tests/fwp01/test_snapshot_capabilities.py
tests/fwp01/test_determinism.py
tests/fwp01/test_compatibility_and_boundaries.py
```

### 10.5 Existing tests expected to change

Only these existing test files may be tightened to replace weak structural assertions, characterize preserved behavior, or add explicit strict input/precision/routing coverage. Their existing compatibility scenarios and expected protected bytes remain unchanged; strict assertions use the proposed strict APIs, not a silent migration of old fixtures:

```text
systems/Parasara/tests/test_validator_and_adapter.py
systems/Parasara/tests/test_phase2_normalizer.py
systems/Parasara/tests/test_phase1_phase2_enrichments.py
systems/Parasara/tests/test_mvp_chart_boundary.py
tests/enrichments/test_varga_d9.py
tests/enrichments/test_varga_more.py
tests/enrichments/test_aspects.py
tests/enrichments/test_parashara_aspects.py
tests/enrichments/test_functional_roles_matrix.py
tests/enrichments/test_planet_strengths.py
tests/enrichments/test_shadbala_components.py
tests/enrichments/test_shadbala_golden.py
tests/astrostate/test_astrostate_api.py
tests/astrostate/test_architecture.py
```

No protected golden or predecessor scenario manifest is updated merely to make a failure pass. New astrology oracle vectors require SME approval recorded by decision ID.

### 10.6 Existing code to reuse

- `engine.identities.CANONICAL_PLANETS` and `normalize_planet_id` as the single identity authority;
- `AstroStateSnapshot`, `CapabilitySnapshot`, `AstroQueryResult`, `freeze_value`, and `freeze_astrostate` for immutable publication;
- existing capability readiness/fact-state enums and safe diagnostics;
- `snapshot_adapter.prepare_predicate_snapshot` and protected `PreparedAstroState` projection;
- Prompt-06 resolved authority and manifest artifact-digest verification;
- the existing Lahiri/whole-sign boundary functions and Surya signed longitudinal speed, retaining original converted longitude for strict records under §5.5;
- current public snapshot generator only as a read-only compatibility oracle.

### 10.7 APIs to add, restrict, and preserve

- **Add, all proposed:** the three producer functions' opt-in precision keyword (§5.5); `SuryaAdapter.from_mapping_strict`, `load_strict`, `from_mappings_strict`, `load_many_strict`; separate `StrictChart`/`StrictChartBatchResult` and safe issue types; `StrictInputError`; `chart_to_astrostate_strict`, `build_derived_state_strict`, `build_strict_snapshot`; strict house-condition producer.
- **Restrict only the strict route:** all strict loading APIs share one schema/semantic validator; strict roles/aspects use approved manifest-pinned artifacts; strict varga/strength claims require approved readiness; mutable access is construction-only. Neither legacy `load_many` nor legacy `load` is silently tightened to the nine-body contract.
- **Preserve:** existing `SuryaAdapter.validate/load/load_many`, `chart_to_astrostate`, producer defaults and public MVP/Career/Yoga routing; existing `Chart` and schema meaning; `AstroStateSnapshot` query names/versions, capability states, protected prepared-state APIs/bytes, same-object v1 authority and all Prompt-01–08 contracts. Exact proposed signatures, errors and file ownership are in §9.1.

### 10.8 Capabilities to complete vs intentionally unavailable

On valid strict input, FWP01 completion requires correct full-precision metadata/location/Lagna, nine normalized planets, placements, 12 houses, lords/occupants and preserved sourced non-node motion. Enrichment facets obey the existing ready/malformed/unavailable contract, including strict house facets, role facts and approved classical-planet whole-sign aspects. Invalid required input yields a strict failure, not an unavailable core attached to a successful legacy snapshot. Existing compatibility scenarios retain their exact ready states/bytes without being relabeled strict.

Classical D9/D3/D7/D30, node aspects, degree-orb conjunction, computed combustion, computed exaltation/debilitation, full Shadbala and every unimplemented Shadbala component may remain unavailable after FWP01 unless the corresponding SME decision is approved before implementation. Dasha/transit remain unavailable and belong to FWP02.

### 10.9 Ordered implementation and stop gates

1. **FWP01-A:** characterize public bytes/defaults, explicit caller routes and protected hashes first; add only §5.5's opt-in producer precision remedy and §9.1's separate strict schema/models/adapter/normalizer/build entry. Prove precision transitions, strict/legacy isolation, safe failures, zero/boundary/mutation cases and unchanged public default behavior. Missing historical precision is a per-record strict error, not reconstruction or fallback; stop if obtaining genuine source precision would require changes beyond the bounded producer scope.
2. **FWP01-B:** centralize house facts; pin roles/aspects to existing manifest artifacts; make varga availability obey SME decisions; prove evidence and ordering. Stop if a pinned artifact must change.
3. **FWP01-C:** separate strict facts from legacy strength/house compatibility; propagate motion/flags truthfully; prove no fabricated values. Stop if current public Career/Yoga bytes cannot be preserved.
4. **FWP01-D:** compose the FWP01 validator with Prompt-01 and Prompt-04 through Prompt-08 gates in one Python 3.11.9 campaign, including full tests, manifests, artifact checks and worktree checks without duplicate compatibility runs. Stop on drift outside the explicit addendum exception.

### 10.10 Remaining V2 implementation boundary

The addendum's exact file list, call-signature constraints, outcome table and finite validation plan govern the remaining V2 correction. It authorizes the bounded predecessor-contract extension as a specification decision; production/test implementation still requires a separate instruction. Additional dependencies must be identified by exact file/reason before extending scope. Synthetic V2 fixtures are non-production only, and V2 graph-enabled manifests are rejected before plan issuance.

## 11. Deterministic validation design

### 11.1 Focused commands

Use the selected Python 3.11.9 environment. The composed validator is the implementation acceptance campaign; run the focused command separately only for purposeful development/failure investigation, not merely to duplicate its successful component results:

```powershell
& 'jyothishyam_env/prompt01-py311/Scripts/python.exe' -m pytest -q tests/fwp01
& 'jyothishyam_env/prompt01-py311/Scripts/python.exe' tools/validate_fwp01.py --lane py311
```

The validator composes accepted predecessor gates using the selected interpreter, including `tools/validate_prompt01.py`, `tools/validate_prompt04.py`, `tools/validate_prompt05.py`, `tools/validate_prompt06.py`, `tools/validate_prompt07.py` and `tools/validate_prompt08.py`. Run the full repository suite once; Prompt-02/03 remain included through composition. Preserve same-runtime determinism checks. Missing original evidence remains INCOMPLETE; do not invent a historical baseline. Updating validator integrity pins/scope and eliminating duplicate compatibility invocations is future work within addendum §5, not part of this documentation task.

### 11.2 Scenario manifest

`tests/fwp01/scenario_manifest.py` emits canonical JSON bytes only. Scenarios include:

- the protected golden chart and synthetic MVP chart through their unchanged compatibility entry points; independently supplied complete strict charts through the proposed strict entries;
- every canonical planet and Kethu alias normalization;
- exact `0°`, every sign transition and both adjacent sides, planet/Lagna `29.99996°`, `13.33334°` and other values rounding across nakshatra/pada boundaries; absolute-source `360°` normalization versus rejection of supplied within-sign `30°`; negative/out-of-range, Boolean, NaN and infinity cases;
- original-longitude consistency; absent/lost historical precision producing deterministic strict failures; default producer records remaining unchanged;
- explicit strict single/batch success and errors versus continued three-planet, partial-house and legacy-numbering compatibility success; no exception-, metadata-, environment- or count-based route switch and no strict-to-legacy fallback;
- all 12 Lagna signs and houses;
- absent/partial/contradictory houses, duplicate/missing planets and contradictory nakshatra/pada;
- input mutation before/after freeze;
- role/aspect tables found from repository root and safe alternate CWDs;
- empty aspect targets, same-sign conjunctions, unsupported orb/node cases;
- every SME-unapproved fact returning typed unavailability;
- stable snapshot queries, evidence order, canonical bytes and digest.

The same bytes and SHA-256 must result under Python 3.11.9, `PYTHONHASHSEED` values `0`, `1`, `42`, and `random`, at least two safe working directories, and repeated cold/warm runs. Paths, timestamps, environment values, object addresses, logs, cache state, and random identity are absent.

### 11.3 Protected checks

Validation fails unless:

- public snapshot is exactly 4,041 bytes with SHA-256 `da2059ba3cfb92eed267f93d1e41585dac1422d68f685022c8609cfd04ad57af`;
- Career and Yoga logical/public characterization bytes and order remain exact;
- current v1 catalog and manifest bytes/fingerprint remain exact;
- Prompt-06, Prompt-07, and Prompt-08 scenario manifests/hashes remain exact;
- `prepared_state.py` remains 51,241 bytes with SHA-256 `a2fca2dd17edd7092e8bee1cc8431891400d09f979a90f4f44d17b71c9466970`;
- all protected artifacts and personal exports match the pre-implementation inventory;
- no generated file appears in the repository;
- private tracker remains ignored, untracked, unstaged and absent from all delivery inventories;
- `git diff --check` passes and staged files remain none.

### 11.4 Full acceptance checklist

FWP01 is complete only when every item is true:

- [ ] Named strict mapping/file/single/batch APIs share one validator and separate strict schema/models; legacy entry semantics remain unchanged.
- [ ] Producer `precision="strict_factual"` derives and serializes facts from original unrounded longitude; default/CLI/public producer output is preserved.
- [ ] Planet/Lagna 29.99996, zero, sign transitions and nakshatra/pada rounding-crossing vectors pass; strict within-sign 30 and missing original precision fail without repair/fallback.
- [ ] §9.1's explicit strict/compatibility routes preserve the three-planet golden, partial houses and legacy numbering; no automatic dispatch or strict-to-legacy recovery exists.
- [ ] A strict construction freezes once after all strict producers; projection/evaluation never refreezes or promotes legacy facts, and supplied authority identity is preserved.
- [ ] Required fields/types/units/ranges and metadata invariants are enforced.
- [ ] Kethu is accepted as an edge alias and Ketu is the sole internal identity.
- [ ] All nine required bodies, Lagna, 12 houses, placements, nakshatra and pada agree.
- [ ] Zero/boundary values are preserved and invalid/contradictory values fail safely.
- [ ] Mutable inputs cannot alter published snapshots/digests.
- [ ] No required construction error is swallowed or converted to a fallback.
- [ ] House ownership, occupancy, lord placement and approved aspects are deterministic and traceable.
- [ ] Role/aspect lookup is repository-root anchored and v1-manifest-pinned.
- [ ] No heuristic role fallback satisfies the strict capability.
- [ ] D9/D3/D7/D30 are either SME-approved with exhaustive boundary vectors or explicitly unavailable.
- [ ] Node aspects and degree-orb conjunctions obey the same approval/unavailability rule.
- [ ] Combustion, retrogression and dignity distinguish sourced fact from unknown; no placeholder false is published as fact.
- [ ] Legacy strength and house scores remain explicitly compatibility/proxy scoped.
- [ ] Full classical Shadbala is never claimed; missing components are typed unavailable.
- [ ] Dasha/transit remain typed unavailable and no FWP02 code is added.
- [ ] Existing snapshot/prepared query semantics and deterministic ordering remain exact.
- [ ] Focused and full tests pass on Python 3.11.9; do not duplicate runs for compatibility.
- [ ] Scenario bytes match across hash seeds, CWDs and fresh-process/cold-warm repetitions on Python 3.11.9.
- [ ] All predecessor validators and protected-artifact checks pass.
- [ ] Public Career/Yoga and 4,041-byte snapshot remain exact.
- [ ] No v1 catalog/manifest, rule corpus, knowledge table, Prompt-06/07/08 manifest, protected report, or personal export changes.
- [ ] No frontend/TypeScript change occurred.
- [ ] No files are staged; no commit, push, PR, merge, branch operation, or GitHub delivery occurred.
- [ ] One independent implementation review finds no blocker/high/medium issue, then the user separately accepts FWP01.

## 12. Mandatory stop conditions

The exact additive V2 extension in the addendum is the selected exception to the predecessor-contract/file/version restrictions below. It does not permit changing V1 semantics or historical artifacts and does not start implementation in this documentation session. Stop implementation for any change beyond that exact exception if any of the following occurs:

- a Surya public-contract/astronomical-engine, ayanamsa or doctrine change appears necessary, or the producer remedy exceeds §5.5's opt-in Parāśara conversion/serialization scope;
- preserving unrounded strict facts requires changing default producer/public MVP output, silently tightening a legacy entry, guessing historical precision, repairing contradictory evidence or falling back from strict failure;
- an existing Prompt-01–08 type, capability ID/version, snapshot schema, serializer, manifest, or protected digest must change;
- a v1 rule, weight, order, table value, rule-set lifecycle state, or authority identity must change;
- public Career/Yoga output or the protected snapshot changes;
- an astrology formula/table/orb/threshold/exception lacks an approved repository authority;
- strict completion would require a new predicate, DSL corpus migration, production graph activation, timing integration, domain interpretation, public API, frontend, or deployment change;
- an additional production/test file outside the exact authorized lists is required;
- the worktree cannot be distinguished safely from cumulative Prompt-06–08 or personal user work;
- deterministic scenario equality on Python 3.11.9 cannot be obtained without weakening a test or updating a protected oracle.

## 13. Final specification disposition

Both reported specification findings are resolved by the bounded plan: §5.5 defines one authorized opt-in producer precision remedy, and §9.1 defines executable strict/legacy routing using actual existing symbols plus clearly proposed additions. §§10–12 align the future file/test scope, validation, acceptance and stop gates. The targeted correction self-check does not constitute implemented or tested strict APIs, an independent review repeat, user implementation acceptance, or an additional specification approval stage.

FWP01 remains bounded without changing Surya astronomy or V1 predecessor behavior. The addendum specifies the sole versioned predecessor extension for the remaining aspect conflict. Unapproved astrology features remain explicitly unavailable until their existing SME decisions are approved. Current v1 public/default compatibility and protected scenario bytes stay on their existing route. The historical DOCX preservation limitation in §2.2 remains unresolved as clarified by §2.3; current readability does not establish historical preservation.

This session changes documentation only and stops after the bounded correction and evidence report. It does not start or authorize FWP01 implementation, FWP02, Prompt-09, GitHub delivery or branch cleanup. Future implementation requires a separate instruction to begin; no new specification-review/approval round is introduced by this correction.
