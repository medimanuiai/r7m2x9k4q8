from typing import Dict, Any
import threading

_lock = threading.Lock()
_rule_hits: Dict[str, int] = {}
_predicate_hits: Dict[str, Dict[bool, int]] = {}


def reset() -> None:
    global _rule_hits, _predicate_hits
    with _lock:
        _rule_hits = {}
        _predicate_hits = {}


def record_rule(rule_id: str) -> None:
    with _lock:
        _rule_hits[rule_id] = _rule_hits.get(rule_id, 0) + 1


def record_predicate(pred_name: str, result: bool) -> None:
    with _lock:
        d = _predicate_hits.get(pred_name) or {True: 0, False: 0}
        d[result] = d.get(result, 0) + 1
        _predicate_hits[pred_name] = d


def rule_report() -> Dict[str, Any]:
    with _lock:
        total = len(_rule_hits)
        return {'total_executed': total, 'hits': dict(_rule_hits)}


def predicate_report() -> Dict[str, Any]:
    with _lock:
        return {k: dict(v) for k, v in _predicate_hits.items()}


def summary() -> Dict[str, Any]:
    return {'rules': rule_report(), 'predicates': predicate_report()}
