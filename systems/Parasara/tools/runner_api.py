"""CLI runner that reads a birth record JSON from STDIN and writes a Parasara
snapshot JSON to STDOUT. Used by the Next.js API route for synchronous calls.

Input (JSON from stdin): {
  "dob": "YYYY-MM-DD",
  "time": "HH:MM",
  "lat": 12.34,
  "lon": 56.78,
  "tz": "Asia/Kolkata",          # optional
  "place": "City, Country"      # optional
}

Output: JSON snapshot printed to stdout.
"""
import sys
import json
import tempfile
from pathlib import Path
from datetime import datetime, timezone

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def main():
    try:
        data = json.load(sys.stdin)
    except Exception as e:
        eprint("Invalid JSON on stdin:", e)
        sys.exit(2)

    lat = data.get('lat')
    lon = data.get('lon')
    dob = data.get('dob')
    time = data.get('time')
    tz = data.get('tz')

    if lat is None or lon is None:
        eprint('lat and lon required')
        sys.exit(3)

    if not dob or not time:
        eprint('dob and time required')
        sys.exit(4)

    # build timezone-aware datetime
    try:
        # combine date and time
        dt_str = f"{dob}T{time}"
        dt = datetime.fromisoformat(dt_str)
        if tz:
            try:
                from zoneinfo import ZoneInfo
                dt = dt.replace(tzinfo=ZoneInfo(tz))
            except Exception:
                # fallback to UTC if timezone unknown
                dt = dt.replace(tzinfo=timezone.utc)
        else:
            # assume UTC if no tz provided
            dt = dt.replace(tzinfo=timezone.utc)
    except Exception as e:
        eprint('Invalid dob/time:', e)
        sys.exit(5)

    try:
        # Ensure the repository root is on sys.path so `systems.*` imports work
        # runner_api.py is at systems/Parasara/tools; repo root is parents[3]
        resolved = Path(__file__).resolve()
        eprint('runner_api resolved path:', str(resolved))
        repo_root = resolved.parents[3]
        repo_root_str = str(repo_root)
        if repo_root_str not in sys.path:
            sys.path.insert(0, repo_root_str)
            eprint('Added to sys.path for imports:', repo_root_str)
        else:
            eprint('Repo root already on sys.path:', repo_root_str)
        # import local generator utilities
        from systems.Parasara.tools.surya_to_parasara import generate_chart
        from systems.Parasara.tools.generate_snapshot import generate as gen_snap
    except Exception as e:
        eprint('Failed to import generator modules:', e)
        sys.exit(6)

    try:
        chart = generate_chart(float(lat), float(lon), dt)
    except Exception as e:
        eprint('Failed to compute planetary positions:', e)
        sys.exit(7)

    # write chart to temp file and invoke existing generate() which accepts input path
    tmp_chart = Path(tempfile.mkstemp(prefix='surya_chart_', suffix='.json')[1])
    tmp_out = Path(tempfile.mkstemp(prefix='parasara_out_', suffix='.json')[1])
    try:
        tmp_chart.write_text(json.dumps(chart))
        out = gen_snap(str(tmp_chart), str(tmp_out))
        # gen_snap writes file and returns dict — include the raw Surya chart for frontend inspection
        out_with_chart = {
            'snapshot': out,
            'surya_chart': chart,
        }
        sys.stdout.write(json.dumps(out_with_chart))
        sys.stdout.flush()
    except Exception as e:
        eprint('Failed to generate snapshot:', e)
        sys.exit(8)
    finally:
        try:
            tmp_chart.unlink()
        except Exception:
            pass
        try:
            tmp_out.unlink()
        except Exception:
            pass


if __name__ == '__main__':
    main()
