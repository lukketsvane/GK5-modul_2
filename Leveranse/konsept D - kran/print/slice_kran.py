# -*- coding: utf-8 -*-
"""
slice_kran.py  ·  slicar printplatene til Kran for Bambu Lab P1S (0,4 mm dyse) med Bambu Studio-CLI og systemprofilane

  py -3 print/slice_kran.py [del av platenamnet ...]
Les platene som cad/kran.py har lagt ut (print/KRAN_P1S_plate*.3mf: delane i printretning, plassert på plata),
skriv kvar del som STL med plasseringa i koordinatane og slicar. Skriv print/KRAN_P1S_plate*.gcode.3mf og
print/slicing.json: tid, gram og åtvaringar frå sliceren, og overheng per del (flater som peikar meir enn 45 grader
nedover og ikkje ligg på plata), så det syner om nokon del treng støtte.
Profilane blir flata ut frå %APPDATA%/BambuStudio/system/BBL (heile inherits-kjeda), som i Lut og Raup.
"""
import json
import os
import re
import shutil
import struct
import subprocess
import tempfile
import zipfile
from pathlib import Path

import numpy as np

HER = Path(__file__).resolve().parent
EXE = Path(r'C:\Program Files\Bambu Studio\bambu-studio.exe')
SYS = Path(os.environ.get('APPDATA', '')) / 'BambuStudio' / 'system' / 'BBL'
MASKIN = 'Bambu Lab P1S 0.4 nozzle'
PETG = 'Bambu PETG HF @BBL P1S 0.4 nozzle'

FELLES = {'curr_bed_type': 'Textured PEI Plate', 'enable_support': '0', 'sparse_infill_pattern': 'gyroid',
          'wall_generator': 'arachne', 'seam_position': 'aligned', 'top_shell_layers': '5', 'bottom_shell_layers': '4'}
PLATER = [
    # 3MF frå kran.py, prosess, filament, ekstra prosessval
    # leddprøva: 0,16 mm lag gjev 1,48 mm for laga på 1,5 mm (0,20 + 8 x 0,16), 1,00 mm for øyret og låseskiva og
    # 2,92 mm for forsterkingsplata (3,0); heilt fylte, så platene er stive som i stål
    ('KRAN_P1S_plate0_leddprove_PETG', '0.16mm Optimal @BBL X1C', PETG,
     {'wall_loops': '3', 'sparse_infill_density': '100%', 'sparse_infill_pattern': 'zig-zag', 'brim_type': 'no_brim'}),
    ('KRAN_P1S_plate1_smaadelar_PETG', '0.16mm Optimal @BBL X1C', PETG,
     {'wall_loops': '4', 'sparse_infill_density': '20%', 'brim_type': 'no_brim'}),
]
OVERHENG_GRENSE = np.cos(np.radians(45.0))      # normal meir enn 45 grader under vassrett
LIM = 0.25                                       # flater lågare enn dette ligg på plata


def profil(kind, namn):
    kjede, cur = [], namn
    while cur:
        p = SYS / kind / f'{cur}.json'
        if not p.exists():
            treff = list((SYS / kind).rglob(f'{cur}.json'))
            if not treff:
                raise FileNotFoundError(f'{kind}/{cur}.json')
            p = treff[0]
        d = json.loads(p.read_text(encoding='utf-8'))
        kjede.append(d)
        cur = d.get('inherits')
    flat = {}
    for d in reversed(kjede):
        flat.update(d)
    flat.pop('inherits', None)
    return flat


def les_3mf(sti):
    """Objekta i ei 3MF-fil frå kran.py: liste av (namn, hjørne (N, 3), trekantar (M, 3)) med plasseringa lagd inn."""
    m = zipfile.ZipFile(sti).read('3D/3dmodel.model').decode('utf-8')
    obj = {}
    for oid, namn, kropp in re.findall(r'<object id="(\d+)" type="model" name="([^"]*)"><mesh>(.*?)</mesh></object>', m, re.S):
        v = np.array(re.findall(r'<vertex x="([-\d.e]+)" y="([-\d.e]+)" z="([-\d.e]+)"/>', kropp), dtype=np.float64)
        t = np.array(re.findall(r'<triangle v1="(\d+)" v2="(\d+)" v3="(\d+)"/>', kropp), dtype=np.int64)
        obj[oid] = (namn, v, t)
    ut = []
    for oid, tr in re.findall(r'<item objectid="(\d+)" transform="([^"]+)"/>', m):
        a = np.array(tr.split(), dtype=np.float64)
        rot, flytt = a[:9].reshape(3, 3), a[9:]
        namn, v, t = obj[oid]
        ut.append((namn, v @ rot + flytt, t))
    return ut


