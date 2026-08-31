# Prompt-05 Remediation R1 Record

Status: **FAILED INDEPENDENT FINAL R1 REVIEW**

This is the canonical historical record for Prompt-05 Remediation R1. It does
not supersede the governing requirements or the stopping report. R1 was an
unstaged remediation session on `main` at
`c719a1bf686e1e37eb8542f9323fc279b670250e`; it created no commit, push, or
pull request, and Prompt-06 did not start.

## Original failed-review findings

| Finding | Original defect | R1 action and claim | Final R1 verification |
| --- | --- | --- | --- |
| HIGH-1 | Career/Yoga compatibility mappings could contradict authoritative inference/rule values | Added typed compatibility projections and duplicate source-comparison fields | **FAIL** — coordinated public-plus-hidden replacement and direct construction still succeeded |
| HIGH-2 | Domain components, indicators, narratives, evidence, and traces lacked exact lineage | Added source reconciliation loops | **FAIL** — indicators with no contribution skipped RuleMatch/evidence/trace validation |
| HIGH-3 | Dasha chronology and transit provenance were structurally weak | Added parsed Dasha invariants and `TransitProducerEvidence` ID catalogs | **FAIL** — a caller could fabricate the catalog and all consuming IDs together |
| HIGH-4 | Career reconstructed `base_score` and contribution totals outside the authorized owner | Removed post-inference Career reaggregation and kept the outward compatibility projection | **PASS** |
| HIGH-5 | `generate_snapshot.py` remained a second public serializer | Moved final public structure/byte ownership into `OutputAssembler` | **FAIL** — valid multi-Yoga input was rejected because assembly read order from evidence instead of typed metadata |
| HIGH-6 | Frontend lint was interactive or not genuinely configured | Added pinned noninteractive ESLint configuration and executed `next lint` | **PASS** |
| MEDIUM-1 | Adversarial and architecture coverage was incomplete | Added `test_remediation_adversarial.py` and focused architecture checks | **FAIL** — coordinated compatibility, producer-catalog, lineage-free-indicator, helper-path, and multi-Yoga attacks remained uncovered |
| MEDIUM-2 | Present insufficient evidence used missing-inference semantics | Changed the present-result issue to `INSUFFICIENT_EVIDENCE` | **FAIL** — nonneutral insufficient results were accepted and no executable missing-inference path existed |
| MEDIUM-3 | `DomainIssue` admitted sensitive POSIX/platform paths | Added Windows, UNC, POSIX, repository, traceback, and exception-path filtering | **PASS** |
| MEDIUM-4 | Review type-check created `frontend/tsconfig.tsbuildinfo` | Made type-check nonincremental and removed the generated root artifact | **PASS** |

## What R1 changed

R1 introduced typed Career and Yoga compatibility projections, strengthened
component/narrative reconciliation, parsed Dasha chronology and hierarchy,
added transit readiness modeling, moved snapshot byte serialization into the
sole `OutputAssembler`, configured frontend ESLint, corrected the present
insufficient-evidence issue code, made `DomainIssue` path checks
platform-neutral, disabled incremental type-check output, and added focused
adversarial tests. It also updated the existing Prompt-05 stopping report with
an R1 addendum.

Those changes were useful but the Final R1 Review correctly rejected the
claim that all ten findings were closed. The failed review carried four highs
and three mediums into R2:

1. caller-controlled Career/Yoga compatibility duplicates;
2. contribution-free indicators without authoritative RuleMatch lineage;
3. self-declared transit provenance catalogs;
4. invalid Yoga source-order lookup in `OutputAssembler`;
5. missing coordinated/adversarial and helper-path coverage;
6. incomplete insufficient/missing-inference semantics; and
7. this canonical R1 report was absent.

## Final R1 validation evidence

```text
PYTHON_3_11: 3.11.9; 959 COLLECTED; 957 PASSED; 2 SKIPPED; 0 FAILED
PYTHON_3_14: 3.14.6; 959 COLLECTED; 957 PASSED; 2 SKIPPED; 0 FAILED
PROMPT05_FOCUSED: 47 PASSED PER LANE
PROMPT05_MANIFEST: 7321e44b1f1ff03ba141e1146fe1feafb88b190c032fc9eacd7974c28834c25a
PROMPT05_MANIFESTS_MATCH: YES
APPROVED_SNAPSHOT: 4,041 BYTES; da2059ba3cfb92eed267f93d1e41585dac1422d68f685022c8609cfd04ad57af
PUBLIC_CAREER_EXACT: YES
PUBLIC_YOGA_EXACT: YES
PREDECESSOR_MANIFESTS_EXACT: YES
PROTECTED_FILES_UNCHANGED: 24/24
PERSONAL_EXPORTS_UNCHANGED: 4/4
FRONTEND_LINT: PASS
FRONTEND_TYPECHECK: PASS; NONINCREMENTAL
FRONTEND_BUILD: PASS; 12 GOVERNED ROUTES
```

The green suites did not override the independently reproduced defects because
the R1 tests omitted their coordinated attack paths. The Final R1 Review
therefore ended with:

```text
PROMPT05_FINAL_R1_REVIEW: FAIL
PROMPT05_ACCEPTANCE_CONFIRMED: FAIL
REMAINING_HIGHS: 4
REMAINING_MEDIUMS: 3
READY_FOR_COMMIT_AUTHORIZATION: NO
READY_FOR_PROMPT06: NO
COMMIT_CREATED: NO
PUSH_PERFORMED: NO
PR_CREATED: NO
PROMPT06_STARTED: NO
```

R2 closure evidence is owned by
`Prompt-05-Remediation-R2.md`; this historical R1 record must not be rewritten
to imply that R1 passed.
