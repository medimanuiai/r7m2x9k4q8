# Prompt-05 Remediation R4

Status: IMPLEMENTATION-VALIDATED — INDEPENDENT FINAL R4 REVIEW PENDING

Date: 2026-08-29

Branch and unchanged HEAD: `main` at
`c719a1bf686e1e37eb8542f9323fc279b670250e`

## Governing review and decision

The Independent Final R3 Review failed two provenance contracts: late Career
configuration/projection substitution and caller-batch authority for
contribution-free indicator lineage. The user approved
`Decisions/Prompt-05-Provenance-Architecture-Decision.md` as the governing R4
architecture.

R4 implemented the bounded private Career same-run value, complete private
RuleMatch ledger, stored same-config inference compatibility projection,
sealed evaluated `DomainIndicator` construction, one-way evaluated domain/Yoga
DTOs, removed evaluated deserializers from public exports, removed the public
late `InferenceEngine.compatibility_projection(result, config)` method, and
made canonical Yoga evaluation construct diagnostics inside the evaluator
boundary. `RuleMatch` became the sole value used by the R4 Yoga projection for
matched state and status. The fourteen required supported-operation attacks
were added in `tests/domain/test_remediation_r4.py` and passed under Python
3.11.9.

## Exact predecessor-contract conflict

The required Prompt-02/WP17 manifest cannot remain exact while the approved R4
Yoga authority rule is enforced.

WP17 scenario `06.yoga.explicit_permutations` deliberately runs after earlier
stateful scenarios. In each of its five permutations, `rajayoga_naive` retains:

- `RuleMatch.status == invalid`;
- `RuleMatch.matched is False`;
- `condition_result.status == matched`;
- `condition_result.matched is True`.

The inherited public projection promotes the condition result over that
RuleMatch. Its locked aggregate is 527 bytes with SHA-256
`299fbabbe6c94e8c27d6a63235b63e64c22e8da1a9a93db8002b54b317c2c8ff`.
Using `RuleMatch` as the sole matched-state authority preserves the 527-byte
shape but changes the aggregate SHA-256 to
`1c49e3aa9c25d67b39681980c335ab9dc7287a22c6cfb6c666a5651c6df29f5f`.

Consequently the composed Prompt-02/WP17 manifest changes from the required
`75b65d2cd1420c6261aadbb8159d10fb8c641137ce08d29f2a651952e5cdfaf7`
to the observed 1,899-byte manifest SHA-256
`06330b43cac062239e0670d1e48ab00c328ee270af64023b2017b819dc7b3017`.
Restoring the old hash requires restoring the exact condition-result truth
override prohibited by the approved decision. Changing the retained
`RuleMatch` would instead change the protected Prompt-02 logical contract and
still violate the predecessor-manifest requirement.

No protected real-chart fixture was found to depend on the disagreement. The
conflict is nevertheless part of the exact inherited Prompt-02/WP17 manifest,
which R4 was explicitly forbidden to change.

## Prompt-02/WP17 Yoga reconciliation

The user authorized a predecessor-baseline correction on 2026-08-29 with this
precedence: the governing Prompt-02 RuleMatch contract, then the approved R4
provenance decision, then legacy WP17 fixture/manifest evidence.

Prompt-02 Sections 4, 9, 10, 11, 13, and 14 establish that status is the
authoritative rule outcome, `matched` is constrained by status, RuleMatch owns
rule outcome/evidence/trace, and the Rule Engine returns RuleMatch before a
compatibility projection. The specification contains no clause allowing a
condition Boolean to override an invalid or unmatched RuleMatch. The old
override was therefore subordinate executable compatibility evidence, not a
normative Prompt-02 requirement.

The authorized correction preserves the R4 production implementation and
changes only the current Prompt-02/WP17 expectation and its executable
semantic guard:

