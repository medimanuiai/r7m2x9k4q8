"""CLI helper: dump varga summaries for a Surya JSON chart or list of charts."""
import json
from pathlib import Path
from typing import Any

from systems.Parasara.engine.adapter.surya_adapter import SuryaAdapter
from systems.Parasara.engine.astrostate_api import (
    AstroStateBuildFailure,
    freeze_astrostate,
    thaw_value,
)
from systems.Parasara.engine.capability import CapabilityReadiness
from systems.Parasara.engine.normalizer import chart_to_astrostate


def _ordered_mapping(value: dict[str, Any], keys: tuple[str, ...]) -> dict[str, Any]:
    return {
        key: value[key]
        for key in keys + tuple(sorted(set(value) - set(keys)))
        if key in value
    }


def _legacy_strength_row(value: Any) -> Any:
    if not isinstance(value, dict):
        return value
    result = _ordered_mapping(value, (
        'planet', 'dignity', 'shadbala', 'functional_role', 'combust',
        'retrograde', 'temporary_friendship', 'strength',
        'strength_components', 'natural_role', 'owns_houses',
        'functional_score', 'yoga_role',
    ))
    if isinstance(result.get('shadbala'), dict):
        result['shadbala'] = _ordered_mapping(result['shadbala'], (
            'rupas', 'dig_bala', 'kala_bala', 'cheshta_bala',
            'drik_bala', 'naisargika',
        ))
    if isinstance(result.get('strength_components'), dict):
        result['strength_components'] = _ordered_mapping(result['strength_components'], (
            'dignity_bonus', 'combust_penalty', 'retro_bonus',
            'temp_friend_bonus', 'varga_bonus',
        ))
    return result


def _legacy_house_summary(value: Any) -> Any:
    if not isinstance(value, dict):
        return value
    return _ordered_mapping(value, (
        'number', 'sign', 'lord', 'occupants', 'lord_strength',
        'benefic_pressure', 'malefic_pressure', 'aspected_by', 'house_score',
    ))


def _legacy_aspects(value: Any) -> Any:
    if isinstance(value, list):
        return [
            _ordered_mapping(item, ('from', 'to', 'type', 'reason'))
            if isinstance(item, dict) else item
            for item in value
        ]
    if isinstance(value, dict):
        result = _ordered_mapping(value, ('edges', 'by_planet', 'config_version'))
        if isinstance(result.get('edges'), list):
            result['edges'] = [
                _ordered_mapping(
                    item,
                    ('source', 'target', 'target_sign', 'kind', 'config_version'),
                )
                if isinstance(item, dict) else item
                for item in result['edges']
            ]
        return result
    return value


def _legacy_varga_position(value: Any) -> Any:
    if isinstance(value, list):
        return [_legacy_varga_position(item) for item in value]
    if isinstance(value, dict):
        return _ordered_mapping(value, (
            'part_index', 'varga_longitude', 'rashi_index', 'rashi_name',
        ))
    return value


def _legacy_vargas(value: dict[str, Any]) -> dict[str, Any]:
    preferred = ('D1', 'D9', 'D60')
    ordered = preferred + tuple(
        sorted(
            set(value) - set(preferred),
            key=lambda item: (
                (0, int(item[1:]))
                if item.startswith('D') and item[1:].isdigit()
                else (1, item)
            ),
        )
    )
    return {key: _legacy_varga_position(value[key]) for key in ordered if key in value}


def dump_vargas(input_path: str, out_path: str | None = None) -> Any:
    p = Path(input_path)
    data = json.load(p.open())
    results = []
    if isinstance(data, list):
        charts = SuryaAdapter.load_many(input_path)
    else:
        charts = [SuryaAdapter.load(input_path)]

    for c in charts:
        astro = chart_to_astrostate(c)
        build = freeze_astrostate(astro)
        if isinstance(build, AstroStateBuildFailure):
            raise ValueError("AstroState snapshot construction failed")
        snapshot = build.snapshot
        planets_result = snapshot.get_planets()
        enrichments = {
            'canonical_planet_ids': {
                item.planet_id: item.planet_id.lower() for item in planets_result.value
            },
            'normalized_degrees': {
                item.planet_id: item.normalized_longitude for item in planets_result.value
            },
            'planet_strengths': {
                item.planet_id: _legacy_strength_row(
                    thaw_value(snapshot.get_planet_strength(item.planet_id).value.value['detail'])
                )
                for item in planets_result.value
                if snapshot.get_planet_strength(item.planet_id).value_present
            },
            'house_summaries': (
                [_legacy_house_summary(thaw_value(item)) for item in snapshot.get_house_summaries().value]
                if snapshot.get_house_summaries().value_present else []
            ),
        }
        whole = snapshot.inspect_capability('aspects.whole_sign_graph')
        aspect_name = (
            'whole_sign_graph'
            if whole.readiness in (CapabilityReadiness.READY, CapabilityReadiness.READY_EMPTY)
            else 'basic_conjunction_list'
        )
        aspects = snapshot.get_aspect_representation(aspect_name)
        if aspects.value_present:
            enrichments['aspects'] = _legacy_aspects(thaw_value(aspects.value))
        varga_result = snapshot.get_vargas()
        metadata_result = snapshot.get_chart_metadata()
        metadata_values = thaw_value(metadata_result.value) if metadata_result.value_present else {}
        location_result = snapshot.get_location()
        if location_result.value_present:
            location = thaw_value(location_result.value)
            metadata_values['birth_location'] = _ordered_mapping(
                location, ('latitude', 'longitude', 'timezone_offset_minutes'),
            )
            metadata_values['birth_location'].pop('place', None)
        metadata = _ordered_mapping(metadata_values, (
            'birth_datetime_utc', 'birth_location', 'ayanamsa', 'house_system',
            'sidereal', 'ephemeris_source',
        ))
        rec = {
            'metadata': metadata,
            'enrichments': enrichments,
            'planets': [{
                'name': item.planet_id,
                'degree_norm': item.normalized_longitude,
                'vargas': _legacy_vargas({
                    varga.varga_id: thaw_value(position.position)
                    for varga in (varga_result.value or ())
                    for position in varga.positions
                    if position.planet_id == item.planet_id
                }) or None,
            } for item in planets_result.value]
        }
        results.append(rec)

    if out_path:
        Path(out_path).write_text(json.dumps(results, indent=2))
    return results


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Dump varga summaries from Surya JSON')
    parser.add_argument('input')
    parser.add_argument('--out', '-o')
    args = parser.parse_args()
    out = dump_vargas(args.input, args.out)
    print('WROTE' if args.out else json.dumps(out, indent=2))


if __name__ == '__main__':
    main()
