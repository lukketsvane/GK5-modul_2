import csv, motor as M
B = dict(M.FINAL)
t, S = M.tal(B)
for k, v in t.items(): print(f'{k:20s} {v}')
with open('tal.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, list(t.keys())); w.writeheader(); w.writerow({k: (round(float(v), 4) if isinstance(v, float) else v) for k, v in t.items()})
M.render_kropp(B, 'kropp.png')
