from typing import Dict, Any, List


class CoverageEngine:
    def __init__(self):
        self.covered = {
            'lagnas': set(),
            'houses': set(),
            'signs': set(),
            'planets': set(),
        }

    def ingest_astro(self, astro: Dict[str, Any]):
        # astro expected to have diagnostics.lagna_summary and diagnostics.planet_strengths
        lagna = astro.get('diagnostics', {}).get('lagna_summary', {}).get('sign')
        if lagna:
            self.covered['lagnas'].add(lagna)
        planets = astro.get('diagnostics', {}).get('planet_strengths', {})
        for pname, pinfo in (planets or {}).items():
            self.covered['planets'].add(pname)
            # try sign
            if isinstance(pinfo, dict):
                s = pinfo.get('sign')
                if s:
                    self.covered['signs'].add(s)
        houses = astro.get('diagnostics', {}).get('houses') or []
        for h in houses:
            try:
                n = h.get('number')
                if n:
                    self.covered['houses'].add(n)
            except Exception:
                continue

    def report(self) -> Dict[str, int]:
        return {k: len(v) for k, v in self.covered.items()}
