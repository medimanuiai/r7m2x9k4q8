from typing import Optional, Dict, Any, List
from pydantic import BaseModel


class ChartConstraints(BaseModel):
    lagna: Optional[str]
    planet_positions: Optional[Dict[str, Dict[str, Any]]] = None
    # planet_positions example: {'Mars': {'sign': 'Aries', 'house': 10, 'retrograde': True}}


class ExpectedOutputs(BaseModel):
    astrostate: Optional[Dict[str, Any]] = None
    rule_matches_snapshot: Optional[str] = None
    career_snapshot: Optional[str] = None
    full_snapshot: Optional[str] = None


class TestCase(BaseModel):
    id: str
    description: Optional[str]
    input_chart_path: str
    expected: ExpectedOutputs
    tags: List[str] = []
