# Parāśara Operations Documentation

Status: CURRENT-STATE  
Owner: Parāśara engine maintainers  
Last verified: 2026-07-13

## Purpose

This folder separates proposed production controls from point-in-time operational evidence. Nothing here, by itself, certifies production readiness.

| Document | Role |
|---|---|
| [Operations Checklist](operations-checklist.md) | Proposed controls, decisions, owners, and required evidence |
| [Licensing Audit](licensing-audit.md) | Scope and limitations of the current dependency-license evidence |

Generated or point-in-time evidence is stored under `../evidence/` and must retain its original evidence date and provenance.

## Status interpretation

- `PROPOSED` controls require approval, implementation, and verification.
- `CURRENT-STATE` describes repository-observed operational behavior.
- `EVIDENCE` records a bounded point-in-time observation.
- Production readiness requires approved controls plus implementation and verification evidence; document presence is insufficient.

