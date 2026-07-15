# Parāśara Operations Checklist

Status: PROPOSED  
Owner: Parāśara engine maintainers with Operations and Legal  
Last reviewed: 2026-07-13

## Scope

This checklist covers birth data, AstroState, rule traces, explainability artifacts, rule promotion, and engine deployment. It records required decisions and controls; it does not assert that infrastructure implements them.

No Parāśara-specific container, infrastructure-as-code, deployment manifest, production monitoring configuration, or operational runbook was found during the scoped repository review. The Docker material under `auth-scaffold/` is separate and is not evidence of Parāśara deployment readiness.

## Required controls

- Encryption at rest through an approved managed key system.
- TLS for service and internal communication.
- Secrets stored outside source control in an approved secrets manager.
- Least-privilege access with named operational roles.
- Auditable access, rule promotion, snapshot approval, deletion, and rollback events.
- Encrypted backups with tested restore procedures.
- Key rotation, credential revocation, incident response, and rule rollback runbooks.
- Monitoring for latency, errors, cache behavior, rule versions, and deterministic replay failures.
- Environment and dependency reproducibility through pinned/locked inputs and build provenance.
- Versioned engine/rule/configuration deployment with rollback and historical replay support.
- Separation of production data, test fixtures, generated reports, and approved evidence.
- Vulnerability, dependency-license, and software-bill-of-materials review.
- Log and trace redaction that prevents unnecessary birth-data or secret exposure.

## Control ownership and evidence

Before a control can be marked implemented, record:

- accountable owner and approver;
- approved policy or decision reference;
- implementation location or service;
- environment scope;
- verification method and last successful date;
- monitoring/alerting behavior;
- exception and remediation process.

| Control area | Current repository evidence | Readiness |
|---|---|---|
| Parāśara deployment packaging | No scoped deployment artifact found | NOT EVIDENCED |
| Secrets and key management | Policy requirement only | NOT EVIDENCED |
| Encryption and transport security | Policy requirement only | NOT EVIDENCED |
| Retention and deletion automation | Proposed decisions only | NOT EVIDENCED |
| Monitoring and alerting | No scoped configuration found | NOT EVIDENCED |
| Backup and restore | No scoped runbook/test evidence found | NOT EVIDENCED |
| Incident response and rollback | Requirement only | NOT EVIDENCED |
| Rule promotion/governance service | Target architecture only | NOT EVIDENCED |
| Dependency licensing | Point-in-time partial inventory | PARTIAL EVIDENCE |
| CI regression testing | Active workflows exist | PARTIAL; NOT PRODUCTION OPERATIONS |

## Privacy and retention decisions

Retention periods for raw birth data, AstroState, detailed traces, archives, backups, and audit metadata require explicit Legal/Privacy and product approval. Earlier documents suggested 90-day and two-year windows; those values are examples, not approved policy.

Before deployment, define consent and lawful basis, jurisdictional requirements, deletion/export procedures, retention automation, trace redaction/access, backup expiry, and incident obligations.

Birth date, time, and location may constitute sensitive personal data depending on jurisdiction and product use. Data minimization must cover raw input, AstroState, caches, traces, snapshots, logs, reports, backups, support exports, and analytics.

## Reliability and release decisions

Define service-level objectives, supported load, timeout/error policy, health checks, dependency failure behavior, migration/rollback procedure, cache invalidation, version compatibility, and recovery-point/recovery-time objectives before deployment.

Release evidence must identify the exact engine, rule-set, predicate, normalization, enrichment, schema, and configuration versions deployed.

## Acceptance evidence

Production readiness requires infrastructure evidence, responsible owners, review dates, automated control tests where practical, and sign-off from Operations, Security, and Legal. A documentation checklist alone is insufficient.

Every control remains `NOT EVIDENCED` or `PARTIAL` until its implementation and verification artifacts are linked here or in a dedicated evidence record.
