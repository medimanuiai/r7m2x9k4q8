import json
from typing import Dict


def generate_from_constraints(base_chart_path: str, constraints: Dict, out_path: str) -> str:
    """Generate a synthetic chart by applying constraints onto a base chart JSON.

    This is a deterministic, constraint-applier rather than a full ephemeris generator.
    It modifies fields like lagna.sign, planet sign, house, and motion.retrograde.
    Returns path to generated chart (out_path).
    """
    with open(base_chart_path, 'r', encoding='utf-8') as fh:
        data = json.load(fh)

    # Apply lagna
    lagna = constraints.get('lagna')
    if lagna:
        if 'lagna' not in data:
            data['lagna'] = {}
        data['lagna']['sign'] = lagna

    pp = constraints.get('planet_positions') or {}
    if pp:
        planets = data.get('planets', [])
        name_map = {p.get('name'): p for p in planets}
        for pname, spec in pp.items():
            p = name_map.get(pname)
            if not p:
                # create minimal planet obj
                p = {'name': pname}
                planets.append(p)
            if 'sign' in spec:
                p['sign'] = spec['sign']
            if 'house' in spec:
                p['house'] = spec['house']
            if 'degree' in spec:
                p['degree'] = spec['degree']
            # motion flags
            if 'retrograde' in spec:
                if 'motion' not in p:
                    p['motion'] = {}
                p['motion']['retrograde'] = bool(spec['retrograde'])
            # flags
            flags = spec.get('flags')
            if flags:
                p['flags'] = {**p.get('flags', {}), **flags}
        data['planets'] = planets

    with open(out_path, 'w', encoding='utf-8') as fh:
        json.dump(data, fh, indent=2, sort_keys=True)
    return out_path
