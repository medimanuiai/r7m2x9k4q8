from typing import Dict, Any, List, Set
from pathlib import Path
import json


class CoverageEngine:
    def __init__(self):
        self.covered: Dict[str, Set] = {
            'lagnas': set(),
            'houses': set(),
            'signs': set(),
            'planets': set(),
            'dignities': set(),
            'retrograde': set(),
            'combust': set(),
            'friendships': set(),
            'yogas': set(),
            'dashas': set(),
            'transits': set(),
            'vargas': set(),
        }

    def ingest_astro(self, astro: Dict[str, Any]):
        # Accept either 'diagnostics' or 'enrichments' top-level keys
        diag = astro.get('diagnostics', {}) or {}
        enrich = astro.get('enrichments', {}) or {}
        # lagna
        lagna = diag.get('lagna_summary', {}).get('sign') or enrich.get('lagna_summary', {}).get('sign')
        if lagna:
            self.covered['lagnas'].add(lagna)
        # planets & planet-level attributes
        planets = diag.get('planet_strengths', {}) or {}
        for pname, pinfo in planets.items():
            self.covered['planets'].add(pname)
            if isinstance(pinfo, dict):
                # dignity
                d = pinfo.get('dignity')
                if d:
                    self.covered['dignities'].add(d)
                # retrograde
                if pinfo.get('retrograde'):
                    self.covered['retrograde'].add(pname)
                # combust
                if pinfo.get('combust'):
                    self.covered['combust'].add(pname)
                # temporary friendship
                tf = pinfo.get('temporary_friendship')
                if tf:
                    self.covered['friendships'].add(tf)
                # yogas listed on planet info
                y = pinfo.get('yogas') or []
                for yy in y:
                    self.covered['yogas'].add(yy)
        # houses
        houses = diag.get('houses') or []
        for h in houses:
            n = h.get('number') if isinstance(h, dict) else None
            if n:
                self.covered['houses'].add(int(n))
            # house-level yogas or occupants
            if isinstance(h, dict):
                for y in h.get('yogas', []) or []:
                    self.covered['yogas'].add(y)
        # add top-level yogas/dashas/transits/vargas if provided in diagnostics or enrichments
        for key in ('yogas', 'dashas', 'transits', 'vargas'):
            arr = diag.get(key) or enrich.get(key) or []
            for it in arr:
                try:
                    # items may be dicts or strings
                    if isinstance(it, dict):
                        # schema-aware extraction
                        self.covered[key].add(it.get('id') or it.get('name') or str(it))
                    else:
                        self.covered[key].add(str(it))
                except Exception:
                    continue

        # transit detectors: look for common transit shapes in enrichments
        trans = enrich.get('transits') or diag.get('transits') or []
        for t in trans:
            if isinstance(t, dict):
                # e.g., {'planet': 'Mars', 'to': '10', 'aspect': 'conjunction'}
                pid = t.get('planet') or t.get('id')
                if pid:
                    self.covered['transits'].add(str(pid))
                # detect target houses or planets
                if t.get('to'):
                    self.covered['transits'].add(f"to:{t.get('to')}")
                if t.get('target'):
                    self.covered['transits'].add(f"target:{t.get('target')}")

        # dasha parsing: support arrays of dicts with 'name' and 'period'
        dashas = enrich.get('dashas') or diag.get('dashas') or []
        for d in dashas:
            if isinstance(d, dict):
                name = d.get('name') or d.get('id')
                if name:
                    self.covered['dashas'].add(str(name))
                period = d.get('period')
                if period:
                    self.covered['dashas'].add(f"period:{period}")

    def ingest_rule_coverage(self, rule_summary: Dict[str, Any]):
        # rule_summary is expected to look like instrumentation.summary()
        rules = (rule_summary or {}).get('rules', {}).get('hits', {}) or {}
        # store rule ids count under 'rules' key
        if 'rules' not in self.covered:
            self.covered['rules'] = set()
        for rid in rules.keys():
            self.covered['rules'].add(rid)

    def report(self) -> Dict[str, int]:
        return {k: len(v) for k, v in self.covered.items()}

    def save(self, path: str):
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        out = {k: sorted(list(v)) for k, v in self.covered.items()}
        p.write_text(json.dumps(out, indent=2))
