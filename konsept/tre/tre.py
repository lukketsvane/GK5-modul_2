# -*- coding: utf-8 -*-
"""
tre.py  ·  dei tre konsepta til 17. november, rekna likt

Kvart konsept er eit lysgrep frå formfamiliane i ../reflektor, med rettingane skeptikarane fann:

  A  Skiva     bøygd spegel, kuv R 1,2 m, Ø 250 mm, vippar frå veggen til feltet      (reflektor/boy)
  B  Over      fresnelplata over skjermkanten, diode i brønn 50°, vippar               (reflektor/fresnel)
  C  Vindauge  linse, maske og delt frontflatespegel: vindauget blir, feltet kjem      (reflektor/projektor)

Same rom, same mannekeng, same watt (1,25 W i stemning, 5 W i arbeid), same tal().

  python tre.py tal          tabell til tal.md
  python tre.py ark A        konseptark for A (B, C)
"""
import os, sys, math, importlib.util, json
import numpy as np

HER = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(HER, '..', 'reflektor')
sys.path.insert(0, os.path.join(HER, '..', 'lysskisse'))
import lysskisse as ls
from lysskisse import b, YV, FELT, watt

def _last(namn, fil):
    spec = importlib.util.spec_from_file_location(namn, fil)
    m = importlib.util.module_from_spec(spec)
    sys.modules[namn] = m
    spec.loader.exec_module(m)
    return m

boy = _last('fam_boy', os.path.join(REF, 'boy', 'familie.py'))
fre = _last('fam_fresnel', os.path.join(REF, 'fresnel', 'familie.py'))
pro = _last('fam_projektor', os.path.join(REF, 'projektor', 'familie.py'))

# Retting frå etterprøvinga av projektor: maska i trakta stengjer lyset utanfor opninga.
# Berre 0,47 av lyset kjem gjennom (0,62 med trakta tilpassa maska).
TRAKT_MASKE = 0.47
_lpw = pro.lumen_per_watt
def _lpw_retta(o, mm, u, spegel=0, blad=1.0):
    v, t = _lpw(o, mm, u, spegel, blad)
    if o.get('type') == 'trakt':
        return v * TRAKT_MASKE, t + ' · maske i trakta ×%.2f' % TRAKT_MASKE
    return v, t
pro.lumen_per_watt = _lpw_retta

def _finn(mod, namn):
    """Siste lysgrep med dette namnet i alle lister i modulen (2- eller 3-tuplar)."""
    funne = None
    for v in vars(mod).values():
        if isinstance(v, list):
            for e in v:
                if isinstance(e, tuple) and e and e[0] == namn and callable(e[-1]):
                    funne = e[-1]
    if funne is None: raise KeyError(namn)
    return funne

# ------------------------------------------------------------------ kroppane på arka
# Berre det auget ser: lysrekninga er den same (sjå kontroll() under).

def _med_kantskive(g, bak=0.0075):
    """Rund, svart skive rett bak den bøygde spegelen. Fliser på 11 mm gjev takka kant, skiva gjev rund silhuett.
    Ho står bak den djupaste kanten (kuv R 1,2 m har pil 6,5 mm), så ho skuggar ikkje spegelflata."""
    def g2(t):
        lys, kropp = g(t)
        a = next(l for l in lys if isinstance(l, ls.Ark))
        n = ls.nrm(a.Nf.mean(0)); c = a.Pf.mean(0)
        V = np.concatenate([a.prim.V0, a.prim.V0 + a.prim.E1, a.prim.V0 + a.prim.E2]) - c
        r = float(np.linalg.norm(V - np.outer(V @ n, n), axis=1).max())    # ytste hjørne på flisene, så tennene blir dekte
        return lys, list(kropp) + [ls.skive(c - bak * n, n, r)]
    return g2

def _med_stolpe(g, x=0.31, y=0.49, r=0.006):
    """Stolpen frå projektoren: står bak skjermen ved høgre kant og ber plata i eit hengsel langs bakkanten."""
    def g2(t):
        lys, kropp = g(t)
        a = next(l for l in lys if isinstance(l, ls.Ark))
        P = a.Pf
        midt = np.abs(P[:, 0] - P[:, 0].mean()) < 0.02
        hengsel = P[midt][np.argmax(P[midt][:, 1])]                     # midt på bakkanten
        topp = b(x, y, hengsel[2] - ls.ZB)
        return lys, list(kropp) + [ls.syl(b(x, y, 0), topp, r), ls.syl(topp, hengsel, r * 0.8),
                                   ls.syl(b(x, y, 0), b(x, y, 0.012), 0.045)]
    return g2

