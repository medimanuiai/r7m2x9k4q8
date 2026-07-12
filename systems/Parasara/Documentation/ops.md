# Parāśara Ops Checklist — Data Retention & Secrets

This checklist outlines minimal operational requirements for handling birth data and secrets before deploying the Parāśara engine.

- **Scope:** storage of input charts, intermediate AstroState, rule execution traces, and explainability artifacts.

- **Encryption at rest:** all persisted birth data and traces must be encrypted using a managed KMS (e.g., AWS KMS, Azure Key Vault).  
  - Acceptance: configuration documented and verified in infra repo.

- **Encryption in transit:** all service endpoints and internal communication must use TLS 1.2+.

- **Secrets management:** store API keys, DB credentials, and signing keys in a secrets manager (Vault, AWS Secrets Manager, Azure Key Vault).  
  - No secrets in plaintext or in repository.

- **Access control & least privilege:** adopt RBAC for storage and compute; restrict access to production data to named roles only.

- **Data retention & deletion policy:** define retention windows for raw charts and derived traces (e.g., retain raw charts for 90 days unless explicit consent to retain longer).  
  - Provide procedures for deletion requests and audit logs for deletions.

- **Trace retention:** keep full traces (detailed rule execution evidence) for 90 days, archive compressed traces for 2 years, and retain trace metadata indefinitely.  
  - Acceptance: trace retention policy documented and automated archival job scheduled in infra.

- **Audit logging:** capture admin actions, rule promotions, snapshot changes, and data deletions. Store logs in an immutable store with retention consistent with policy.

- **Backups & disaster recovery:** ensure backups are encrypted and regularly tested for restore.

- **Privacy & legal:** verify consent model for storing birth details; consult legal for jurisdictional requirements (e.g., GDPR, CCPA).

- **Operational runbooks:** include steps for rotating keys, revoking compromised keys, and emergency rollback of rule sets.

Add this file to the onboarding checklist and seek Ops/Legal sign-off before Phase 10 deployment.
