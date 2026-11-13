"""Gen 01 på svart (husstil oppdatert 2026-11-13) + kryssjekk av felles.py mot motor.py."""
import os, sys, math
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import felles as fe
import motor as mo
ims, masks = {}, {}
for B in mo.BODIES + mo.CONTROLS:
    t, geo = mo.tal(B)
    # kryssjekk lys: felles.sok med gen01-opninga
    op = lambda B, ph: (lambda P, n, dA: (P, np.tile(n, (len(P), 1)), dA))(*mo.aperture(B, ph))
    eta, _ = mo.cavity_eta(B)
    S = fe.sok(B, list(np.radians(np.arange(-180, 180, 5))), op, eta)
    print(f"{B['id']:2d} Phi motor={t['Phi_lm']:7.0f} felles={S['work']['Phi']:7.0f}  R_stem={S['mood']['R_stem']:.2f} Ev={S['mood']['Ev_stem']:.0f} stem_ok={S['mood']['stem_ok']}")
    V = geo['V'].copy(); V[:, :2] -= np.vstack(geo['contacts']).mean(0)
    ims[B['id']], masks[B['id']] = fe.render(V, geo['F'])
grid = {(B['rad'], B['kol']): B['id'] for B in mo.BODIES}
fe.brett(ims, grid, 'brett.png')
fe.stripe([ims[17], ims[18]], 'kontroll.png')
print(fe.formkritikk({k: masks[k] for k in grid.values()}, grid)['iou_snitt'])
