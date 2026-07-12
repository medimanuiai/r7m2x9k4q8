import json
from pathlib import Path
from typing import Dict, List, Optional, Any


class GoldenChartLibrary:
    def __init__(self, base_dir: str):
        self.base = Path(base_dir)

    def list_golden_charts(self):
        return list(self.base.glob('*.json'))

    def load(self, name: str) -> Dict[str, Any]:
        p = self.base / name
        with p.open('r', encoding='utf-8') as fh:
            return json.load(fh)

    def find_by_id(self, chart_id: str) -> Optional[Dict[str, Any]]:
        # naive: match filename contains id
        for p in self.list_golden_charts():
            if chart_id in p.name:
                with p.open('r', encoding='utf-8') as fh:
                    return json.load(fh)
        return None
