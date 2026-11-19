"""Verdssnitt av kjelda, rå lineære trekantsnitt. Origo og skalering i mm til RAUP-R1."""
from pathlib import Path
import json,numpy as np
r=Path(__file__).resolve().parents[1]; out=r/'kontroll'; data=np.load(out/'fbx_malenett.npz'); sc=270/float(data['c006'][:,2].max()); zero=np.array([.15,-.25,0]); parts={k:(data[k]-zero)*sc for k in data if not k.endswith('_tri')}
def section(k,z):
    t=parts[k][data[k+'_tri']]; t=t[(t[:,:,2].min(1)<z)&(t[:,:,2].max(1)>z)]; seg=[]
    for face in t:
        ends=[]
        for p,q in zip(face,np.roll(face,-1,axis=0)):
            if (p[2]<z)!=(q[2]<z): ends.append(p[:2]+(z-p[2])/(q[2]-p[2])*(q[:2]-p[:2]))
        if len(ends)==2: seg.append(ends)
    return np.array(seg)
def loops(seg):
    adj={}; nd=lambda p:tuple(p.round(3));
    for a,b in seg:
        a,b=nd(a),nd(b)
        if a==b:continue
        adj.setdefault(a,set()).add(b); adj.setdefault(b,set()).add(a)
    lines=[]
    while adj:
        start=next((a for a,v in adj.items() if len(v)==1),next(iter(adj))); line=[start]; q=start
        while q in adj:
            v=next(iter(adj[q])); adj[q].remove(v); adj[v].remove(q)
            if not adj[q]:del adj[q]
            if v in adj and not adj[v]:del adj[v]
            line.append(v);q=v
        lines.append(np.array(line))
    return sorted(lines,key=lambda p:-np.linalg.norm(np.diff(p,axis=0),axis=1).sum())
slices={}
for k,levels in [('c001',[1,8,15,28,38,50,65,85,105,125,145,165,180,190]),('c006',[11,15,25,50,100,175,220,240,255,265])]:
    for z in levels:
        seg=section(k,z+.0137); ls=loops(seg); slices[f'{k}_{z}']=[p.tolist() for p in ls]
        if not ls:continue
        sel=ls[0]; lengths=np.r_[0,np.cumsum(np.linalg.norm(np.diff(sel,axis=0),axis=1))]; pts=np.array([np.interp(np.arange(0,lengths[-1],12),lengths,sel[:,i]) for i in range(2)]).T
        print(k,z,'loops',len(ls),'xy',seg.min(axis=(0,1)).round(1),seg.max(axis=(0,1)).round(1), 'len',round(lengths[-1],1));
        if z in (15,65,125,180,100,240):print(' outline',pts.round(1).tolist())
(out/'fbx_snitt_mm.json').write_text(json.dumps({'skala_mm_per_BU':sc,'origo_BU':zero.tolist(),'snitt':slices},separators=(',',':')),encoding='utf-8');print('scale',sc)
for k,a in parts.items(): print(k,a.min(0).round(1).tolist(),a.max(0).round(1).tolist());
print('Relevante kontekstdokument:'); print('\n'.join(str(p.relative_to(r.parents[1])) for p in r.parents[1].rglob('*.md') if any(w in p.stem.lower() for w in ('prism','monitor','diffus','raup','komponent')) )[:4000]); assert len(slices)>20
