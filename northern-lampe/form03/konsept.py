"""Tre konsept på likt nivå: (a) bru · (b) krok · (c) flak. Same kamera, skala og tal(). -> ../konsept.png, ../konsept.json"""
import os, sys, json, importlib.util
import numpy as np
from PIL import Image, ImageDraw, ImageFont
HER = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HER)
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, 'form01')); sys.path.insert(0, os.path.join(ROOT, 'form02'))
import felles as fe
import val as V2                                   # form02: bru + krok (brukar form01/motor som M1)
spec = importlib.util.spec_from_file_location('motor3', os.path.join(HER, 'motor.py'))
M3 = importlib.util.module_from_spec(spec); spec.loader.exec_module(M3)

Ba, ta, Sa = V2.tal_bru(15.0)
Bb = dict(V2.B_KROK); tb, Sb = V2.tal_krok(Bb)
Bc = dict(M3.FINAL); tc, Sc = M3.tal(Bc)
rows = {'a': (ta, Sa, lambda s: V2.M1.geometri(Ba, s)), 'b': (tb, Sb, lambda s: V2.geometri_krok(Bb, s)), 'c': (tc, Sc, lambda s: M3.geometri(Bc, s))}
nn_ = lambda v, d=0: f'{v:,.{d}f}'.replace(',', ' ').replace('.', ',')
keys = ['Phi_lm', 'P_W', 'U0', 'Ev_stem', 'R_stem', 'masse_kg', 'fot_cm2', 'svikt_mm', 'L_ansikt', 'A_kjol_cm2', 'A_krav_cm2']
out = {k: {q: float(rows[k][0][q]) for q in keys} for k in 'abc'}
out['a'].update(tipp=float(ta['tipp_deg']), vri=float(ta['sving']), synleg=False)
out['b'].update(tipp=None, vri=float(tb['sving']), synleg=False)
out['c'].update(tipp=float(tc['tipp_aleine']), vri=float(tc['sving']), synleg=True, L_synleg=float(tc['L_arb_topp']), Phi_ansikt=float(tc['Phi_ansikt']))
json.dump(out, open(os.path.join(ROOT, 'konsept.json'), 'w'), indent=1)
ims = []
for k in 'abc':
    t, S, geo = rows[k]
    V, F, emit = geo(S['work']['s'])[:3]
    V = V.copy(); V[:, 1] -= 0.45
    im, _ = fe.render(V, F, fe.Cam(S=2048, el=17, az=240, fov=19, D=4.6, target=(0, 0, 0.32)), emit=emit)
    im.save(os.path.join(ROOT, f'konsept_{k}.png')); ims.append(im)
W_, H_ = 3 * 1024 + 4 * 60, 1024 + 120 + 470
sh = Image.new('RGB', (W_, H_), 'black'); dr = ImageDraw.Draw(sh)
FONT = r'C:\Windows\Fonts\georgiai.ttf'
fh, fb = ImageFont.truetype(FONT, 44), ImageFont.truetype(FONT, 28)
head = {'a': '(a) bru', 'b': '(b) krok', 'c': '(c) flak'}
sub = {'a': 'lysrøyr på to bukkar · vri i endegrepet', 'b': 'lysrøyr på arm frå bakkanten · vri', 'c': 'lysande brett over skjermen · vipp'}
for j, k in enumerate('abc'):
    x = 60 + j * (1024 + 60); o = out[k]
    sh.paste(ims[j], (x, 60))
    dr.text((x, 60 + 1024 + 30), head[k], font=fh, fill=(240, 236, 228))
    dr.line([x, 60 + 1024 + 92, x + 250, 60 + 1024 + 90], fill=(240, 236, 228), width=2)
    tipp = 'klemt' if o['tipp'] is None else f"tipp {nn_(o['tipp'])}°"
    lines = [sub[k],
             f"{nn_(o['Phi_lm'])} lm · {nn_(o['P_W'], 1)} W · U0 {nn_(o['U0'], 2)}",
             f"stemning {nn_(o['Ev_stem'])} lx på veggen · {o['R_stem'] * 100:.0f} %",
             f"ansiktslys krev {nn_(o['L_ansikt'] / 1000, 1)} kcd/m²" + (' (mjukt)' if o['L_ansikt'] <= 3000 else ' (for hardt)'),
             f"{nn_(o['masse_kg'], 2)} kg · {nn_(o['fot_cm2'])} cm² · {tipp} · svikt {nn_(o['svikt_mm'], 1)} mm"]
    for i, s in enumerate(lines):
        dr.text((x, 60 + 1024 + 125 + i * 44), s, font=fb, fill=(170, 163, 152) if i in (0, 4) else (240, 236, 228))
sh.save(os.path.join(ROOT, 'konsept.png'))
print(json.dumps(out, indent=1))
