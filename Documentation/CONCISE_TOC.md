# Concise Table of Contents
This file lists the most important project documents with file path and a one-line purpose — quick reference for newcomers.

Document | Path | Purpose
---|---|---
Docs Index / TOC | Documentation/README.md | Project documentation index and links to major specs
All Docs TOC (generated) | Documentation/ALL_DOCS_TOC.md | Full list of Markdown files across the repo (auto-generated)
Systems TOC | Documentation/TOC_SYSTEMS.md | System-level table of contents (Surya / Parasara)
Surya System Index | Documentation/Systems/SuryaSiddhanta.md | SuryaSiddhanta code pointers, ayanamsa, nakshatra, and tests
Parasara System Index | Documentation/Systems/Parasara.md | Parasara code pointers, rules, enrichments, and tests
Astrology Engine Spec | Documentation/03_ASTROLOGY_ENGINE_SPEC.md | Detailed engine design: nakshatra, dasha, calculations and interfaces
API Spec | Documentation/02_API_SPECIFICATIONS.md | REST endpoints, request/response contracts used by frontend/backend
Validation & Roadmap | Documentation/09_VALIDATION_AND_ROADMAP.md | Phase plan, validation layers, acceptance criteria (Surya/Vimshottari etc.)
Testing Framework README | tests/testing_framework/README.md | How to run snapshot, golden, and regression tooling
Surya Validation tests | tests/surya/test_positions.py | Skyfield-based validation harness for planetary positions
Surya Test Cases (generated) | tests/surya/planet_position_test_cases.json | 500 deterministic Surya test cases (expected values populated)
Completion Matrix | tests/COMPLETION_MATRIX.md | Cross-system test and validation tracking; verify current claims against code and canonical system status
Dasha (Vimshottari) golden | tests/dasha/golden_vimshottari_01.json | Golden output used to validate Vimshottari implementation
Aspects tests | tests/enrichments/test_parashara_aspects.py | Unit tests for Parāśara Graha Drishti and nodes config
Rules README | systems/Parasara/rules/parashara/v1/README.md | How rule YAMLs are organized and metadata requirements
Surya engine docs | systems/SuryaSiddhanta/Documentation/SuryaSiddhanta_System.md | Surya engine developer guide and testing notes
Parasara documentation index | systems/Parasara/Documentation/README.md | Canonical navigation, authority, architecture, status, and task mapping
Parasara implementation status | systems/Parasara/Documentation/implementation/status.md | Evidence-based current implementation status and known limitations
Parasara specifications | systems/Parasara/Documentation/specifications/README.md | Focused approved and current compatibility contracts
Parasara guides | systems/Parasara/Documentation/guides/README.md | Verified testing and vertical-slice guidance
Parasara operations | systems/Parasara/Documentation/operations/README.md | Operational readiness, controls, and licensing evidence boundaries
