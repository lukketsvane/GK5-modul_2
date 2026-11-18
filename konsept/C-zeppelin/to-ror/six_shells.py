from pathlib import Path
p=Path(__file__).resolve().parent
f=p/"build.py"
s=f.read_text(encoding="utf-8")
changes=[
    ("PITCH=40.0\nSTATIONS=list(range(-4,5))","PITCH=60.0\nSTATIONS=list(range(6))\nSHELL_KINDS=(4,2,0,0,2,4)"),
    ("for k in range(5):\n    for lane in range(4):","for k in sorted(set(SHELL_KINDS)):\n    for lane in range(4):"),
    ("    for i in STATIONS:\n        lane=(i+4)%4\n        x=i*PITCH\n        add(f\"leaf_{which}_{abs(i)}_{lane}\",f\"petal_{which}_{i}\",which,x,yy,AXIS_Z)\n        add(f\"mount_{which}_{lane}\",f\"pipe_clamp_{which}_{i}\",which,x,yy,AXIS_Z,color=\"metal\")",
     "    for i in STATIONS:\n        lane=i%4\n        x=(i-2.5)*PITCH\n        kind=SHELL_KINDS[i]\n        add(f\"leaf_{which}_{kind}_{lane}\",f\"shell_{i+1}_{which}\",which,x,yy,AXIS_Z)\n        add(f\"mount_{which}_{lane}\",f\"pipe_clamp_{which}_{i+1}\",which,x,yy,AXIS_Z,color=\"metal\")"),
    ("\"pivots\":2,\"moving_tubes\":2,\"petals\":18,","\"pivots\":2,\"moving_tubes\":2,\"shells\":6,\"half_shells\":12,")
]
for a,z in changes:
    assert s.count(a)==1,repr(a)
    s=s.replace(a,z)
f.write_text(s,encoding="utf-8")
v=p/"verify.py"
t=v.read_text(encoding="utf-8")
marker='root=Path(__file__).resolve().parent'
assert t.count(marker)==1
t=t.replace(marker,marker+'''
scene=json.loads((root/"scene.json").read_text(encoding="utf-8"))
shells=[p for p in scene["parts"] if p["name"].startswith("shell_")]
assert len(shells)==12, len(shells)
assert len({p["name"].split("_")[1] for p in shells})==6
for shell_id in map(str,range(1,7)):
    assert {p["name"].split("_")[2] for p in shells if p["name"].split("_")[1]==shell_id}=={"upper","lower"}
print("SHELL_COUNT_CONFIRMED=6",flush=True)
''')
v.write_text(t,encoding="utf-8")
print("SIX_SHELL_STATIONS_APPLIED",flush=True)
