"""Run one side-engine case: python run_side.py name '{json geo overrides}' nrays"""
import sys, json, time, math
import numpy as np
import fyrlys as F

name = sys.argv[1]
cfg = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
nr = int(sys.argv[3]) if len(sys.argv) > 3 else 200000
t0 = time.time()
g = F.default_geo(**cfg)
tal = F.Tally(g)
E, ab = F.trace(g, nrays=nr, batch=50000, tally=tal, seed=11)
maps = tal.maps()
phi = g["flux"]
P, D, W, NB, LAST = E[:, 0:3], E[:, 3:6], E[:, 6], E[:, 7], E[:, 8]
el = np.degrees(np.arcsin(np.clip(D[:, 2], -1, 1)))
res = dict(name=name, cfg=cfg, nrays=nr, nlam=len(g["z_lam"]) + 1, roof_tip=round(g["z_roof_tip"], 1))
res["flux_src"] = phi
res["esc_total"] = W.sum()
res["esc_down"] = W[el < 0].sum()
res["esc_up"] = W[el >= 0].sum()
res["esc_up_gt5"] = W[el > 5].sum()
res["esc_direct"] = W[NB == 0].sum()
res["esc_direct_max_el"] = float(el[NB == 0].max()) if (NB == 0).any() else None
res["esc_up_by_last"] = {F.NAMES[int(s)]: round(float(W[(el >= 0) & (LAST == s)].sum()), 3) for s in np.unique(LAST[el >= 0])} if (el >= 0).any() else {}
res["esc_up_by_nb"] = {int(b): round(float(W[(el >= 0) & (NB == b)].sum()), 3) for b in np.unique(NB[el >= 0])[:6]} if (el >= 0).any() else {}
res["absorbed"] = {k: round(float(v), 2) for k, v in ab.items() if v > 0.05}
# elevation distribution of escaped flux (lm per 5 deg)
h, be = np.histogram(el, np.arange(-90, 91, 5), weights=W)
res["el_hist"] = {f"{int(be[i])}": round(float(h[i]), 2) for i in range(len(h)) if h[i] > 0.05}
# ---- table (z=0): use y-mirror symmetry
dn = D[:, 2] < -1e-6
t = -P[dn, 2] / D[dn, 2]
X = P[dn, 0] + t * D[dn, 0]; Y = P[dn, 1] + t * D[dn, 1]; Wd = W[dn]; NBd = NB[dn]
X = np.concatenate([X, X]); Y = np.concatenate([Y, -Y]); Wd = np.concatenate([Wd, Wd]) / 2; NBd = np.concatenate([NBd, NBd])
R = np.hypot(X, Y); A = np.degrees(np.arctan2(Y, X))
rb = np.arange(50, 1001, 10.0); ab_ = np.arange(-90, 90.01, 0.75)
Hh, _, _ = np.histogram2d(R, A, [rb, ab_], weights=Wd)
area = 0.5 * (rb[1:] ** 2 - rb[:-1] ** 2)[:, None] * (np.diff(ab_) * F.DEG)[None, :] * 1e-6  # m2
lux = Hh / area
Hd, _, _ = np.histogram2d(R[NBd == 0], A[NBd == 0], [rb, ab_], weights=Wd[NBd == 0])
luxd = Hd / area
np.savez_compressed(f"table_{name}.npz", lux=lux, luxd=luxd, rb=rb, ab=ab_)
rc = 0.5 * (rb[1:] + rb[:-1]); ac = 0.5 * (ab_[1:] + ab_[:-1])
sect = np.abs(ac) <= 30
for rr in (100, 150, 200, 300, 400, 500, 700):
    i = np.argmin(np.abs(rc - rr))
    row = lux[max(i - 1, 0):i + 2].mean(0)
    rowd = luxd[max(i - 1, 0):i + 2].mean(0)
    s = row[sect]
    sm = np.convolve(s, np.ones(3) / 3, mode="same")[1:-1]
    sd = np.convolve(rowd[sect], np.ones(3) / 3, mode="same")[1:-1]
    mod = (sm.max() - sm.min()) / max(sm.max() + sm.min(), 1e-9)
    res[f"arc_{rr}"] = dict(mean=round(float(s.mean()), 1), peak=round(float(sm.max()), 1), min=round(float(sm.min()), 1), mod=round(float(mod), 2),
                           direct_mean=round(float(rowd[sect].mean()), 1), mod_direct=round(float((sd.max() - sd.min()) / max(sd.max() + sd.min(), 1e-9)), 2))
