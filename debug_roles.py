import sys
sys.path.insert(0,'.')
from systems.Parasara.engine.adapter.surya_adapter import SuryaAdapter
from systems.Parasara.engine.normalizer import chart_to_astrostate
from systems.Parasara.engine.enrichments import planet_strengths as psmod
chart = SuryaAdapter.load('systems/Parasara/fixtures/surya_test_chart.json')
astro = chart_to_astrostate(chart)
print('lagna_sign:', astro.lagna_sign)
LORD_SIGNS = {}
for s,l in psmod.SIGN_LORD.items():
    LORD_SIGNS.setdefault(l, []).append(s)
print('LORD_SIGNS sample:', {k:LORD_SIGNS.get(k) for k in ['Mercury','Mars','Jupiter']})
signs = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
lagna_idx = signs.index(astro.lagna_sign) if astro.lagna_sign in signs else None
for name in ['Mercury','Mars','Moon','Sun']:
    owned = LORD_SIGNS.get(name, [])
    print('\nPlanet',name,'owns',owned)
    wsum=0
    for osign in owned:
        si=signs.index(osign)
        house_num = ((si - lagna_idx) % 12) + 1
        print('  sign',osign,'-> house',house_num,'weight',psmod.HOUSE_ROLE_WEIGHTS.get(house_num))
        wsum += psmod.HOUSE_ROLE_WEIGHTS.get(house_num,0)
    print(' total weight',wsum)
