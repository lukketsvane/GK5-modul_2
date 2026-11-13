# -*- coding: utf-8 -*-
"""rendre.py  ·  studiorendrar av ei kitbash-lampe med innstillingane til byggjesettet

Skriv scenefila og køyrer Blender med rendre_blender.py (ein kopi av modell/byggjesett/rendre_blender.py: same
materiale, lys, verd, kamera, prøvetal og utdata). Tre scener per lampe:

  <namn>-samla     lampa samla, trekvart, svart bakgrunn (som projektoren-samla: asimut -38, elevasjon 22, 50 mm)
  <namn>-sprengt   same kamera, delane dregne frå kvarandre (del.spreng, eller ut frå midten)
  <namn>-del       delbanken: ortografisk, gjennomsiktig bakgrunn, 4 pikslar per mm (asimut -35, elevasjon 28)

  import rendre
  rendre.scener(delar, mappe, 'lampe')                  skriv <mappe>/scener.json og nett for trykte og kjøpte delar (render/nett/)
  rendre.koyr(mappe, ['lampe-samla'], prove=True)       rendre til <mappe>/render/lampe-samla-prove.png
  python rendre.py <mappe> [scene ...] [--prove]        same frå kommandolina

Trykte delar får materialet «print» (matt raudbrun), delane frå settet held materiala sine. Blender går på CPU med
fire trådar og lågaste prioritet. Full storleik (1600 x 1000) tek nokre minutt: køyr han i bakgrunnen.
"""
import os, sys, json, subprocess
sys.dont_write_bytecode = True
HER = os.path.dirname(os.path.abspath(__file__))
if HER not in sys.path: sys.path.insert(0, HER)
import miljo
import numpy as np
import trimesh
import kit as K

BLENDER = os.environ.get('KITBASH_BLENDER', r'C:/Users/Iver/Documents/verktoy/blender-5.1.2-windows-x64/blender.exe')
SKRIPT = os.path.join(HER, 'rendre_blender.py')
SAMLA = dict(azimut=-38, elevasjon=22, lens=50, faktor=0.82)        # som scena projektoren-samla i modell/byggjesett/delar.py
BANK = dict(azimut=-35, elevasjon=28, lens=50, faktor=1.0)          # som delbanken same stad
MATERIALE = ('aluminium', 'stål_svart', 'stål', 'plast_grå', 'plast_svart', 'kopar', 'kretskort', 'gummi_svart', 'keramikk',
             'fresnel', 'glas', 'film', 'print', 'led', 'opal')
_STL = {}


def _settfil(pid, under):
    """STL-fila til ein underdel i byggjesettet, om ho finst."""
    fil = os.path.join(K.SETT, 'stl', '%s_%s_%s.stl' % (pid, K.DIMS[pid]['namn'], under))
    return fil if os.path.exists(fil) else None


def _lik(fil, mesh):
    """Er STL-fila i settet den same forma som meshen vi har sjekka?"""
    if fil not in _STL:
        m = trimesh.load(fil); _STL[fil] = (len(m.faces), m.bounds.copy())
    n, b = _STL[fil]
    return n == len(mesh.faces) and np.allclose(b, mesh.bounds, atol=0.02)


def _objekt(delar, mappe):
    """Scenelista: éin post per underdel. Delar frå settet peikar på STL-filene i modell/byggjesett/stl/ (ikkje kopierte);
    trykte og kjøpte delar og filmstykke blir skrivne til <mappe>/render/nett/ slik dei er teikna (ikkje til <mappe>/stl/,
    der sjekk.eksporter legg dei trykte delane slik dei ligg på plata)."""
    os.makedirs(os.path.join(mappe, 'render', 'nett'), exist_ok=True)
    ut = []
    for d in delar:
        for u, m, mat in d.under:
            if mat not in MATERIALE:
                raise ValueError('%s/%s: materialet «%s» finst ikkje i rendraren (%s)' % (d.namn, u, mat, ', '.join(MATERIALE)))
            fil = _settfil(d.pid, u) if d.slag == 'sett' else None
            if fil is None or not _lik(fil, m):
                fil = os.path.join(mappe, 'render', 'nett', '%s_%s.stl' % (d.namn, u) if u != d.namn else '%s.stl' % d.namn)
                m.export(fil)
            o = dict(fil=os.path.relpath(fil, mappe).replace('\\', '/'), mat=mat, M=d.M.tolist(),
                     del_=(d.pid or 'ny'), under=u, namn=d.namn, slag=d.slag)
            if d.pid == 'P08' and d.flat_film: o['flat'] = True
            ut.append(o)
    return ut