| Predecessor baseline file | Old file SHA-256 | New file SHA-256 | Exact semantic difference |
|---|---|---|---|
| `tests/wp17/scenario_manifest.py` | `6610d85308731cd867b2b3ba29c1f28c8336c292bfeaec8e7224310fd0f5dc9f` | `45debae8158344dc6daffab52fac317f0c8453a1a2034022bbd58c1c7f113985` | Asserts every public Yoga `matched` value comes from RuleMatch and pins the five expected `rajayoga_naive` invalid/condition-true conflicts; emitted bytes are otherwise unchanged. |
| `tests/wp17/test_determinism_subprocess.py` | `258ec46989ba7a83513c588e0b5bfb93ca83d81befbc22ff3d16fe3117137b75` | `ab3965c1457e119d7561d53372f072b9e21f2319926dd5671d998d82a6b82e39` | Pins the corrected Yoga scenario row and replaces only the superseded Prompt-02/WP17 aggregate digest. |
| `tools/validate_prompt02.py` | `116ace8e804ed98b80381d4b7b7c199925655af4fd927b24ab1338929aa7cb57` | `ab5f29f2448dc1d5e46a5f91edcda466eb326ffe37d5112bbb97321182b45179` | Replaces only `EXPECTED_PROMPT02_MANIFEST_SHA256` with the reconciled digest. |

The 1,899-byte manifest differs semantically only at
`scenarios[5].public_sha256`: old Yoga public aggregate
`299fbabbe6c94e8c27d6a63235b63e64c22e8da1a9a93db8002b54b317c2c8ff`,
new Yoga public aggregate
`1c49e3aa9c25d67b39681980c335ab9dc7287a22c6cfb6c666a5651c6df29f5f`.
Reconstructing the old manifest by changing only that field reproduces
`75b65d2cd1420c6261aadbb8159d10fb8c641137ce08d29f2a651952e5cdfaf7`.
The corrected manifest is
`06330b43cac062239e0670d1e48ab00c328ee270af64023b2017b819dc7b3017`.

The approved snapshot did not change: 4,041 bytes and SHA-256
`da2059ba3cfb92eed267f93d1e41585dac1422d68f685022c8609cfd04ad57af`.
Prompt-03 and Prompt-04 manifests also remain exact. Historical reports retain
their old hashes as historical evidence. Full reconciliation lineage is in
`Prompt-02/Reports/Prompt-02-WP17-Yoga-Contract-Reconciliation.md`.

## Tests and validation performed

Windows Python 3.11.9 and 3.14.6 produced identical results:

- focused reconciliation plus R4 plus WP17 subprocess: 19 passed, comprising
  4 reconciliation tests, all 14 R4 attack classes, and 1 WP17 subprocess test;
- Prompt-02 composed focused gate: 17 Prompt-02, 10 WP19, and 22 WP17 passed;
- Prompt-03 composed focused gate: 19 Prompt-03, 17 Prompt-02, and 22 WP17
  passed; inference manifest remained `f57bc285...a563786e`;
- Prompt-04 composed focused gate: 62 Prompt-04, 19 Prompt-03, 17 Prompt-02,
  and 22 WP17 passed; Prompt-04 manifest remained `440a459c...b7930b`;
- one Prompt-05 full validator per lane: 1,005 nodes collected, 1,003 passed,
  2 optional dependency tests skipped, 0 failed; 93 focused Prompt-05 tests;
- Prompt-05 manifest matched across lanes at
  `f6d90db74309127e99d55e17c542214b05bb385b8ec62447c1baef53c393ba92`;
- rule lint inspected the same five rule files; strict snapshot, all 24
  protected artifacts, four personal exports, and validator worktree-mutation
  checks passed;
- frontend lint, nonincremental TypeScript type-check, and production build in
  an OS-temporary mirror passed; 12 governed routes and all 14 static
  generation units were preserved; no repository TypeScript build-info file
  was created.

Focused and complete domain coverage also preserves Career same-run config and
ledger authority, transit provenance, sole InferenceEngine aggregation,
insufficient/missing-inference distinctions, ordinary Yoga compatibility, and
Yoga source ordering.

Prompt-02/WP17 Yoga baseline contradiction reconciled; Prompt-05 R4 validation
completed; independent Final R4 Review pending.

## Unresolved issues and repository actions

No R4 implementation or reconciliation defect is known. Prompt-05 remains
unaccepted until one independent read-only Final R4 Review passes. Commit
authorization remains separate. The safety policy prevented automatic removal
of the external OS-temporary frontend mirror after its successful build; that
mirror is outside the repository and did not affect validation or repository
state.

No file was staged. No commit, push, PR, merge, or Prompt-06 action occurred.

Recommended next action:

**RUN ONE INDEPENDENT READ-ONLY FINAL R4 REVIEW**
