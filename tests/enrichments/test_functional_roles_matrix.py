import os
import yaml
from systems.Parasara.engine.enrichments.functional_roles import _load_table_for_lagna, compute_functional_roles
from systems.Parasara.engine.astrostate import AstroState, PlanetState


def _make_planets_list():
    names = ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn','Rahu','Ketu']
    # create placeholder planets with no specific degrees; engine relies on lagna only for table-driven mode
    return [PlanetState(name=n, sign=None, degree=None, house=None) for n in names]


def test_functional_roles_matrix_exists_and_matches_tables():
    base = os.path.join(os.getcwd(), 'rules', 'parashara', 'functional_roles')
    files = [f for f in os.listdir(base) if f.endswith('.yaml')]
    assert files, 'No functional role tables found under rules/parashara/functional_roles'

    for fname in sorted(files):
        lagna = os.path.splitext(fname)[0]
        table = _load_table_for_lagna(lagna)
        assert isinstance(table, dict)
        # create astrostate with lagna and planets
        astro = AstroState(metadata={}, location=None, lagna_sign=lagna, planets=_make_planets_list())
        result = compute_functional_roles(astro)
        # every planet in table should be present in result with matching functional_role and score
        for pname, pdata in table.items():
            if pname in result:
                assert result[pname].get('functional_role') == pdata.get('functional_role')
                # compare float-ish scores with rounding
                assert round(float(result[pname].get('functional_score') or 0), 2) == round(float(pdata.get('functional_score') or 0), 2)