def _tilpass(delar, kam, storleik, marg=0.06):
    """Kameraet til byggjesettet står i ein avstand som er sett for hand per scene (faktor). Her blir siktepunktet og
    faktoren rekna ut slik at heile lampa akkurat får plass i biletet med `marg` luft, i same retning og med same linse."""
    V = np.vstack([m.vertices for _, _, m, _ in K.alle_under(delar)])
    lo, hi = V.min(0), V.max(0); R = float(np.linalg.norm(hi - lo)) / 2
    az, el = np.radians(kam['azimut']), np.radians(kam['elevasjon'])
    retn = np.array([np.sin(az) * np.cos(el), -np.cos(az) * np.cos(el), np.sin(el)])        # frå siktepunktet mot kameraet
    hogre = np.cross([0, 0, 1.0], retn); hogre /= np.linalg.norm(hogre); opp = np.cross(retn, hogre)
    W, H = storleik
    th, tv = (1 - marg) * 18.0 / kam['lens'], (1 - marg) * 18.0 * H / W / kam['lens']
    mal = (lo + hi) / 2
    for _ in range(4):
        q = V - mal; a = q @ retn; x = q @ hogre; y = q @ opp
        Dist = float(np.max(a + np.maximum(np.abs(x) / th, np.abs(y) / tv)))
        z = Dist - a
        mal = mal + hogre * (np.max(x / z) + np.min(x / z)) / 2 * Dist + opp * (np.max(y / z) + np.min(y / z)) / 2 * Dist
    halv_v = np.arctan(18.0 * H / W / kam['lens'])
    return mal, Dist * np.sin(halv_v) / max(R, 1e-9)


def _scene(delar, mappe, kamera, prover, storleik, delbank=None):
    lo, hi = K.grenser(delar)
    kam = dict(kamera); mal = (lo + hi) / 2
    if not delbank:
        mal, kam['faktor'] = _tilpass(delar, kam, storleik)
        kam['faktor'] = round(float(kam['faktor']), 4)
    sc = dict(objekt=_objekt(delar, mappe), lo=lo.tolist(), hi=hi.tolist(), prover=prover, storleik=list(storleik), baklys=False,
              kamera=dict(mal=np.asarray(mal).tolist(), **kam))
    if delbank: sc['delbank'] = dict(px_per_mm=delbank)
    return sc


def scener(delar, mappe, namn='lampe', azimut=None, elevasjon=None, storleik=(1600, 1000), prover=48,
           sprengfaktor=0.6, px_per_mm=4, sprengt=None):
    """Skriv (eller utvid) <mappe>/scener.json med <namn>-samla, <namn>-sprengt og <namn>-del.
    azimut / elevasjon: eit anna kamera enn standarden (-38 / 22), til dømes azimut=38 for å sjå lampa frå høgre.
    sprengt: ei ferdig liste med delar til det sprengde biletet. Elles kit.sprengd(delar, sprengfaktor).
    Gjev namna på scenene."""
    os.makedirs(mappe, exist_ok=True)
    kam = dict(SAMLA)
    if azimut is not None: kam['azimut'] = azimut
    if elevasjon is not None: kam['elevasjon'] = elevasjon
    fil = os.path.join(mappe, 'scener.json')
    data = json.load(open(fil, encoding='utf-8')) if os.path.exists(fil) else {}
    data[namn + '-samla'] = _scene(delar, mappe, kam, prover, storleik)
    data[namn + '-sprengt'] = _scene(sprengt or K.sprengd(delar, sprengfaktor), mappe, kam, prover, storleik)
    data[namn + '-del'] = _scene(delar, mappe, BANK, 32, storleik, delbank=px_per_mm)
    json.dump(data, open(fil, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    return [namn + '-samla', namn + '-sprengt', namn + '-del']


def koyr(mappe, scener_=None, prove=False, vent=True, logg=None):
    """Rendre scenene i <mappe>/scener.json til <mappe>/render/. scener_: namn, eller None for alle.
    prove=True gjev bilete i ein tredel av storleiken med 24 prøver (namn-prove.png).
    vent=False startar Blender i bakgrunnen og gjev prosessen attende (til full storleik).
    Gjev lista med biletfiler (vent=True)."""
    fil = os.path.abspath(os.path.join(mappe, 'scener.json'))
    ut = os.path.abspath(os.path.join(mappe, 'render'))
    alle = list(json.load(open(fil, encoding='utf-8')))
    val = list(scener_) if scener_ else alle
    for s in val:
        if s not in alle: raise KeyError('scena «%s» finst ikkje i %s (%s)' % (s, fil, ', '.join(alle)))
    cmd = [BLENDER, '-b', '-P', SKRIPT, '--', '--scener', fil, '--ut', ut] + val + (['--prove'] if prove else [])
    bilete = [os.path.join(ut, s + ('-prove' if prove else '') + '.png') for s in val]
    loggfil = logg or os.path.join(ut, 'blender.log')
    os.makedirs(ut, exist_ok=True)
    if not vent:
        return subprocess.Popen(cmd, stdout=open(loggfil, 'w', encoding='utf-8', errors='replace'), stderr=subprocess.STDOUT)
    r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    open(loggfil, 'w', encoding='utf-8').write(r.stdout + '\n' + r.stderr)
    for linje in r.stdout.splitlines():
        if linje.startswith('RENDRA'): print(' ', linje, flush=True)
    manglar = [b for b in bilete if not os.path.exists(b)]
    if r.returncode != 0 or manglar:
        raise RuntimeError('Blender feila (kode %s). Sjå %s. Manglar: %s' % (r.returncode, loggfil, manglar))
    return bilete


if __name__ == '__main__':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass
    a = sys.argv[1:]
    if not a or a[0].startswith('--'):
        print(__doc__); sys.exit(0)
    mappe = a[0]; val = [x for x in a[1:] if not x.startswith('--')]
    for b in koyr(mappe, val or None, prove='--prove' in a):
        print(b)
