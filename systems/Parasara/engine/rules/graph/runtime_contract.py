"""Locked Prompt-08 contracts and pure canonical helpers; no execution owner."""
from __future__ import annotations

import hashlib

from systems.Parasara.engine.rules.canonical import FrozenMapping, canonical_json_bytes


GRAPH_CONTRACT_DATA = FrozenMapping({
    "identity": "parashara-rule-graph-compiler",
    "version": "1.0.0",
    "compatibility_contract": "compiled-rule-set+rulematch-dependencies@1.0.0",
    "contracts": {
        "schema": "1.0.0", "declarations": "rule-dependency-declarations@1.0.0",
        "nodes": "rule-dependency-nodes@1.0.0", "edges": "rule-dependency-edges@1.0.0",
        "bound_rule": "graph-bound-rule@1.0.0", "graph": "rule-dependency-graph@1.0.0",
        "plan": "rule-execution-plan@1.0.0", "trace": "rule-dependency-trace@1.0.0",
    },
    "authoring_schema": {
        "document": ("graph_schema_version", "system", "rule_set_family", "rule_set_version", "rules"),
        "rule": ("rule_id", "revision", "requires_matches", "requires_absence", "optional_supports"),
        "reference": ("rule_id", "revision"), "all_fields_required": True, "unknown_fields": "reject",
        "concrete_revision_per_id": 1,
    },
    "identity_grammars": {
        "identity": r"^[A-Za-z0-9][A-Za-z0-9_.@/-]*$",
        "rule_id": r"^[A-Za-z0-9][A-Za-z0-9_.-]*$",
        "revision": r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$",
        "source_id": r"^[A-Za-z0-9][A-Za-z0-9._/-]*\.json$",
    },
    "path_policy": {"root": "explicit_authority_repository_root", "separator": "/",
        "forbidden_segments": ("", ".", ".."), "link_escape": "reject", "lookup": "manifest_only"},
    "parser_policy": {"encoding": "strict_utf8_no_bom_nfc_no_surrogates", "documents": 1,
        "duplicate_keys": "reject_before_mapping", "values": ("object", "array", "string"),
        "nesting": "escape_aware_preflight_root_one", "comments": False, "trailing_data": False},
    "edge_policy": {"kinds": ("requires_matches", "requires_absence", "optional_supports"),
        "direction": "prerequisite_to_dependent", "duplicate": "reject", "conflicting_pair": "reject",
        "self": "reject_before_cycles", "optional_missing_node": "reject", "optional_orders": True,
        "cross_system": False, "cross_set": False, "cross_version": False, "cross_domain": False,
        "domain_comparison": "identical_canonical_tuple", "membership": "exact_bijection",
        "empty_graph": "reject", "edgeless_nonempty": "accept"},
    "outcome_policy": {
        "matched": ("matched", "satisfied", "unsatisfied", "observed_matched"),
        "unmatched": ("unmatched", "unsatisfied", "satisfied", "observed_unmatched"),
        "missing_capability": ("missing_capability", "unavailable", "unavailable", "observed_unavailable"),
        "invalid_parameters": ("invalid", "unavailable", "unavailable", "observed_unavailable"),
        "error": ("error", "unavailable", "unavailable", "observed_unavailable"),
        "timeout": ("error", "unavailable", "unavailable", "observed_unavailable"),
        "skipped": ("skipped", "unavailable", "unavailable", "observed_unavailable"),
        "dependency_skip": ("skipped", "unavailable", "unavailable", "observed_unavailable"),
        "gate_precedence": ("unavailable", "unsatisfied", "passed"),
        "optional_gates": False, "dependency_evidence": False, "excluded": "fatal",
    },
    "planning_policy": {"nodes": "manifest_contiguous_source_order", "edges": ("prerequisite", "dependent", "kind_ordinal"),
        "algorithm": "kahn_min_heap_source_order", "components": "one_ready_queue",
        "priority_tiebreak": False, "scc": "iterative_sorted_kosaraju",
        "witness": "lowest_scc_member_sorted_dfs_first_edge_to_start_visited_once",
        "scc_order": "minimum_member", "blocked_tails": "exclude",
        "depth": "root_one_max_predecessor_plus_one_including_optional", "layers": False},
    "diagnostics_policy": {
        "stages": ("source", "parse", "schema", "membership", "edges", "cycles", "planning", "authorization", "execution"),
        "ordering": ("stage", "node_or_256", "prerequisite_or_256", "code", "field_path", "canonical_details"),
        "truncation": "first_255_canonical_traversal_then_final_marker", "structural_failure": "one_fatal",
        "messages": {
            "P08E001_INVALID_SOURCE": "Graph source violates the encoding, path, or strict JSON contract.",
            "P08E002_DUPLICATE_KEY": "A graph object repeats a field.",
            "P08E003_SCHEMA_MISMATCH": "Graph fields or schema version are unsupported.",
            "P08E101_UNKNOWN_DEPENDENCY": "A dependency is not a member of the selected rule set.",
            "P08E102_REVISION_MISMATCH": "A dependency revision differs from its selected rule revision.",
            "P08E103_VERSION_MISMATCH": "Graph system, family, or rule-set version differs from the selected manifest.",
            "P08E104_DUPLICATE_DEPENDENCY": "A dependency pair and kind are repeated.",
            "P08E105_CONFLICTING_DEPENDENCY": "A dependency pair declares more than one kind.",
            "P08E106_SELF_DEPENDENCY": "A rule depends on itself.",
            "P08E107_MEMBERSHIP_MISMATCH": "Graph nodes are not the exact compiled manifest membership.",
            "P08E108_CROSS_DOMAIN_DEPENDENCY": "Dependency nodes have different domain scopes.",
            "P08E201_CYCLE": "The rule dependency graph contains a cycle.",
            "P08E301_UNAUTHORIZED_SOURCE": "The selected authority does not authorize this graph source.",
            "P08E302_AUTHORITY_MISMATCH": "Graph or plan objects do not share the exact issued authority.",
            "P08E303_COMPONENT_MISMATCH": "Graph or DSL component contracts do not match the manifest.",
            "P08E304_DECLARATION_DIGEST_MISMATCH": "Graph declarations differ from the selected manifest.",
            "P08E305_GRAPH_DIGEST_MISMATCH": "Validated graph semantics differ from the selected manifest.",
            "P08E306_PLAN_DIGEST_MISMATCH": "Execution plan semantics differ from the selected manifest.",
            "P08E307_DIRECT_EXECUTION_BYPASS": "Graph-enabled rules require the authorized plan entry point.",
            "P08E308_RUNTIME_INVARIANT": "Graph execution cannot publish a complete consistent rule ledger.",
            "P08E401_LIMIT_VIOLATION": "A locked graph resource limit was exceeded.",
            "P08E999_DIAGNOSTIC_LIMIT": "Additional graph diagnostics were deterministically suppressed.",
        },
    },
    "resource_limits": {"source_bytes": 1_048_576, "graph_artifacts": 1, "nodes_minimum": 1,
        "nodes": 256, "edges": 4096, "dependencies_per_node": 32, "graph_depth": 64,
        "json_depth": 8, "mapping_entries": 16, "array_elements": 256, "string_code_points": 256,
        "identifier_code_points": 128, "source_id_code_points": 256, "diagnostics": 256,
        "cycle_witness_nodes": 257, "cache_entries": 1, "issued_plans": 1,
        "runtime_traces": 256, "runtime_decisions": 4096},
    "canonical_projections": {
        "declarations": ("contract", "document"), "nodes": ("contract", "nodes"),
        "edges": ("contract", "edges"), "bound_rule": ("contract", "node", "dependencies"),
        "graph": ("contract", "declarations_sha256", "nodes_sha256", "edges_sha256"),
        "plan": ("contract", "graph_sha256", "dsl_compiled_rule_set_sha256", "graph_compiler_content_sha256", "graph_contract_sha256", "execution_order"),
        "trace": ("contract", "plan_sha256", "source_order", "snapshot_sha256", "context_sha256"),
        "declaration_order": "rule_id_revision_and_reference_id_revision", "encoding": "canonical_json_bytes",
        "hash": "sha256_lowercase", "raw_source": "audit_and_cache_only", "manifest_fingerprint": "excluded_no_cycle",
    },
    "result_ordering": ("-priority", "rule_id", "rule_version", "evaluation_plan_position"),
})

LIMITS = GRAPH_CONTRACT_DATA["resource_limits"]
CONTRACTS = GRAPH_CONTRACT_DATA["contracts"]
KINDS = GRAPH_CONTRACT_DATA["edge_policy"]["kinds"]
MESSAGES = GRAPH_CONTRACT_DATA["diagnostics_policy"]["messages"]
STAGES = GRAPH_CONTRACT_DATA["diagnostics_policy"]["stages"]


def digest(value):
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


GRAPH_CONTRACT_SHA256 = digest(GRAPH_CONTRACT_DATA)


def dependency_trace_id(plan_sha256, source_order, snapshot_sha256, context_sha256):
    return "graph." + digest(dict(contract=CONTRACTS["trace"], plan_sha256=plan_sha256,
        source_order=source_order, snapshot_sha256=snapshot_sha256, context_sha256=context_sha256))
