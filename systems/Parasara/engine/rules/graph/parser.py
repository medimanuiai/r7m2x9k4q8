"""Bounded strict JSON graph declarations. No path access or authority issuance."""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import re
import unicodedata

from systems.Parasara.engine.rules.canonical import FrozenMapping
from systems.Parasara.engine.rules.graph.runtime_contract import GRAPH_CONTRACT_DATA, LIMITS, KINDS, CONTRACTS
from systems.Parasara.engine.rules.graph.models import DiagnosticCollector, GraphCompilationFailed, diagnostic


@dataclass(frozen=True, slots=True)
class ParsedGraph:
    document: FrozenMapping
    source_raw_sha256: str


class _ParseFailure(ValueError):
    def __init__(self, code="P08E001_INVALID_SOURCE", details=None):
        self.code, self.details = code, details or {}


def valid_source_id(value):
    return (isinstance(value, str) and len(value) <= LIMITS["source_id_code_points"]
        and re.fullmatch(GRAPH_CONTRACT_DATA["identity_grammars"]["source_id"], value) is not None
        and not any(p in GRAPH_CONTRACT_DATA["path_policy"]["forbidden_segments"] for p in value.split("/")))


def _bound(resource, observed):
    if observed > LIMITS[resource]:
        raise _ParseFailure("P08E401_LIMIT_VIOLATION", dict(resource=resource, limit=LIMITS[resource], observed=observed))


def _pairs(items):
    seen = set()
    for key, _ in items:
        if key in seen:
            raise _ParseFailure("P08E002_DUPLICATE_KEY")
        seen.add(key)
    _bound("mapping_entries", len(items))
    return dict(items)


def _scalar(_):
    raise _ParseFailure()


def parse_graph_source(*, source_id, payload, rule_positions=None):
    if isinstance(source_id, str) and len(source_id) > LIMITS["source_id_code_points"]:
        return GraphCompilationFailed((diagnostic("P08E401_LIMIT_VIOLATION", stage="source",
            details=dict(resource="source_id_code_points", limit=LIMITS["source_id_code_points"], observed=len(source_id))),))
    if not valid_source_id(source_id):
        return GraphCompilationFailed((diagnostic("P08E001_INVALID_SOURCE", stage="source"),))
    try:
        if not isinstance(payload, (str, bytes)):
            raise _ParseFailure()
        raw = payload.encode("utf-8", "strict") if isinstance(payload, str) else payload
        _bound("source_bytes", len(raw))
        text = raw.decode("utf-8", "strict")
        if text.startswith("\ufeff") or unicodedata.normalize("NFC", text) != text:
            raise _ParseFailure()
        depth, in_string, escaped = 0, False, False
        for char in text:
            if in_string:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == '"':
                    in_string = False
            elif char == '"':
                in_string = True
            elif char in "[{":
                depth += 1
                _bound("json_depth", depth)
            elif char in "]}":
                depth -= 1
                if depth < 0:
                    raise _ParseFailure()
        value = json.loads(text, object_pairs_hook=_pairs, parse_int=_scalar, parse_float=_scalar, parse_constant=_scalar)
        pending = [value]
        while pending:
            item = pending.pop()
            if isinstance(item, str):
                _bound("string_code_points", len(item))
                if unicodedata.normalize("NFC", item) != item or any(0xD800 <= ord(c) <= 0xDFFF for c in item):
                    raise _ParseFailure()
            elif isinstance(item, dict):
                pending.extend(reversed(tuple(item.values())))
                pending.extend(reversed(tuple(item.keys())))
            elif isinstance(item, list):
                _bound("array_elements", len(item))
                pending.extend(reversed(item))
            else:
                raise _ParseFailure()
    except (UnicodeError, json.JSONDecodeError, _ParseFailure) as exc:
        return GraphCompilationFailed((diagnostic(getattr(exc, "code", "P08E001_INVALID_SOURCE"),
            stage="parse", source_id=source_id, details=getattr(exc, "details", {})),))

    collector = DiagnosticCollector(source_id)
    schema = GRAPH_CONTRACT_DATA["authoring_schema"]
    grammars = GRAPH_CONTRACT_DATA["identity_grammars"]
    current_node = None

    def wrong(path):
        collector.add("P08E003_SCHEMA_MISMATCH", stage="schema", field_path=path, node_source_order=current_node)

    def fields(value, kind, path):
        if not isinstance(value, dict):
            wrong(path)
            return False
        for name in schema[kind]:
            if name not in value:
                wrong(path + "." + name)
        for name in sorted(set(value) - set(schema[kind])):
            wrong(path + "." + name if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name) else path)
        return all(name in value for name in schema[kind])

    def identity(value, kind, path):
        if isinstance(value, str) and len(value) > LIMITS["identifier_code_points"]:
            collector.add("P08E401_LIMIT_VIOLATION", stage="schema", field_path=path, node_source_order=current_node,
                details=dict(resource="identifier_code_points", limit=LIMITS["identifier_code_points"], observed=len(value)))
        elif not isinstance(value, str) or not re.fullmatch(grammars[kind], value):
            wrong(path)

    if fields(value, "document", "$"):
        if value["graph_schema_version"] != CONTRACTS["schema"]:
            wrong("$.graph_schema_version")
        for name in ("system", "rule_set_family", "rule_set_version"):
            identity(value[name], "identity", "$." + name)
        if not isinstance(value["rules"], list):
            wrong("$.rules")
        else:
            positions = rule_positions or {}
            def row_key(pair):
                index, row = pair
                rule_id = row.get("rule_id") if isinstance(row, dict) else None
                revision = row.get("revision") if isinstance(row, dict) else None
                return (positions.get(rule_id, LIMITS["nodes"]) if isinstance(rule_id, str) else LIMITS["nodes"],
                    rule_id if isinstance(rule_id, str) else "", revision if isinstance(revision, str) else "", index)
            for ordinal, (index, row) in enumerate(sorted(enumerate(value["rules"]), key=row_key)):
                rule_id = row.get("rule_id") if isinstance(row, dict) else None
                current_node = positions.get(rule_id) if isinstance(rule_id, str) else None
                i = current_node if current_node is not None else ordinal
                path = f"$.rules[{i}]"
                if not fields(row, "rule", path):
                    continue
                identity(row["rule_id"], "rule_id", path + ".rule_id")
                identity(row["revision"], "revision", path + ".revision")
                for kind in KINDS:
                    if not isinstance(row[kind], list):
                        wrong(path + "." + kind)
                        continue
                    def reference_key(reference):
                        if not isinstance(reference, dict):
                            return ("", "")
                        return tuple(reference.get(k) if isinstance(reference.get(k), str) else "" for k in ("rule_id", "revision"))
                    for j, reference in enumerate(sorted(row[kind], key=reference_key)):
                        ref_path = f"{path}.{kind}[{j}]"
                        if fields(reference, "reference", ref_path):
                            identity(reference["rule_id"], "rule_id", ref_path + ".rule_id")
                            identity(reference["revision"], "revision", ref_path + ".revision")
    if collector.items:
        return GraphCompilationFailed(collector.finish())
    return ParsedGraph(FrozenMapping(value), hashlib.sha256(raw).hexdigest())
