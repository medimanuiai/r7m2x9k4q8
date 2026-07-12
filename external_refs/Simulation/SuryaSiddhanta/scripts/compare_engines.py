"""Compare SuryaSiddhanta `ndastro_engine` outputs with reference engines.

Runs only inside external_refs/Simulation/SuryaSiddhanta and handles missing refs gracefully.
"""
import json
import sys
from datetime import datetime
from importlib import import_module
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SURYA_PKG_PATH = ROOT / "systems" / "SuryaSiddhanta"

# load fixtures
fixtures_path = HERE / ".." / "fixtures" / "fixtures.json"
fixtures = json.loads(fixtures_path.read_text())

report = {}

# Helper to safely import external engines
def try_import(module_path, add_sys_path=None):
    if add_sys_path:
        sys.path.insert(0, str(add_sys_path))
    try:
        mod = import_module(module_path)
        return mod
    except Exception as exc:
        return None
    finally:
        if add_sys_path:
            try:
                sys.path.remove(str(add_sys_path))
            except Exception:
                pass

# Import SuryaSiddhanta engine (local system). Add package dir so internal
# `from ndastro_engine import ...` imports succeed when loading modules.
try:
    sys.path.insert(0, str(SURYA_PKG_PATH))
    from ndastro_engine.core import get_planet_position, get_planets_position
    from ndastro_engine.ayanamsa import get_ayanamsa
    from ndastro_engine.dasa import DasaContext, get_dasa_birth_info, get_dasa_timeline
    from ndastro_engine.enums import Planets
except Exception as e:
    print("Failed to import SuryaSiddhanta engine:", e)
    raise
finally:
    try:
        sys.path.remove(str(SURYA_PKG_PATH))
    except Exception:
        pass

# Try import VedicAstroEngineLite by adding its repo folder to sys.path
VAE_PATH = ROOT / "external_refs" / "VedicAstroEngineLite"
vae_mod = None
if VAE_PATH.exists():
    try:
        sys.path.insert(0, str(VAE_PATH))
        import importlib
        vae_mod = importlib.import_module("vedic_astro_engine")
    except Exception:
        vae_mod = None
    finally:
        try:
            sys.path.remove(str(VAE_PATH))
        except Exception:
            pass

# Try import VedAstro (best-effort)
VED_PATH = ROOT / "external_refs" / "VedAstro.Python"
ved_mod = None
if VED_PATH.exists():
    try:
        sys.path.insert(0, str(VED_PATH))
        import importlib
        ved_mod = importlib.import_module("vedastro")
    except Exception:
        ved_mod = None
    finally:
        try:
            sys.path.remove(str(VED_PATH))
        except Exception:
            pass

def run_surya_for_fixture(fx):
    dt = datetime.fromisoformat(fx["datetime_utc"])
    out = {}
    # get planets for core set (use Planets enum) including nodes and ascendant
    planet_list = [
        Planets.SUN,
        Planets.MOON,
        Planets.MARS,
        Planets.MERCURY,
        Planets.JUPITER,
        Planets.VENUS,
        Planets.SATURN,
        Planets.RAHU,
        Planets.KETHU,
        Planets.ASCENDANT,
    ]
    try:
        ayan = get_ayanamsa(dt, "lahiri")
    except Exception:
        ayan = None
    for p in planet_list:
        key = p.name
        try:
            pos = get_planet_position(p, fx["lat"], fx["lon"], dt)
            trop = pos.longitude
            sid = None
            if ayan is not None:
                sid = (trop - ayan) % 360.0
            out[key] = {"tropical": trop, "sidereal": sid}
        except Exception as e:
            out[key] = {"error": str(e)}
    # ayan
    try:
        out["ayanamsa_lahiri"] = get_ayanamsa(dt, "lahiri")
    except Exception as e:
        out["ayanamsa_lahiri"] = str(e)

    # dasa info
    try:
        ctx = DasaContext(birth_datetime=dt, lat=fx["lat"], lon=fx["lon"], ayanamsa_system="lahiri")
        dbi = get_dasa_birth_info(ctx)
        out["sidereal_moon"] = dbi.sidereal_moon_longitude
        out["janma_nakshatra"] = dbi.janma_nakshatra.name
    except Exception as e:
        out["dasa_error"] = str(e)
    # dasa timeline (top-level mahadasa starts)
    try:
        timeline = get_dasa_timeline(ctx)
        # return first 6 mahadasa start datetimes as ISO strings
        mahadasa_starts = [p.start_utc.isoformat() for p in timeline[:6]]
        out["dasa_maha_starts"] = mahadasa_starts
    except Exception:
        pass

    return out

