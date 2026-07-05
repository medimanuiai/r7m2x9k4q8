# Gaps To Fill After Coding

## Calibration and backtesting
- Collect labeled historical dataset (minimum 500 charts across domains) with event timestamps and verified outcomes for career, marriage, major wealth events, and health incidents.
- Implement backtest harness that computes per-rule `historical_accuracy`, `precision`, `recall`, and `false_positive_rate`.
- Use backtest results to tune: context multipliers, logistic scale `k`, epsilon for collapse rule, and confidence coefficients (α, β, γ). Record tuned values in `rules/parashara/v1/calibration.json`.

## SME review and governance
- Build SME UI for rule review with: rule diff viewer, test harness runner, approve/reject buttons, and signature capture.
- Implement approval workflow: `draft` → `reviewed` (SME comments required) → `validated` (SME signature) → `production`.
- SLA: review turnaround 5 business days for critical rules; emergency patch process for urgent fixes.

## Operational infrastructure
- Trace retention: see `ops.md` for retention policy (full traces 90 days, archive 2 years, trace metadata retained indefinitely).
- Distributed cache invalidation: use centralized rule-store versioning and publish invalidation events; TTL for AstroState cache default 24 hours.
- Monitoring: dashboards for rule evaluation latency (p95 < 200ms), cache hit rate (>80%), and rule usage counts.

## UX and language templates
- Create human summary templates per domain with placeholders for `score`, `confidence`, `key_indicators[]`, and `timeframe`.
- Conflict messaging: when `confidence <= 0.25` and `conflicts[]` present, use template: "Signals conflict for this domain; low confidence. Key evidence: {indicators}. See details."

## Legal and compliance
- Data retention policy: birth data and traces stored encrypted; retention default 2 years unless user requests deletion.
- Licensing audit: verify all third-party code and libraries; produce a compliance report confirming no AGPL code is included.

## Performance tuning and scaling
- Profile rule engine on representative workload (1000 charts, 100 concurrent requests); identify top 10 slow predicates.
- Implement compiled execution plan cache and precompile top 50 hot rules.
- Run scale tests for 10k charts and 500 concurrent requests; document resource usage and tuning steps.

## Governance and operational policies
- Define rule-set branching: `main` (production), `staging`, `dev`. Promotion requires passing unit tests and backtests.
- Implement rollback: ability to revert to previous rule-set version and re-run snapshots within 1 hour.

## SME training and documentation
- Create SME guide: DSL primer, macro patterns, evidence expectations, and unit-test templates.
- Provide example rule authoring workflow with sample rule, test fixture, and expected trace.

## Data and tooling
- Build tooling to convert classical Parāśara text rules into DSL templates (semi-automated).
- Provide utilities to visualize AstroState graph and rule traces (web UI or static HTML export).
