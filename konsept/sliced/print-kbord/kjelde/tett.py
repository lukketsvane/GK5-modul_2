import zipfile, re, sys
from collections import Counter, defaultdict
def les(body):
    V=[tuple(map(float,x)) for x in re.findall(r'<vertex x="([-\d.e]+)" y="([-\d.e]+)" z="([-\d.e]+)"',body)]
    T=[list(map(int,x)) for x in re.findall(r'<triangle v1="(\d+)" v2="(\d+)" v3="(\d+)"',body)]
    return V,T
def opne(T):
    E=Counter((t[i],t[(i+1)%3]) for t in T for i in range(3))
    return [(u,v) for (u,v),n in E.items() if E.get((v,u),0)!=n]
def paa(V,u,v,w):
    a,b,c=V[u],V[v],V[w]
    ab=[b[i]-a[i] for i in range(3)]; ac=[c[i]-a[i] for i in range(3)]
    L=sum(x*x for x in ab)
    if L==0: return False
    t=sum(ab[i]*ac[i] for i in range(3))/L
    if t<=1e-9 or t>=1-1e-9: return False
    d=[ac[i]-t*ab[i] for i in range(3)]
    return sum(x*x for x in d)<1e-10
def tett(V,T):
    for _ in range(20):
        op=opne(T)
        if not op: break
        endra=False
        punkt=set(x for e in op for x in e)
        for (u,v) in op:
            for w in punkt:
                if w in (u,v) or not paa(V,u,v,w): continue
                for t in T:
                    for i in range(3):
                        if t[i]==u and t[(i+1)%3]==v:
                            c=t[(i+2)%3]; T.remove(t); T.append([u,w,c]); T.append([w,v,c]); endra=True; break
                    if endra: break
                if endra: break
            if endra: break
        if not endra: break
    return T
for f in sys.argv[1:]:
    z=zipfile.ZipFile(f); filer={n:z.read(n) for n in z.namelist()}; z.close()
    m=filer['3D/3dmodel.model'].decode()
    def byt(mo):
        head,body,tail=mo.group(1),mo.group(2),mo.group(3)
        V,T=les(body)
        if not opne(T): return mo.group(0)
        T=tett(V,T)
        print(f.split('/')[-1], 'tetta, opne no', len(opne(T)))
        tris=''.join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a,b,c in T)
        body=re.sub(r'<triangles>.*?</triangles>',f'<triangles>{tris}</triangles>',body,flags=re.S)
        return head+body+tail
    ny=re.sub(r'(<object id="\d+"[^>]*>)(.*?)(</object>)',byt,m,flags=re.S)
    if ny!=m:
        filer['3D/3dmodel.model']=ny.encode()
        with zipfile.ZipFile(f,'w',zipfile.ZIP_DEFLATED) as z:
            for n,d in filer.items(): z.writestr(n,d)
