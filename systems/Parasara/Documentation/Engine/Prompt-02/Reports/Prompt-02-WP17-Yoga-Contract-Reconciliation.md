# Prompt-02/WP17 Yoga Contract Reconciliation

Status: COMPLETE — IMPLEMENTATION-VALIDATED; INDEPENDENT FINAL R4 REVIEW PENDING

Date: 2026-08-29  
Branch and unchanged HEAD: `main` at
`c719a1bf686e1e37eb8542f9323fc279b670250e`

## Conflict and authority

WP17 scenario `06.yoga.explicit_permutations` evaluates five source-order
permutations. In each permutation, `rajayoga_naive` retains an invalid,
unmatched RuleMatch while its diagnostic condition result is matched:

```text
RuleMatch.status: invalid
RuleMatch.matched: False
condition_result.status: matched
condition_result.matched: True
```

The former public compatibility projection selected
`condition_result.matched`, yielding `True`. The R4 projection selects
`RuleMatch.matched`, yielding `False`. No protected real-chart fixture has this
disagreement.

The governing Prompt-02 specification does not require the override:

- Section 4 makes `status` authoritative and assigns RuleMatch rule outcome,
  rule evidence, rule errors, and root rule trace ownership.
- Section 9 defines `status` as authoritative and `matched` as a Boolean
  derived from or validated against status.
- Section 10 requires invalid and unmatched statuses to remain distinct and
  false; invalid must not become an ordinary nonmatch.
- Section 11 assigns the rule-level outcome, evidence summary, errors, and
  root trace to RuleMatch. Compatibility duplication is serializer-only.
- Sections 13 and 14 require status/matched consistency and require the generic
  Rule Engine to return RuleMatch before Yoga or public projection.

There is no normative Prompt-02 clause allowing condition truth to replace a
RuleMatch outcome. The contradictory WP17 expectation was therefore a legacy
fixture/manifest baseline and was subordinate to the Prompt-02 contract and
the approved Prompt-05 provenance decision.

## End-to-end trace and resolution

```text
condition_result.matched=True
  -> generic Rule Engine retains RuleMatch(status=invalid, matched=False)
  -> YogaEvaluationRecord retains both diagnostic values
  -> authoritative YogaDiagnostic construction rejects the disagreement
  -> one-way public compatibility uses RuleMatch.matched=False
  -> WP17 Yoga public aggregate changes
  -> Prompt-02 current manifest expectation changes
```

The former override was in
`engine/enrichments/yoga_engine.py::project_yoga_compatibility`, which selected
the condition Boolean when present. The approved R4 code instead uses
`record.rule_match` for identity, matched state, evidence/trace authority, and
public trace identity. No serializer-only override was restored.

## Baseline lineage

```text
OLD_PREDECESSOR_MANIFEST_HASH:
75b65d2cd1420c6261aadbb8159d10fb8c641137ce08d29f2a651952e5cdfaf7

NEW_PREDECESSOR_MANIFEST_HASH:
06330b43cac062239e0670d1e48ab00c328ee270af64023b2017b819dc7b3017

OLD_APPROVED_SNAPSHOT_SIZE: 4041
NEW_APPROVED_SNAPSHOT_SIZE: UNCHANGED

OLD_APPROVED_SNAPSHOT_SHA256:
da2059ba3cfb92eed267f93d1e41585dac1422d68f685022c8609cfd04ad57af

NEW_APPROVED_SNAPSHOT_SHA256: UNCHANGED
```

Both predecessor manifests are 1,899 bytes. The only semantic manifest delta
is `scenarios[5].public_sha256`, from
`299fbabbe6c94e8c27d6a63235b63e64c22e8da1a9a93db8002b54b317c2c8ff`
to `1c49e3aa9c25d67b39681980c335ab9dc7287a22c6cfb6c666a5651c6df29f5f`.
The Yoga public aggregate remains 527 bytes. Replacing only that field in the
new manifest reproduces the old manifest digest exactly.

| Changed predecessor file | Reason | Old SHA-256 | New SHA-256 |
|---|---|---|---|
| `tests/wp17/scenario_manifest.py` | Assert RuleMatch-owned public truth and the exact five conflict rows | `6610d85308731cd867b2b3ba29c1f28c8336c292bfeaec8e7224310fd0f5dc9f` | `45debae8158344dc6daffab52fac317f0c8453a1a2034022bbd58c1c7f113985` |
| `tests/wp17/test_determinism_subprocess.py` | Pin the corrected Yoga row and aggregate | `258ec46989ba7a83513c588e0b5bfb93ca83d81befbc22ff3d16fe3117137b75` | `ab3965c1457e119d7561d53372f072b9e21f2319926dd5671d998d82a6b82e39` |
| `tools/validate_prompt02.py` | Replace only the superseded current Prompt-02 manifest constant | `116ace8e804ed98b80381d4b7b7c199925655af4fd927b24ab1338929aa7cb57` | `ab5f29f2448dc1d5e46a5f91edcda466eb326ffe37d5112bbb97321182b45179` |

No approved snapshot, fixture JSON, astrology rule, rule weight, source order,
Prompt-03 manifest, Prompt-04 manifest, or historical Prompt-01–05 report was
rewritten. Historical old hashes remain visible as historical evidence.

## Regression coverage and validation

`tests/domain/test_yoga_contract_reconciliation.py` adds four focused tests:

1. invalid RuleMatch cannot be overridden or mutated by condition truth;
2. unmatched RuleMatch cannot be overridden, and disagreement is rejected;
3. invalid disagreement rejects authoritative YogaDiagnostic construction;
4. compatible canonical evaluation preserves order and public construction,
   replacement, and reconstruction cannot bypass the authority boundary.

Python 3.11.9 and 3.14.6 each passed all 19 combined reconciliation/R4/WP17
checks. The composed Prompt-02, Prompt-03, and Prompt-04 focused validators and
one Prompt-05 full validator per lane passed. Each full lane collected 1,005
nodes, with 1,003 passed, 2 optional-dependency skips, and 0 failed. Prompt-05
focused contracts passed 93. Prompt-03, Prompt-04, and Prompt-05 manifest
hashes remained respectively `f57bc285...a563786e`, `440a459c...b7930b`, and
`f6d90db7...3c393ba92` in both lanes.

Frontend lint, nonincremental type-check, temporary-mirror production build,
12-route validation, and all 14 static generation units passed. All 24
protected artifacts, all four personal exports, public Career output, ordinary
Yoga compatibility/order, and the 4,041-byte approved snapshot remained exact.

## Current state

Prompt-02/WP17 Yoga baseline contradiction reconciled; Prompt-05 R4 validation
completed; independent Final R4 Review pending.

No staging, commit, push, PR, merge, or Prompt-06 work occurred.