def skriv_stl(sti, v, t):
    p = v[t]
    n = np.cross(p[:, 1] - p[:, 0], p[:, 2] - p[:, 0])
    n /= np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-12)
    rad = np.zeros(len(t), dtype=np.dtype([('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')]))
    rad['n'], rad['v'] = n, p
    with open(sti, 'wb') as f:
        f.write(b'Kran konsept D'.ljust(80, b' '))
        f.write(struct.pack('<I', len(rad)))
        rad.tofile(f)


def overheng(v, t):
    """Areal (mm2) av flater som peikar meir enn 45 grader nedover og ikkje ligg på plata, og lågaste høgd for dei."""
    p = v[t]
    n = np.cross(p[:, 1] - p[:, 0], p[:, 2] - p[:, 0])
    a = np.linalg.norm(n, axis=1) / 2
    nz = n[:, 2] / np.maximum(2 * a, 1e-12)
    zmin = p[:, :, 2].min(axis=1)
    sel = (nz < -OVERHENG_GRENSE) & (zmin > LIM + v[:, 2].min())
    return dict(areal_mm2=round(float(a[sel].sum()), 1), lagaste_z_mm=round(float(zmin[sel].min()), 2) if sel.any() else None)


def main():
    import sys
    val = sys.argv[1:]
    sti = HER / 'slicing.json'
    ut = json.loads(sti.read_text(encoding='utf-8')) if (val and sti.exists()) else {}
    for namn, prosess, filament, ekstra in PLATER:
        if val and not any(v in namn for v in val):
            continue
        tmp = Path(tempfile.mkdtemp(prefix='kran_slice_'))
        try:
            filer, oh = [], {}
            for i, (onamn, v, t) in enumerate(les_3mf(HER / f'{namn}.3mf')):
                lo, hi = v.min(axis=0), v.max(axis=0)
                assert lo[0] >= 0 and lo[1] >= 0 and abs(lo[2]) < 1e-6 and hi[0] <= 256 and hi[1] <= 256 and hi[2] <= 256, (onamn, lo, hi)
                oh[onamn] = overheng(v, t)
                f = tmp / f'{i:02d}_{onamn.split()[0]}.stl'
                skriv_stl(f, v, t)
                filer.append(str(f))
            m, p, fi = profil('machine', MASKIN), profil('process', prosess), profil('filament', filament)
            p.update(FELLES)
            p.update(ekstra)
            for k, d in (('machine', m), ('process', p), ('filament', fi)):
                (tmp / f'{k}.json').write_text(json.dumps(d, indent=1), encoding='utf-8')
            ut3 = f'{namn}.gcode.3mf'
            cmd = [str(EXE), '--orient', '0', '--arrange', '0',
                   '--load-settings', f"{tmp / 'machine.json'};{tmp / 'process.json'}",
                   '--load-filaments', str(tmp / 'filament.json'),
                   '--slice', '0', '--outputdir', str(tmp), '--export-3mf', ut3, *filer]
            r = subprocess.run(cmd, capture_output=True, text=True, creationflags=0x00000040)   # IDLE_PRIORITY_CLASS
            info = json.loads((tmp / 'result.json').read_text(encoding='utf-8')) if (tmp / 'result.json').exists() else {}
            if r.returncode != 0 or not (tmp / ut3).exists():
                ut[namn] = dict(ok=False, kode=r.returncode, info=info, stderr=r.stderr[-600:], overheng=oh)
                print(namn, 'FEILA', r.returncode, info, flush=True)
                continue
            shutil.copy2(tmp / ut3, HER / ut3)
            pl = (info.get('sliced_plates') or [{}])[0]
            fil = (pl.get('filaments') or [{}])[0]
            ut[namn] = dict(ok=True, prosess=prosess, filament=filament, val=ekstra,
                            tid_min=round(float(pl.get('total_predication', 0)) / 60, 1),
                            gram=round(float(fil.get('total_used_g', 0)), 1),
                            atvaring=pl.get('warning_message', ''), overheng=oh)
            print(namn, json.dumps(ut[namn], ensure_ascii=False), flush=True)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    (HER / 'slicing.json').write_text(json.dumps(ut, ensure_ascii=False, indent=1), encoding='utf-8')


if __name__ == '__main__':
    main()
