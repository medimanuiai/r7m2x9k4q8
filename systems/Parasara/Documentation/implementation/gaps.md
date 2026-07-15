# Parāśara Engine Gap Register

Status: CURRENT-STATE  
Owner: Parāśara engine maintainers  
Last verified: 2026-07-13

This register separates verified implementation gaps from proposals that still require an architectural, product, SME, privacy, legal, or operational decision. It does not broaden the scope of Prompt-01.

## Verified architecture gaps

- Predicate results and evaluator return contracts are not yet standardized across the runtime; the live Prompt-01 audit workspace is establishing the contract and migration boundary.
- Ownership of the two Parāśara rule directories is unresolved and must be determined from loaders, imports, runtime paths, tests, CI, and compatibility evidence.
- `ASPECT` versus `ASPECT_EXISTS` compatibility remains unresolved pending caller, rule-file, and test analysis.
- Current simplified astrological calculations do not implement every target calculation described by the Master Architecture.

## Validation gaps

- A complete repository-wide behavioral verification has not been run as part of the documentation review.
- Structural documentation evidence is point-in-time; it does not establish that live Prompt-01 audit files are complete or approved.
- Golden, snapshot, and integration coverage exists, but coverage is not equivalent to full Master Architecture conformance.

## Engineering gaps

- Rule governance, promotion, rollback, and immutable approval records are not established as a production workflow.
- Calibration and backtesting need approved datasets, metrics, acceptance thresholds, and SME review boundaries.
- Public API versioning, compatibility policy, and production deployment architecture remain incomplete or unverified.
- Performance baselines, cache policy, concurrency targets, and capacity limits require measurement and approval.

## Operations and compliance gaps

- Data classification, retention, deletion, trace access, encryption, and incident procedures require owner approval and implementation evidence.
- Dependency and source-license checks provide point-in-time evidence only; they do not prove legal compliance or absence of every incompatible source.
- Monitoring objectives, alert thresholds, recovery targets, and operational ownership are not approved.

## Proposals requiring approval

The archived gap list contains candidate dataset sizes, latency and cache targets, retention periods, service levels, branching models, workflow states, and user-interface ideas. None should be treated as a requirement until the appropriate authority approves it and the decision is recorded in a canonical specification or decision record.

## Related documents

- [Current implementation status](status.md)
- [Dependency-ordered roadmap](roadmap.md)
- [Active tasks](tasks.md)
- [Operational checklist](../operations/operations-checklist.md)
- [Archived proposal list](../archive/legacy-gaps-to-fill.md)
