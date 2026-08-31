# Prompt-05 — Typed Domain Models

Status: REMEDIATION R4 IMPLEMENTATION-VALIDATED — INDEPENDENT FINAL R4 REVIEW PENDING  
Last verified: 2026-08-29

Prompt-05 adds one deeply immutable `DomainPrediction` shared by the six
authorized Parāśara domain identifiers, migrates only the substantive Career
path, maps existing Yoga records to `RuleMatch`-backed `YogaDiagnostic` values,
publishes availability-bearing Dasha/transit contracts without integrating
calculators, and routes the primary snapshot through one serialization-only
`OutputAssembler`.

Public Career/Yoga behavior and the approved snapshot remain exact. The legacy
Wealth row exists only in the outward compatibility profile and is not an
implemented domain. Prompt-01–04 types and semantics are unchanged.

- [Normative requirements](requirements/Prompt-05-Typed-Domain-Models.md)
- [Discovery report](Reports/Prompt-05-Discovery.md)
- [Typed-domain contract](../../specifications/domain-prediction.md)
- [Stopping report](Reports/Prompt-05-Stopping-Report.md)
- [Approved provenance decision](Decisions/Prompt-05-Provenance-Architecture-Decision.md)
- [R4 remediation report](Reports/Prompt-05-Remediation-R4.md)

Validation:

```powershell
python tools/validate_prompt05.py full
```

Run on both supported Windows Python lanes. The existing untracked
`jyothishyam_env/` in this workspace contains stale inaccessible pytest
basetemps; local validation therefore supplies process-local
`PYTEST_ADDOPTS=--ignore=jyothishyam_env`. Clean CI requires no ignore.

Prompt-05 does not establish scientific, SME, security, privacy, licensing,
operational, release, or production approval. Prompt-06 has not started.

Prompt-02/WP17 Yoga baseline contradiction reconciled; Prompt-05 R4 validation
completed; independent Final R4 Review pending. The governing Prompt-02
RuleMatch contract prevailed over the legacy WP17 condition override. The
current manifest is `06330b43...b3017`; full old-to-new lineage is recorded in
the Prompt-02 reconciliation and R4 reports. Prompt-05 is not accepted or
commit-authorized, and Prompt-06 has not started.

Remediation R1 closes the six high and four medium findings from the initial
architectural review. Python 3.11.9 and 3.14.6 each collected 959 tests (957
passed, 2 skipped), produced Prompt-05 manifest
`7321e44b1f1ff03ba141e1146fe1feafb88b190c032fc9eacd7974c28834c25a`,
and preserved every predecessor manifest and protected artifact. Frontend
lint, non-incremental type-check, and production build pass without creating
`tsconfig.tsbuildinfo`.