def run_vael_for_fixture(fx):
    VAE_PATH = ROOT / "external_refs" / "VedicAstroEngineLite"
    if not VAE_PATH.exists():
        return None
    try:
        sys.path.insert(0, str(VAE_PATH))
        import importlib
        vae = importlib.import_module("vedic_astro_engine")
        dt = datetime.fromisoformat(fx["datetime_utc"])
        res = vae.build_charts(dt.year, dt.month, dt.day, dt.hour, dt.minute, fx["lat"], fx["lon"], ayanamsha_type="LAHIRI")
        planets = {}
        for name, data in (res.get("planets") or {}).items():
            try:
                planets[name.upper()] = data.get("longitude")
            except Exception:
                pass
        # include lagna if present
        lagna = res.get("lagna") or res.get("lagna_longitude")
        dashas = res.get("dashas")
        out = {"planets": planets, "ayanamsha": res.get("ayanamsha"), "lagna": lagna, "dashas": dashas}
        return out
    except Exception as e:
        return {"error": str(e)}
    finally:
        try:
            sys.path.remove(str(VAE_PATH))
        except Exception:
            pass

def run_ved_for_fixture(fx):
    if not ved_mod:
        return None
    try:
        from importlib import reload
        reload(ved_mod)
        calc = ved_mod.vedastro.calculate
        # vedastro Calculate API expects custom classes; use demo helper if present
        # fallback: return None if integration is complex
        return {"note": "VedAstro integration not implemented in lightweight script"}
    except Exception as e:
        return {"error": str(e)}

for fx in fixtures:
    name = fx["name"]
    report[name] = {}
    report[name]["surya"] = run_surya_for_fixture(fx)
    report[name]["vael"] = run_vael_for_fixture(fx)
    report[name]["ved"] = run_ved_for_fixture(fx)

    # compute deltas between Surya and VAE if both present
    try:
        s = report[name]["surya"]
        v = report[name]["vael"]
        if s and v and isinstance(v, dict) and "planets" in v:
            deltas = {}
            tol = 0.05  # degrees
            for p in ["SUN","MOON","MARS","MERCURY","JUPITER","VENUS","SATURN"]:
                if p in s and p in v["planets"]:
                    try:
                        s_lon = float(s[p].get("sidereal") if isinstance(s[p], dict) else s[p])
                        v_lon = float(v["planets"][p])
                        diff = abs(((s_lon - v_lon + 180) % 360) - 180)
                        deltas[p] = {"surya": s_lon, "vael": v_lon, "delta_deg": diff, "within_tol": diff <= tol}
                    except Exception as e:
                        deltas[p] = {"error": str(e)}
            # compare ascendant/lagna if present
            try:
                if "LAGNA" in s and v.get("lagna"):
                    s_lon = float(s["LAGNA"].get("sidereal") if isinstance(s["LAGNA"], dict) else s["LAGNA"])
                    v_lon = float(v.get("lagna"))
                    diff = abs(((s_lon - v_lon + 180) % 360) - 180)
                    deltas["LAGNA"] = {"surya": s_lon, "vael": v_lon, "delta_deg": diff, "within_tol": diff <= tol}
            except Exception:
                pass
            # compare nodes if present in vae
            for node in ["RAHU", "KETU"]:
                try:
                    if node in s and node in v["planets"]:
                        s_lon = float(s[node].get("sidereal") if isinstance(s[node], dict) else s[node])
                        v_lon = float(v["planets"][node])
                        diff = abs(((s_lon - v_lon + 180) % 360) - 180)
                        deltas[node] = {"surya": s_lon, "vael": v_lon, "delta_deg": diff, "within_tol": diff <= tol}
                except Exception:
                    pass
            # compare dasa starts if both provided
            try:
                if s.get("dasa_maha_starts") and v.get("dashas"):
                    # VAE dashas structure varies; try common keys
                    vae_dashas = v.get("dashas")
                    vae_maha = None
                    if isinstance(vae_dashas, dict):
                        # try vimsottari
                        vae_maha = vae_dashas.get("vimsottari") or list(vae_dashas.values())[0]
                    if isinstance(vae_maha, list):
                        # assume list of dicts with 'start' key
                        v_starts = [str(item.get("start")) for item in vae_maha[:6]]
                        s_starts = s.get("dasa_maha_starts")
                        report[name]["dasa_compare"] = {"surya": s_starts, "vael": v_starts}
            except Exception:
                pass
            report[name]["deltas_surya_vael"] = deltas
    except Exception:
        pass

print(json.dumps(report, indent=2))
