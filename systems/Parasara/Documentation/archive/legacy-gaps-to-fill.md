# Legacy Gaps To Fill After Coding

Status: HISTORICAL  
Owner: Parāśara engine maintainers  
Archived: 2026-07-13

This document preserves earlier proposals. Numeric targets, service levels, retention periods, workflows, and architecture choices below are not approved merely because they appear here. Use `../implementation/gaps.md` for the current evidence-based gap register.

## Calibration and backtesting

- Collect a labeled historical dataset, originally proposed as a minimum of 500 charts across domains.
- Implement a backtest harness with per-rule accuracy, precision, recall, and false-positive metrics.
- Tune scoring and confidence parameters from approved backtest results.

## SME review and governance

- Build SME review tooling and an approval workflow.
- Earlier proposals included a five-business-day review SLA and an emergency patch process.

## Operational infrastructure

- Define trace retention, cache invalidation, monitoring, latency, and cache-hit targets.
- Earlier proposals included a 24-hour cache TTL, p95 latency below 200 ms, and cache hit rate above 80 percent.

## UX and language templates

- Create domain summary and conflict-message templates.

## Legal and compliance

- Define retention, encryption, deletion, and license-audit requirements.
- An earlier proposal suggested a two-year retention default.

## Performance and scaling

- Profile representative workloads and establish approved scale targets.
- Earlier proposals referenced 1,000-chart and 10,000-chart workloads and precompiling 50 hot rules.

## Governance, training, and tooling

- Define rule-set branching, promotion, rollback, SME training, rule-authoring examples, classical-text conversion aids, and trace visualization.

All quantities and choices above remain historical proposals unless approved through the documentation authority hierarchy.
