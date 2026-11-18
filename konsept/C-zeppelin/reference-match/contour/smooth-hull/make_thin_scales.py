from pathlib import Path
p=Path(__file__).resolve().parent
q=p/"thin-scales"
s=(p/"build_smooth.py").read_text(encoding="utf-8")
a="down=[36,32,26,20,8][kind]"
b="down=[14,12,10,7,3][kind]"
assert a in s
s=s.replace(a,b)
(q/"build.py").write_text(s,encoding="utf-8")
(q/"astra_scoop.py").write_text((p/"astra_scoop.py").read_text(encoding="utf-8"),encoding="utf-8")
r=(p/"render_smooth.py").read_text(encoding="utf-8")
repls={
'make_material("Satin silver aluminum", (0.26, 0.28, 0.30), 0.82, 0.28)':'make_material("Satin silver aluminum", (0.18, 0.19, 0.20), 0.84, 0.32)',
"0.90, 0.35, 6.0":"0.90, 0.35, 4.7",
"0.52, 0.25, 10.0":"0.52, 0.25, 11.0"
}
for a,b in repls.items():
 assert a in r,a
 r=r.replace(a,b)
a='    output_dir = root / "renders"'
b='''    make_softbox(studio, "Warm inner rim", (0.02, -0.17, 0.045),
                 0.50, 0.085, 9.0, (1.0, 0.70, 0.44))
    output_dir = root / "renders"'''
assert a in r
r=r.replace(a,b)
(q/"render.py").write_text(r,encoding="utf-8")
(q/"compare_silhouette.py").write_text((p/"compare_silhouette.py").read_text(encoding="utf-8"),encoding="utf-8")
print("improved scoop upper domes and lower warm diffuser")
