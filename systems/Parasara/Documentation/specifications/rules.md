# Rule and RuleMatch Contract

Status: APPROVED  
Authority: Master Architecture Specification  
Approval basis: Master Architecture Specification and approved staged sequence  
Owner: Parāśara engine maintainers  
Last reviewed: 2026-07-13

## Rules

Rules express versioned astrological meaning declaratively. Rule loading must validate schema, required metadata, unique identity, dependencies, versions, provenance, lifecycle state, and applicable SME policy before execution.

Python provides safe execution infrastructure; YAML or JSON expresses approved astrological knowledge. Rule data must not enable arbitrary Python execution or hidden mutation.

Every rule must identify its rule ID/version, rule-set version or selection context, family/category, applicable domains and contexts, condition tree, semantic weight and priority, provenance, lifecycle status, quality metadata, and applicable approval state.

## Rule engine

The generic Rule Engine loads and validates rules, evaluates condition trees through registered predicates, aggregates factual evidence, and constructs universal RuleMatch objects. It does not own final domain aggregation, confidence, or narrative.

Invalid rules must fail loading or compilation before production evaluation. Compilation must provide deterministic traversal and execution ordering, validate predicate/parameter schemas, expand approved macros/references canonically, and reject missing references or dependency cycles.

Logical operators preserve evaluated PredicateResults and explicit errors rather than collapsing evidence into raw booleans prematurely. Diagnostic mode may retain matched and unmatched rule evaluations; production exposure follows explicit policy.

## RuleMatch

One immutable RuleMatch contract must preserve rule identity and version, rule-set version, family/category/domain, match state, semantic weight and priority, context, PredicateResults, evidence, provenance, quality, and deterministic trace identity.

Predicates must not assign adjusted domain contributions. Custom Yoga and Career match dictionaries are compatibility behavior pending the universal RuleMatch stage.

RuleMatch must remain serializable, deterministic, and evidence-backed for both matched and diagnostic unmatched results. A match must not exist without the originating rule identity, version, provenance, and preserved predicate evaluation evidence.

RuleMatch may carry semantic base weight and priority from rule metadata. Final context-adjusted contribution, normalized domain score, conflict resolution, and confidence belong to the shared InferenceEngine.

## Version and governance

Rule-set selection must be explicit. Missing requested versions must fail clearly. Production execution must enforce the approved lifecycle and SME policy; experimental rules must be identified as such.

Multiple versions may coexist. Selection, cache identity, traces, snapshots, and output must use the requested version without silent fallback. Promotion and rollback preserve historical versions and immutable audit provenance.

## Dependencies

Higher-order rule dependencies belong to an explicit compiled rule graph, not recursive predicate calls. Missing dependencies, version incompatibility, disabled/unapproved dependencies, cross-domain restrictions, and direct or indirect cycles must have deterministic validation behavior.

## Current compatibility boundary

The active loaders use mutable global dictionaries, silently replace duplicate IDs, skip some invalid files/rules through broad exception handling, and resolve paths partly from the current working directory. The M1 runtime hardcodes rule types and returns a serialized RuleMatch-shaped dictionary. Yoga and Career use additional custom dictionaries. These are current compatibility behaviors, not completion of this contract.
