from typing import Any, Callable, Dict, Tuple, List, Optional
from functools import wraps
from dataclasses import dataclass, field, replace
import json
import time


# Immutable predicate result returned by every predicate
@dataclass(frozen=True)
class PredicateResult:
    matched: bool
    predicate_id: str
    inputs: Dict[str, Any]
    evidence: Dict[str, Any]
    trace_steps: List[Dict[str, Any]]
    errors: List[Dict[str, Any]]
    cache_hit: bool
    evaluation_time_ms: Optional[float]


# predicate registry: name -> callable(params, astro, context) -> PredicateResult
PREDICATE_REGISTRY: Dict[str, Callable[[dict, Any, dict], PredicateResult]] = {}

# simple cache keyed by (astro_id, predicate_name, params_json) -> PredicateResult (with cache_hit=True)
_CACHE: Dict[Tuple[int, str, str], PredicateResult] = {}


def register_predicate(name: str):
    def _decorator(fn: Callable[[dict, Any, dict], PredicateResult]):
        PREDICATE_REGISTRY[name.upper()] = fn
        return fn
    return _decorator


def clear_cache():
    _CACHE.clear()


def _cache_key(astro: Any, pname: str, params: dict):
    try:
        pstr = json.dumps(params or {}, sort_keys=True, default=str)
    except Exception:
        pstr = str(params or {})
    return (id(astro), pname.upper(), pstr)


def _normalize_inputs(params: Optional[dict]) -> Dict[str, Any]:
    if not params:
        return {}
    # ensure empty lists/dicts normalized
    return params


def evaluate_predicate(name: str, params: dict, astro: Any, context: dict) -> PredicateResult:
    key = _cache_key(astro, name, params or {})
    if key in _CACHE:
        return _CACHE[key]
    pname = name.upper()
    fn = PREDICATE_REGISTRY.get(pname)
    inputs = _normalize_inputs(params or {})
    start = time.perf_counter()
    if not fn:
        # unknown predicate -> deterministic failure
        duration = (time.perf_counter() - start) * 1000.0
        res = PredicateResult(
            matched=False,
            predicate_id=pname,
            inputs=inputs,
            evidence={'reason': 'unknown_predicate', 'predicate': pname},
            trace_steps=[],
            errors=[],
            cache_hit=False,
            evaluation_time_ms=duration,
        )
        # store cached copy with cache_hit True
        _CACHE[key] = replace(res, cache_hit=True)
        return res
    try:
        out = fn(inputs or {}, astro, context or {})
        # support legacy tuple return temporarily
        if isinstance(out, tuple):
            ok, evidence = out
            duration = (time.perf_counter() - start) * 1000.0
            res = PredicateResult(
                matched=bool(ok),
                predicate_id=pname,
                inputs=inputs,
                evidence=(evidence or {}),
                trace_steps=[],
                errors=[],
                cache_hit=False,
                evaluation_time_ms=duration,
            )
        elif isinstance(out, PredicateResult):
            # ensure predicate_id and inputs populated
            duration = (time.perf_counter() - start) * 1000.0
            res = out
            # if incoming result missing evaluation_time_ms, replace
            if res.evaluation_time_ms is None:
                res = replace(res, evaluation_time_ms=duration)
        else:
            duration = (time.perf_counter() - start) * 1000.0
            res = PredicateResult(
                matched=False,
                predicate_id=pname,
                inputs=inputs,
                evidence={'reason': 'invalid_predicate_return', 'type': str(type(out))},
                trace_steps=[],
                errors=[{'error': 'invalid_return_type', 'type': str(type(out))}],
                cache_hit=False,
                evaluation_time_ms=duration,
            )
        # store cached copy with cache_hit True
        try:
            _CACHE[key] = replace(res, cache_hit=True)
        except Exception:
            _CACHE[key] = res
        return res
    except Exception as e:
        duration = (time.perf_counter() - start) * 1000.0
        res = PredicateResult(
            matched=False,
            predicate_id=pname,
            inputs=inputs,
            evidence={'reason': 'predicate_error', 'predicate': pname},
            trace_steps=[],
            errors=[{'error': str(e)}],
            cache_hit=False,
            evaluation_time_ms=duration,
        )
        _CACHE[key] = replace(res, cache_hit=True)
        return res


def evaluate_condition(node: dict, astro: Any, context: dict) -> PredicateResult:
    start = time.perf_counter()
    t = node.get('type')
    if t is None:
        duration = (time.perf_counter() - start) * 1000.0
        return PredicateResult(False, 'UNKNOWN', node.get('params', {}) or {}, {'reason': 'missing_type'}, [], [{'error': 'missing_type'}], False, duration)
    t = str(t).upper()
    if t in ('AND', 'OR'):
        children = node.get('children', []) or []
        child_results: List[PredicateResult] = []
        for c in children:
            child_results.append(evaluate_condition(c, astro, context))
        results_bools = [cr.matched for cr in child_results]
        if t == 'AND':
            matched = all(results_bools)
        else:
            matched = any(results_bools)
        evidences = {'children': [cr.evidence for cr in child_results]}
        trace_steps = [
            {'predicate_id': cr.predicate_id, 'matched': cr.matched, 'errors': cr.errors, 'evaluation_time_ms': cr.evaluation_time_ms}
            for cr in child_results
        ]
        errors = [err for cr in child_results for err in cr.errors]
        duration = (time.perf_counter() - start) * 1000.0
        return PredicateResult(matched=matched, predicate_id=t, inputs=node.get('params', {}) or {}, evidence=evidences, trace_steps=trace_steps, errors=errors, cache_hit=False, evaluation_time_ms=duration)
    # leaf predicate: delegate to evaluate_predicate
    params = node.get('params', {}) or {}
    return evaluate_predicate(t, params, astro, context)
