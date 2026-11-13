import json, csv, math
import motor as M
B, t, S = M.final_tal()
for k, v in t.items(): print(f'{k:14s} {v}')
with open('tal.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, list(t.keys())); w.writeheader(); w.writerow({k: (round(v, 4) if isinstance(v, float) else v) for k, v in t.items()})
M.render_kropp(B, 'kropp.png')
