# Prompt-04 — AstroState API implementation

Status: IMPLEMENTED — REMEDIATED, PENDING FINAL APPROVAL CHECK
Authority: approved Prompt-04 AstroState API specification
Owner: Parāśara engine maintainers
Last verified: 2026-08-21

## Implemented boundary

Prompt-04 adds one immutable, deterministic post-construction factual boundary:

```text
Chart -> mutable AstroState construction -> explicit producers
  -> freeze_astrostate -> AstroStateSnapshot -> typed factual queries
```

`engine/astrostate_api.py` owns frozen core facts, the composed general
capability catalog, construction issues, the closed success/failure build
union, canonical serialization, SHA-256 digest, and read-only queries.
`engine/astrostate.py` remains only the bounded mutable construction and
compatibility model.

The general catalog retains all seven Prompt-01 capability definitions at
`1.0.0` while adding chart, house, dignity, varga, strength, Dasha, and transit
areas required by the stable API. Core-backed capabilities reference their one
canonical owner; independent supplies for those capabilities are rejected.
Public constructors and `dataclasses.replace` defensively copy and recursively
freeze nested values. Capability construction enforces the catalog version,
core-path ownership, readiness/content/empty-state matrix, and safe issues;
snapshot construction revalidates every core-backed capability against its
`AstroCore` owner after direct construction or replacement. Factual presence
flags are intrinsic model invariants. Successful and failed build issues use
the same typed canonical ordering, and evaluation context accepts only the
supported factual `instant`. Basic-conjunction and whole-sign aspect
representations remain separate, every published planet endpoint belongs to
the snapshot's core entity set, whole-sign planet target signs must agree with
the target planet, and sign/house queries map through canonical snapshot facts.
Invalid supplied aspect endpoints or shapes produce a deterministic fatal build
failure with no snapshot; facts are not silently discarded or converted to
ready-empty. Nonfatal `malformed` readiness remains available only for bounded
capability availability or producer outcomes without invalid supplied facts.

## Consumer migration

- `rules/snapshot_adapter.py` projects snapshot facts into the exact protected
  `PreparedAstroState` view; all seven capability bytes and digests remain exact.
- Yoga runs only its existing whole-sign aspect and functional-role producers
  before freeze, then evaluates the immutable snapshot. Its mutable wrapper,
  public rows, typed logical bytes, firing, order, and traces remain exact.
- Career builds its factual bridge through explicit snapshot queries and keeps
  its completeness policy outside AstroState. RuleMatches, InferenceResult,
  score, confidence, evidence, narrative, trace identity, and public JSON remain
  exact. Canonical Career evaluation propagates unexpected programming defects;
  expected factual unavailability remains a typed neutral/error result.
- The snapshot assembler, legacy completeness helper, and varga tool consume
  the immutable boundary while preserving their compatibility entry points.

The mutable `evaluate_yoga_rules(AstroState)`, `prepare_career_facts(AstroState)`,
`interpret_career(AstroState)`, and `assemble_output(AstroState)` wrappers remain
one-direction adapters. Their owner is the Parāśara engine; later removal or
further thinning belongs to approved typed-domain/output work, not Prompt-04.

## Availability truth

Current planet, house, aspect, dignity, varga, role, strength, and partial
Shadbala facts are represented with explicit readiness and factual scope.
Shadbala is labeled `legacy_partial_proxy`. No integrated current Dasha or
transit producer exists, so those queries return typed unavailable outcomes.
Missing data never becomes adverse domain evidence inside AstroState.

## Compatibility locks

- Career public hashes: `74442a…`, `fee279…`, `169cf5…`.
- Yoga public hash: `d6ad3c…`; typed logical hash: `8b639e…`.
- approved MVP snapshot: 4041 bytes, `da2059…`.
- current WP17 manifest: `75b65…`; Prompt-03 manifest: `f57bc2…`.
- Prompt-04 cross-lane snapshot/query manifest:
  `440a459cc60e9575874341e7c6673e714585ae79123957c9c19ccd175cb7930b`.
