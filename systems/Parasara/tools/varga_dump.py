"""CLI helper: dump varga summaries for a Surya JSON chart or list of charts."""
import json
from pathlib import Path
from typing import Any

from systems.Parasara.engine.adapter.surya_adapter import SuryaAdapter
from systems.Parasara.engine.normalizer import chart_to_astrostate


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
        rec = {
            'metadata': astro.metadata,
            'enrichments': astro.enrichments,
            'planets': [{
                'name': p.name,
                'degree_norm': p.degree_norm,
                'vargas': p.vargas
            } for p in astro.planets]
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
