# -*- coding: utf-8 -*-
"""
slice_lut.py  ·  slicar printplatene til Lut for Bambu Lab P1S (0,4 mm dyse) med Bambu Studio-CLI og systemprofilane

  py -3 print/slice_lut.py
Les produksjon/*.stl (monteringsposisjon), snur delane til printretning, plasserer dei på plata og slicar.
Skriv print/LUT_P1S_plate*.gcode.3mf og print/slicing.json (tid, gram og åtvaringar frå sliceren).
Profilane blir flata ut frå %APPDATA%/BambuStudio/system/BBL (heile inherits-kjeda), som i konsept C.
"""
import json
import os
import shutil
import struct
import subprocess
import tempfile
from pathlib import Path

import numpy as np

HER = Path(__file__).resolve().parent
ROT = HER.parent
EXE = Path(r'C:\Program Files\Bambu Studio\bambu-studio.exe')
SYS = Path(os.environ.get('APPDATA', '')) / 'BambuStudio' / 'system' / 'BBL'
MASKIN = 'Bambu Lab P1S 0.4 nozzle'
PLA = 'Bambu PLA Matte @BBL P1S 0.4 nozzle'
PETG = 'Bambu PETG HF @BBL P1S 0.4 nozzle'

FELLES = {'curr_bed_type': 'Textured PEI Plate', 'enable_support': '0', 'sparse_infill_pattern': 'gyroid',
          'wall_generator': 'arachne', 'seam_position': 'aligned', 'top_shell_layers': '5', 'bottom_shell_layers': '4'}
PLATER = [
    # namn, prosess, filament, ekstra prosessval, objekt: (stl, rotasjon om X i grader, x, y på plata)
    ('LUT_P1S_plate0_passprove_PLA', '0.20mm Standard @BBL X1C', PLA,
     {'wall_loops': '3', 'sparse_infill_density': '15%', 'brim_type': 'no_brim'},
     [('P00_passprove', 0.0, None, None)]),
    ('LUT_P1S_plate1_blad_PLA', '0.20mm Standard @BBL X1C', PLA,
     {'wall_loops': '3', 'sparse_infill_density': '15%', 'ironing_type': 'top', 'brim_type': 'no_brim'},
     [('D01_blad', 90.0, None, None)]),
    ('LUT_P1S_plate2_fot_hovud_knott_PLA', '0.16mm Optimal @BBL X1C', PLA,
     {'wall_loops': '6', 'sparse_infill_density': '15%', 'brim_type': 'no_brim'},
     [('D03_fot', 180.0, 30.5, 18.0), ('D02_hovud', 180.0, 40.0, 116.0), ('D05_knott', 180.0, 150.0, 146.0)]),
    ('LUT_P1S_plate3_lyskopp_PETG_kvit', '0.16mm Optimal @BBL X1C', PETG,
     {'wall_loops': '4', 'sparse_infill_density': '15%', 'brim_type': 'no_brim'},
     [('D06_lyskopp', 180.0, None, None)]),
    ('LUT_P1S_plate4_botnplate_PLA_alternativ', '0.20mm Standard @BBL X1C', PLA,
     {'wall_loops': '3', 'sparse_infill_density': '100%', 'sparse_infill_pattern': 'zig-zag', 'brim_type': 'no_brim'},
     [('D04_botnplate', 0.0, None, None)]),
]


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


def les_stl(sti):
    b = sti.read_bytes()
    n = struct.unpack('<I', b[80:84])[0]
    return np.frombuffer(b[84:84 + n * 50], dtype=np.dtype([('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')])).copy()


def skriv_stl(sti, tri):
    with open(sti, 'wb') as f:
        f.write(b'Lut konsept D'.ljust(80, b' '))
        f.write(struct.pack('<I', len(tri)))
        tri.tofile(f)


def snu(tri, grad):
    a = np.radians(grad)
    v = tri['v'].astype(np.float64)
    y, z = v[..., 1].copy(), v[..., 2].copy()
    v[..., 1] = y * np.cos(a) - z * np.sin(a)
    v[..., 2] = y * np.sin(a) + z * np.cos(a)
    v -= v.reshape(-1, 3).min(axis=0)
    tri['v'] = v.astype(np.float32)
    return tri


def main():
    import sys
    val = sys.argv[1:]
    sti = HER / 'slicing.json'
    ut = json.loads(sti.read_text(encoding='utf-8')) if (val and sti.exists()) else {}
    for namn, prosess, filament, ekstra, objekt in PLATER:
        if val and not any(v in namn for v in val):
            continue
        tmp = Path(tempfile.mkdtemp(prefix='lut_slice_'))
        try:
            filer = []
            for stl, grad, x, y in objekt:
                tri = snu(les_stl(ROT / 'produksjon' / f'{stl}.stl'), grad)
                lo, hi = tri['v'].reshape(-1, 3).min(axis=0), tri['v'].reshape(-1, 3).max(axis=0)
                if x is None:
                    x, y = 128 - (hi[0] - lo[0]) / 2, 128 - (hi[1] - lo[1]) / 2
                tri['v'] += np.array([x, y, 0], dtype=np.float32)
                hi2 = tri['v'].reshape(-1, 3).max(axis=0)
                assert hi2[0] <= 256 and hi2[1] <= 256 and hi2[2] <= 256, (stl, hi2)
                f = tmp / f'{stl}.stl'
                skriv_stl(f, tri)
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
                ut[namn] = dict(ok=False, kode=r.returncode, info=info, stderr=r.stderr[-600:])
                print(namn, 'FEILA', r.returncode, info, flush=True)
                continue
            shutil.copy2(tmp / ut3, HER / ut3)
            pl = (info.get('sliced_plates') or [{}])[0]
            fil = (pl.get('filaments') or [{}])[0]
            ut[namn] = dict(ok=True, prosess=prosess, filament=filament, val=ekstra,
                            tid_min=round(float(pl.get('total_predication', 0)) / 60, 1),
                            gram=round(float(fil.get('total_used_g', 0)), 1),
                            atvaring=pl.get('warning_message', ''))
            print(namn, ut[namn], flush=True)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    (HER / 'slicing.json').write_text(json.dumps(ut, ensure_ascii=False, indent=1), encoding='utf-8')


if __name__ == '__main__':
    main()