# flux to table rings and field 0.6 x 0.4 in front (x 0.1..0.5, y -0.3..0.3) -> from raw points
f = (X >= 100) & (X <= 500) & (np.abs(Y) <= 300)
res["field_lm"] = round(float(Wd[f].sum()), 2)
res["field_mean_lux"] = round(float(Wd[f].sum() / 0.24), 1)
gx = np.arange(100, 501, 50.0); gy = np.arange(-300, 301, 50.0)
Hf, _, _ = np.histogram2d(X[f], Y[f], [gx, gy], weights=Wd[f])
Hf = Hf / (0.05 * 0.05)
res["field_min_lux_50mm"] = round(float(Hf.min()), 1); res["field_max_lux_50mm"] = round(float(Hf.max()), 1)
res["table_lm_r_lt_1m"] = round(float(Wd[R < 1000].sum()), 2)
# ---- luminance maps
Lt = maps["top"]; Lb = maps["bot"]
res["L_lamtop_max"] = round(float(np.nanmax(Lt)), 0)
rcen = 0.5 * (tal.rb[1:] + tal.rb[:-1])
acen = 0.5 * (tal.ab[1:] + tal.ab[:-1])
fr = np.abs(acen) <= 30
res["L_lamtop_by_r"] = {f"{rcen[i]:.1f}": round(float(Lt[i, fr].mean()), 0) for i in range(len(rcen)) if rcen[i] >= g["r_in"] and i % 2 == 0}
res["L_lambot_by_r"] = {f"{rcen[i]:.1f}": round(float(Lb[i, fr].mean()), 0) for i in range(len(rcen)) if rcen[i] >= g["r_in"] and i % 4 == 0}
res["L_rooftop_max"] = round(float(np.nanmax(maps["rtop"][:, fr])), 0)
res["L_edge_out_avg"] = round(float(maps["edge_out"]), 0)
res["L_sleeve_in_max"] = round(float(maps["sl"].max()), 0)
res["L_mantel_in_max"] = round(float(maps["mt"].max()), 0)
res["L_rib_max"] = round(float(maps["rib"].max()), 0)
L_strip = phi / (g["strip_w"] * (g["strip_z1"] - g["strip_z0"]) * 1e-6) / math.pi
res["L_strip"] = round(L_strip, 0)
eyes = {}
for H in (250, 350, 470, 600):
    for Dd in (400, 700):
        Pp, L, surf = F.eye_view(g, maps, tal, (Dd, 0, H), n=24000, L_strip=L_strip)
        vis = np.isin(surf, (F.LAMT, F.ROOFT, F.LAMB, F.RIB, F.SIDE, F.LAMEO, F.SLIN, F.MANT, F.STRIP, F.BOXS, F.FLOOR, F.CEIL, F.LAMEI, F.ROOFB))
        strip_frac = float((surf == F.STRIP).mean())
        Lv = L[vis] if vis.any() else np.array([0.0])
        eyes[f"H{H}_D{Dd}"] = dict(p999=round(float(np.percentile(L, 99.9)), 0), mean=round(float(L.mean()), 0), p95=round(float(np.percentile(L, 95)), 0), p99=round(float(np.percentile(L, 99)), 0),
                                   max=round(float(L.max()), 0), frac_gt1500=round(float((L > 1500).mean()), 3), frac_gt3000=round(float((L > 3000).mean()), 3),
                                   strip_seen=strip_frac,
                                   surf={F.NAMES[int(s)]: round(float((surf == s).mean()), 2) for s in np.unique(surf)})
res["eyes"] = eyes
res["time_s"] = round(time.time() - t0, 1)
np.savez_compressed(f"maps_{name}.npz", top=Lt, bot=Lb, rb=tal.rb, ab=tal.ab, sl=maps["sl"], mt=maps["mt"])
json.dump(res, open(f"res_{name}.json", "w"), indent=1, default=float)
print(json.dumps(res, default=float))