# ------------------------------------------------------------------ dei tre, etter søket 13.11 (a_sok, b_sok, c_sok)

def _A(t):
    import a_sok   # fast flik på stamma til veggen bak skjermen, 40 % av watten, satin, 12 x 8,4 cm, 30 cm over bordet
    return a_sok.a_ny(0.40, 0.30, 0.12, 0.084, ls.SATIN)(t)

def _B(t):
    import b_sok   # plata knekt: flik 60 mm mot veggen bak skjermen, diffusorark 14°, plata 62 cm over bordet
    return b_sok.b_ny(0.62, 0.06, 14, b(0.0, YV, 0.60))(t)

def _C(t):
    import c_sok   # vasskule Ø 70 mm, hovudet 70 cm over bordet, gråfilter 1,5 i maska, 65 % til bordet i arbeid
    return c_sok.c_ny(c_sok.LINSER['vasskule'], 0.65, 0.06, 0.0, grad=1.5, pos=b(0.40, 0.42, 0.70), fot=(0.40, 0.50))(t)

KONSEPT = {
    'A': dict(namn='Skiva', g=_A,
              setning='Ei kjelde i foten lyser opp på ei bøygd spegelskive som vippar frå veggen ned på feltet. Ein fast flik på stamma held veggen bak skjermen lys.',
              handling='Handlinga: vipp skiva.', familie='boy', kandidat='spegel-kuv-1.2 med veggflik'),
    'B': dict(namn='Over', g=_B,
              setning='Fresnelplata over skjermkanten er knekt. Den store delen vippar lyset frå veggen ned på bordet, fliken held veggen bak skjermen lys.',
              handling='Handlinga: vipp plata.', familie='fresnel', kandidat='over-knekk, brønn 50°, flik 60 mm, ark 14°'),
    'C': dict(namn='Vindauge', g=_C,
              setning='Ei vasskule teiknar eit vindauge av lys på veggen. Ein spegel glir inn i strålen og legg feltet på bordet, medan vindauget blir.',
              handling='Handlinga: skyv spegelen inn.', familie='projektor', kandidat='dele-vindauge med vasskule, gråfilter og høgt hovud'),
}

# Versjonane frå første runde (før veggen bak skjermen og jamnheita), til samanlikning
FORSTE = {
    'A': _med_kantskive(_finn(boy, 'spegel-kuv-1.2')),
    'B': _med_stolpe(lambda t: fre.plate(t, fre.OVER_C, fre.OVER_A, 0.12, fre.gli(b(0.0, YV, 0.60), FELT), spreiing=12, kjelde=(40, 50, 50))),
    'C': _finn(pro, 'dele-vindauge'),
}

def rekn(k, n=5):
    g = KONSEPT[k]['g']
    R, m = ls.overgang(g, n=n)
    s, a = R[0], R[-1]
    Ea = max(a['E_felt'], 1e-9); f = 350.0 / Ea
    La = lambda d: max(d['L_lampe'], d['L_flate'])
    rad = dict(
        konsept=k, namn=KONSEPT[k]['namn'], W350=a['W'] * f, timar=ls.CELLE / (a['W'] * f), jamnheit=a['U'],
        vegg350=a['E_vegg'] * f, bak350=a['E_bak'] * f, ansikt350=a['E_ansikt'] * f, skjerm350=a['E_skjerm'] * f,
        auge25=max(a['L_auge25'], a['L_flate']) * f, auge47=La(a) * f, auge60=max(a['L_auge60'], a['L_flate']) * f,
        s_W=s['W'], s_felt=s['E_felt'], s_vegg=s['E_vegg'], s_bak=s['E_bak'], s_skjerm=s['E_skjerm'],
        s_auge25=max(s['L_auge25'], s['L_flate']), s_auge47=La(s), s_auge60=max(s['L_auge60'], s['L_flate']),
        likskap=ls.likskap(s['_fordeling'], a['_fordeling']), topp=m['topp'], sprang=m['sprang'], jamn_auke=m['jamn_auke'],
        veg_felt=[r['E_felt'] for r in R], veg_auge=[La(r) for r in R], veg_skjerm=[r['E_skjerm'] for r in R],
        strekk=max(a.get('strekk', 0), s.get('strekk', 0)))
    return rad

