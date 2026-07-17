# Parāśara Engine Gap Register

Status: CURRENT-STATE  
Owner: Parāśara engine maintainers  
Last verified: 2026-07-17

This register separates verified implementation gaps from proposals that still require an architectural, product, SME, privacy, legal, or operational decision. It does not broaden the scope of Prompt-01.

## Verified architecture gaps

- Current simplified astrological calculations do not implement every target calculation described by the Master Architecture.
- Universal RuleMatch, shared InferenceEngine, universal typed domain output,
  and OutputAssembler are not implemented.
- Full compiler/DSL/macros/dependency graph and explicit multi-version rule-set
  selection/governance are not implemented.
- The broad stable AstroState query API and immutable construction lifecycle
  remain beyond the Prompt-01 prepared factual boundary.

## Validation gaps

- Prompt-01 has dual-lane regression/determinism/snapshot/CI evidence, but this
  is not full Master Architecture, scientific, or release conformance.
- Branch-protection required-check configuration is external repository state
  and was not verifiable locally.

## Engineering gaps

- Rule governance, promotion, rollback, and immutable approval records are not established as a production workflow.
- Calibration and backtesting need approved datasets, metrics, acceptance thresholds, and SME review boundaries.
- Public API versioning, compatibility policy, and production deployment architecture remain incomplete or unverified.
- WP18 performance is dated descriptive evidence only. Broader performance,
  concurrency, and capacity targets require separate approval.

## Operations and compliance gaps

- Audit-25 privacy/raw-output/report-artifact/provider-diagnostic findings
  require separate owner review before applicable public release.
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