- legacy varga outputs: golden 5,752 bytes / `f13f8ea89ba972d4936bc7e4547f4fe6d629cc1603943b02e92a311406086b98`;
  Surya test 20,380 bytes / `0f82ee03920845d155cf299bea81fb9fab24e69fe3c94108101c9fa6e7d0a133`;
  Surya generated 19,729 bytes / `c896599cd87358a2023e6a2937ffb281699f95b4e9a7c5850f2ee2fb6a3cc888`.
- rule files, protected artifacts, and four personal exports are unchanged.

The Prompt-04 manifest changed from
`380b07be61e2f228ec01907ae094fe8e3494b30bf9cabeaa60bb761b9a31821a`
because aspect query rows now retain the whole-sign `target_sign` field (and
encode it as `null` for basic-conjunction rows). Snapshot logical digests and
all prepared-state hashes remain unchanged. The new hash reproduced across
both Python lanes, three hash seeds, fresh processes, and repository and
OS-temporary working directories.

## Manifest resolution

The raw Prompt-01 full validator and historical digest remain preserved as
historical evidence. Current Prompt-01 integrity is composed through WP17 and
Prompt-02. `tools/validate_prompt04.py` runs WP17 plus current Prompt-02,
Prompt-03, and Prompt-04 gates; it never runs the raw historical Prompt-01 full
gate against current HEAD. The historical WP06/WP07 capability-fingerprint
documentation discrepancy remains deferred.

## Validation

Use Windows and both supported lanes:

```powershell
& 'jyothishyam_env/prompt01-py311/Scripts/python.exe' tools/validate_prompt04.py full
& 'jyothishyam_env/prompt01-py314/Scripts/python.exe' tools/validate_prompt04.py full
```

Focused and full validation pass under Python 3.11.9 and 3.14.6. Each full
lane collected 912 nodes and completed with 910 passed and 2 skipped. Each
lane also passed Prompt-02/03 focused contracts, all 62 Prompt-04 tests, all 22
WP17 checks, all three deterministic manifests, rule lint, the strict approved
snapshot, 24 protected artifacts, four protected exports, and worktree
mutation checks. The standalone Prompt-02 and Prompt-03 full validators also
pass in both lanes after implementation. The frontend Next.js production build
compiled, type-checked, linted, and generated all 14 pages/routes.

Remediation evidence includes 38 total fixed remediation cases. It rejects
core/capability replacement disagreement,
catalog/version/core-path and presence-flag contradictions, canonical but
snapshot-absent or unknown aspect endpoints, malformed endpoint shapes, and
whole-sign target-sign disagreement before snapshot publication. It separately
preserves nonfatal malformed capability availability, and proves that injected
`RuntimeError` defects propagate from both canonical Career paths while expected
factual unavailability remains typed. All remediation findings R1-R10 are
verified; Prompt-04 acceptance gates pass pending the final independent approval
check.

The validator records only personal exports present at startup. A clean
checkout with none present proceeds, while an initially present export that is
modified, deleted, or renamed fails protection checks. The legacy varga tool
again emits byte-identical output using snapshot metadata/location queries.

A bounded Python 3.11 diagnostic benchmark on `surya_test_chart.json` measured
approximately 2.099 ms per freeze (200 iterations), 0.149 ms per 14-query
bundle (2,000 iterations), 53.983 ms per Career evaluation (50 iterations),
and 31.072 ms per Yoga evaluation (20 iterations), with an 80,429-byte traced
peak for one freeze. These are local diagnostic observations, not release SLAs.

This evidence establishes structural and deterministic compatibility only. It
does not imply scientific/SME, release, privacy, security, licensing, or
operational approval. Mutable construction compatibility, partial/proxy
Shadbala, unavailable integrated Dasha/transits, and legacy discovery paths
remain explicit limitations outside this remediation.