def f0(x): return f'{x:,.0f}'.replace(',', ' ')
def f1(x): return f'{x:.1f}'.replace('.', ',')
def f2(x): return f'{x:.2f}'.replace('.', ',')

def tabell(rader):
    def ok(v, krav): return v if krav else v + ' (ikkje halde)'
    L = ['| | ' + ' | '.join(f"{r['konsept']} {r['namn']}" for r in rader) + ' |', '| --- |' + ' --- |' * len(rader)]
    lin = [
        ('Watt for 350 lx på feltet (tak 7,5)', lambda r: ok(f2(r['W350']), r['W350'] <= 7.5)),
        ('Timar per celle ved 350 lx', lambda r: f1(r['timar'])),
        ('Jamnheit (referanse 0,6)', lambda r: f2(r['jamnheit'])),
        ('Mot auget ved 350 lx, 25 / 47 / 60 cm (F1 3000, F5 1500)', lambda r: ok(f"{f0(r['auge25'])} / {f0(r['auge47'])} / {f0(r['auge60'])}", max(r['auge25'], r['auge47'], r['auge60']) <= 3000)),
        ('Veggen bak skjermen ved 350 lx (F6 100 til 150)', lambda r: ok(f0(r['bak350']), r['bak350'] >= 100)),
        ('Veggsona ved 350 lx', lambda r: f0(r['vegg350'])),
        ('Skjermflata ved 350 lx (del av feltet)', lambda r: f"{f0(r['skjerm350'])} ({f2(r['skjerm350'] / 350)})"),
        ('Ansiktet ved 350 lx', lambda r: f0(r['ansikt350'])),
        ('Stemning: mot auget 25 / 47 / 60 cm (krav 500)', lambda r: ok(f"{f0(r['s_auge25'])} / {f0(r['s_auge47'])} / {f0(r['s_auge60'])}", max(r['s_auge25'], r['s_auge47'], r['s_auge60']) <= 500)),
        ('Stemning: veggen bak skjermen / sona, lx', lambda r: f"{f0(r['s_bak'])} / {f0(r['s_vegg'])}"),
        ('Stemning: feltet / skjermflata, lx', lambda r: f"{f0(r['s_felt'])} / {f0(r['s_skjerm'])}"),
        ('Likskap stemning og arbeid (over 0,9 er dimmar)', lambda r: f2(r['likskap'])),
        ('Lysaste mellomsteg mot auget / største sprang', lambda r: f"{f2(r['topp'])} / {f2(r['sprang'])}"),
        ('Feltet langs overgangen, lx', lambda r: ' · '.join(f0(x) for x in r['veg_felt'])),
        ('Skjermflata langs overgangen, lx', lambda r: ' · '.join(f0(x) for x in r['veg_skjerm'])),
    ]
    for t, fn in lin:
        L.append(f'| {t} | ' + ' | '.join(fn(r) for r in rader) + ' |')
    return '\n'.join(L) + '\n'

if __name__ == '__main__':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass
    a = sys.argv[1:]
    if a and a[0] == 'tal':
        nokkel = a[1:] or list(KONSEPT)
        rader = []
        for k in nokkel:
            r = rekn(k); rader.append(r)
            json.dump(r, open(os.path.join(HER, f'tal-{k}.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
            print(k, {x: (round(v, 2) if isinstance(v, float) else v) for x, v in r.items() if not isinstance(v, list)})
        if len(rader) == len(KONSEPT):
            open(os.path.join(HER, 'tal.md'), 'w', encoding='utf-8').write(tabell(rader))
            print(tabell(rader))
    elif a and a[0] == 'tabell':
        rader = [json.load(open(os.path.join(HER, f'tal-{k}.json'), encoding='utf-8')) for k in KONSEPT]
        open(os.path.join(HER, 'tal.md'), 'w', encoding='utf-8').write(tabell(rader)); print(tabell(rader))
    elif a and a[0] == 'ark':
        import studie
        k = a[1]; K = KONSEPT[k]; px = int(a[2]) if len(a) > 2 else 560
        r = studie.konseptark(f"{k}  {K['namn']}", K['setning'], K['g'], fil=os.path.join(HER, f'ark-{k}-{K["namn"].lower()}.png'),
                              px=px, ss=1, handling=K['handling'])
        print(k, 'ferdig', {x: round(float(v), 2) for x, v in r.items() if isinstance(v, (int, float))})
