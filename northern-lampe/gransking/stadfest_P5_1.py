"""Motbevis P5: innsyn til LED-stripa forbi renne og plate, samla, vinkel stripa dekkjer. Analytisk, sekund."""
import math, numpy as np
YS, ZS, D, TP, BP, CW, ZC = 0.22, 0.70, 0.05, 0.003, 0.16, 0.008, 0.005   # form04 FINAL, renne i geometri()
EYE = np.array([-0.30, 0.45])                                            # felles.EYES[0] (y, z), alfa_arb 0


def synleg(w, eye=EYE, cw=CW, zc=ZC, n=20001):
    """Del av stripa (mm) som auget ser: line frå stripepunkt til auge under rennekanten og framfor platekanten."""
    u = np.linspace(-w / 2, w / 2, n) if w > 0 else np.array([0.0])
    # lokalt: s mot brukaren (= -y), z ned frå lina
    se, ze = -(eye[0] - YS), ZS - eye[1]
    k = (se - u) / ze
    ok = (np.abs(u + k * zc) < cw) & (np.abs(u + k * D) > BP / 2) & (np.abs(u + k * (D + TP + 0.002)) > BP / 2)
    return ok.mean() * w * 1000, math.degrees(math.atan2(se, ze))


def samla(w, n=4001):
    u = np.linspace(-w / 2, w / 2, n) if w > 0 else np.array([0.0])
    tr = (np.sin(np.arctan((CW - u) / ZC)) + np.sin(np.arctan((CW + u) / ZC))) / 2          # berre renna (kode 6)
    pp = (np.sin(np.minimum(np.arctan((CW - u) / ZC), np.arctan((BP / 2 - u) / D)))
          + np.sin(np.minimum(np.arctan((CW + u) / ZC), np.arctan((BP / 2 + u) / D)))) / 2  # renne og plate
    return tr.mean(), pp.mean()


print('samla (renne, renne+plate):')
for w in (0, 0.005, 0.010):
    a, b = samla(w); print(f'  w {w*1000:.0f} mm: {a:.3f}  {b:.3f}  forbi plata {a-b:.3f}')
print('vinkel stripa dekkjer frå rille (luft):')
for w in (0.005, 0.010):
    mid = 2 * math.degrees(math.atan(w / 2 / D)); r = math.hypot(BP / 2, D); ph = math.atan(BP / 2 / D)
    print(f'  w {w*1000:.0f}: midt {mid:.1f}  ytst {math.degrees(w*math.cos(ph)/r):.1f}')
print('innsyn, modellauge:')
for w in (0, 0.005, 0.010):
    b, sv = synleg(w); print(f'  w {w*1000:.0f}: {b:.2f} mm  sikt {sv:.1f} deg')
print('L_LED 10 mm, 482 lm:', 482 / (math.pi * 0.010 * 0.60), ' 5 mm, 459 lm:', 459 / (math.pi * 0.005 * 0.60))
print('følsemd for augepunkt (y, z) -> synleg mm for 5 / 10 mm:')
for e in [(-0.30, 0.40), (-0.30, 0.42), (-0.30, 0.45), (-0.30, 0.48), (-0.30, 0.50), (-0.25, 0.45), (-0.35, 0.45)]:
    print(f'  {e}: {synleg(0.005, np.array(e))[0]:.2f}  {synleg(0.010, np.array(e))[0]:.2f}  sikt {synleg(0, np.array(e))[1]:.1f}')
print('veggtjukn 1,5 mm innover (opning ±6,5 mm):', synleg(0.005, cw=0.0065)[0], synleg(0.010, cw=0.0065)[0])
se, ze = YS - EYE[0], ZS - EYE[1]
for w in (0.005, 0.010, 0.016):
    print(f'naudsynt veggdjupn for w {w*1000:.0f} mm: {(CW + w/2) * ze / se * 1000:.2f} mm (modellauge),'
          f' {(CW + w/2) * (ZS-0.40) / se * 1000:.2f} mm (auge 5 cm lågare)')
# apparent storleik og grov UGR-del for 10 mm
ws = synleg(0.010)[0] / 1000; r = math.hypot(se, ze); c = ze / r
x = np.linspace(-0.30, 0.30, 601); rr = np.sqrt(x ** 2 + r ** 2)
Om = np.trapezoid(ws * c * r / rr ** 3 * r, x) if hasattr(np, 'trapezoid') else 0
print(f'romvinkel synleg stripe 10 mm: {Om*1e3:.2f} msr, I mot auga {25600*ws*c*0.6:.1f} cd (grovt)')
