from pathlib import Path
p=Path(__file__).resolve().parent
s=(p/"build_contour.py").read_text(encoding="utf-8")
s="from astra_scoop import make_scoop\n"+s
s=s.replace("yy=sign*(23.5+fold)","yy=sign*(10.5+fold)")
s=s.replace('''def hinge_cap():''',
'''def moving_scoop(i):
    kind=abs(i)
    direction=1 if i<=0 else -1
    w=[55,51,45,39,31][kind]
    up=[58,48,38,26,10][kind]
    down=[36,32,26,20,8][kind]
    return make_scoop(w,up,down,-1,0,direction).translate((0,-18.0,0))

def hinge_cap():''')
a='''for i in range(-4,5):
    for sign in (-1,1):
        STATION_PARTS[f"blade_{i}_{sign}"]=blade(i,sign)'''
b='''for i in range(-4,5):
    for sign in (-1,1):
        STATION_PARTS[f"blade_{i}_{sign}"]=blade(i,sign)
    STATION_PARTS[f"scoop_{i}"]=moving_scoop(i)'''
assert a in s
s=s.replace(a,b)
a='''        add(f"blade_{i}_{sign}","leaf",f"station_{i}_blade_{sign}",x,sign*16*lane,HEIGHT)'''
b='''        add(f"blade_{i}_{sign}","fixed",f"station_{i}_blade_{sign}",x,sign*8*lane,HEIGHT)'''
assert a in s
s=s.replace(a,b)
a='''    add("shaft_lane_0_knob" if i==4 else f"shaft_lane_{lane}", "leaf", f"station_{i}_shaft",x,0,HEIGHT,color="metal")'''
b='''    add(f"scoop_{i}","leaf",f"station_{i}_moving_scoop",x,-16*lane,HEIGHT)
    add("shaft_lane_0_knob" if i==4 else f"shaft_lane_{lane}", "leaf", f"station_{i}_shaft",x,0,HEIGHT,color="metal")'''
assert a in s
s=s.replace(a,b)
s=s.replace('''    "sampled_exact_distances_between_neighbouring_middle_petal_solids_mm":DISTANCES,''','''    "sampled_exact_distances_between_neighbouring_middle_petal_solids_mm":DISTANCES,''')
(p/"build_contour.py").write_text(s,encoding="utf-8")
(p/"astra_scoop.py").write_text((p.parent/"astra_scoop.py").read_text(encoding="utf-8"),encoding="utf-8")
print("Modeled 9 exterior bent-metal louvres over reference-contour fixed diffuser hull",flush=True)
