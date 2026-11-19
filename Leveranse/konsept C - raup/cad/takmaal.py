from pathlib import Path
import numpy as np, csv
r=Path(__file__).resolve().parents[1]; a=np.load(r/'kontroll/fbx_malenett.npz'); p=(a['c001']-[.15,-.25,0])*270/a['c006'][:,2].max(); t=p[a['c001_tri']]; k=t[:,0,:]; u=t[:,1,:]-k; v=t[:,2,:]-k; det=u[:,0]*v[:,1]-u[:,1]*v[:,0]; valid=np.abs(det)>1e-7; det=np.where(valid,det,1.)
f=r/'kontroll/fbx_tak.csv'
with f.open('w',newline='') as file:
    w=csv.writer(file);w.writerow(['x_mm','y_mm','topp_mm','botn_mm']);
    for y in range(-70,91,10):
        line=[]
        for x in range(-90,101,10):
            co=([x,y]-k[:,:2]); s=(co[:,0]*v[:,1]-co[:,1]*v[:,0])/det; d=(u[:,0]*co[:,1]-u[:,1]*co[:,0])/det; ok=valid&(s>=0)&(d>=0)&(s+d<=1); z=(k[:,2]+s*u[:,2]+d*v[:,2])[ok];line.append(f'{z.max():3.0f}' if len(z) else '  .');
            if len(z): w.writerow([x,y,round(z.max(),2),round(z.min(),2)])
        print(y,' '.join(line))
assert f.stat().st_size>200
