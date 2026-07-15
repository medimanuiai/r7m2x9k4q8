# Parāśara Engine Target State

Status: APPROVED  
Authority: Jyothishyam Master Architecture Specification and approved stage prompts  
Approval basis: Master Architecture Specification and approved staged sequence  
Owner: Parāśara engine maintainers  
Last reviewed: 2026-07-12

## Purpose

This document is a local navigation summary of the approved target architecture. It does not replace the Jyothishyam Master Architecture Specification or approved implementation prompts.

## Required runtime flow

```text
Surya Siddhanta
  -> Adapter and Normalization
  -> Core AstroState
  -> Enrichment Pipeline
  -> Enriched AstroState evaluation snapshot
  -> Generic Predicate Engine
  -> PredicateResult
  -> Generic Rule Engine
  -> universal RuleMatch[]
  -> shared InferenceEngine
  -> typed Domain Interpreters
  -> OutputAssembler
  -> public JSON
```

## Layer boundaries

### Surya Siddhanta

Produces astronomical facts only. It must not perform astrological interpretation.

### Adapter and normalization

Validate upstream data and construct one deterministic canonical representation. Raw Surya structures must not remain an alternate downstream data source.

### AstroState

Acts as the single source of truth after normalization. It must expose stable factual access, explicit capability/completeness information, and immutable evaluation-time state.

The implementation may use separate `CoreAstroState` and `EnrichedAstroState` types or one controlled builder that freezes the completed evaluation snapshot. In either design, mutation must end before predicate and rule evaluation begins, and consumers must not trigger hidden enrichment calculations.

### Enrichment pipeline

Computes reusable astrological facts in dependency order. Enrichments must not know about domain interpreters or produce predictions.

Each enrichment must declare its factual inputs, required capabilities, output version, deterministic ordering, and missing-data behavior. Enrichment failures must remain distinguishable from factual negative results.

### Predicate engine

Answers factual questions only. Every active registered predicate must return the universal immutable `PredicateResult` contract. Predicates must not score, assign confidence, narrate, or mutate AstroState.

Missing capability, invalid parameters, factual nonmatch, and evaluation error are distinct outcomes. Predicate caching belongs inside the Predicate Engine and uses AstroState digest, predicate identity/version, canonical parameters, and relevant evaluation/configuration/enrichment versions. Cached logical values are immutable and version-isolated.

### Rule engine

Loads and validates declarative rules, evaluates condition trees, preserves PredicateResults, and produces the universal `RuleMatch` contract. It must not compute final domain scores or narratives.

Rule-set selection is explicit and has no silent version fallback. Loading validates identity, metadata, provenance, lifecycle state, dependencies, system scope, and applicable approval policy before execution.

### Inference engine

One shared engine owns contribution aggregation, normalization, confidence, conflict resolution, and explainable combination policy across all domains.

### Domain interpreters

Select rule packs, invoke generic services, and add evidence-backed domain labeling or narrative. They must not implement generic scoring, confidence, conflict resolution, enrichment calculation, or public JSON assembly.

### Output assembler

Is the only public serializer. It performs no astrological reasoning, scoring, or confidence calculation.

## Configuration and evaluation context

Every evaluation is governed by an explicit configuration containing at minimum:

- interpretation system;
- engine version;
- rule-set version;
- predicate-library and DSL versions where applicable;
- normalization and enrichment versions;
- execution mode;
- evaluation instant;
- relevant feature/configuration versions.

These values propagate through cache identity, RuleMatch, traces, snapshots, and public output so historical evaluations can be replayed without cross-version contamination.

## Error ownership

- The adapter rejects invalid upstream structures.
- AstroState construction reports normalization and capability failures explicitly.
- Query APIs expose typed missing-data or unavailable-capability behavior.
- Predicates return structured expected errors without converting unavailable facts into nonmatches.
- The Rule Engine applies explicit rule-level failure policy.
- Unexpected programming defects remain visible in strict development and test modes.
- Domain and output layers serialize only approved status/error contracts.

Broad exception swallowing and silent fallback across architectural boundaries are prohibited.

## System extensibility

Parāśara, Jaimini, KP, Tajaka, and future interpretation systems share AstroState and generic infrastructure while remaining independent plugins or system scopes. Predicates, rules, configuration, caches, and traces identify their system scope. Adding one interpretation system must not require modifying another or embedding Parāśara-specific meaning in shared infrastructure.

## Rule governance and replay

- Multiple rule-set versions may coexist.
- Strict execution includes only rules allowed by approved production and SME policy.
- Experimental execution identifies draft or unapproved rules explicitly.
- Promotion, rollback, and audit records preserve immutable provenance.
- Historical replay selects the original engine, rule, predicate, configuration, and evaluation-context versions.
- Trace identities and ordering are deterministic.

## Global invariants

- Identical chart, engine version, rule-set version, evaluation instant, and configuration produce identical logical output.
- Downstream modules consume AstroState, not raw Surya JSON.
- Astrological knowledge is declarative where required by the Master Architecture.
- Predicates produce only PredicateResult.
- Rules produce only universal RuleMatch.
- Scoring and confidence belong to the shared Inference Engine.
- Domain interpreters return typed domain models.
- Public serialization belongs to the Output Assembler.
- Every conclusion retains evidence, provenance, and version information.
- Production rule execution enforces approved governance policy.
- Missing capabilities remain distinct from negative factual evidence.
- Cache entries are isolated by state, system, version, parameters, and relevant context.
- Shared infrastructure remains free of interpretation-system-specific business meaning.

## Approved staged direction

The current approved sequence begins with:

1. PredicateResult consolidation.
2. Universal RuleMatch.
3. Shared InferenceEngine.
4. Stable AstroState query API.
5. Typed domain outputs and thin interpreters.
6. Fully wired rule-set version selection.
7. Baseline DSL extensions.
8. Explicit rule dependency graph.

Each stage requires its prescribed audits and acceptance evidence before the next stage begins.

## Compatibility policy

Existing behavior should be preserved when it agrees with the approved architecture or is outside the active stage. Compatibility behavior may be replaced only with evidence that it violates an approved requirement. Contract migrations must not silently alter astrological mathematics.
