# -*- coding: utf-8 -*-
# rekning_endeleg.py · Kran, endeleg arkitektur: masse, tyngdepunkt, vippevinklar og armmoment.
# Geometri frå referanse/maaling.json (kameratilpassing). x mot armtuppen frå leddaksen, y fram, z opp frå bordet.
#   py -3 design/rekning_endeleg.py   (skala 0,85/1,00/1,15, armvinkel -30/0/+75, og plan B med to lag)
import math, json, sys
from shapely.geometry import Polygon, Point, LineString, box
from shapely.ops import unary_union
from shapely import affinity
ST, AL, PA, PETG, EP = 7.85e-3, 2.70e-3, 1.14e-3, 1.27e-3, 1.15e-3
G=9.81
def geo(s, lag=3):
    J=(0.0,330.0*s)
    L=(-154.2*s,0.0); R=(25.6*s,0.0)
    Rt=24.6*s
    top=Point(J).buffer(Rt,quad_segs=64)
    hull=unary_union([top,Point(L).buffer(0.01),Point(R).buffer(0.01)]).convex_hull
    # høgrekanten: line (25.6,0)->(10.4,314.1)
    p1=(25.6*s,0); p2=(10.4*s,314.1*s)
    dx,dz=p2[0]-p1[0],p2[1]-p1[1]
    # halvplan til venstre for linja, under z=317s; over 317 tillat R16-bule (skjult bak øyret)
    far=2000
    hp=Polygon([ (p1[0]-dx*far/ dz*0, -10), (p1[0]+ (-10-p1[1])*dx/dz,-10), (p1[0]+(far-p1[1])*dx/dz, far), (-far,far), (-far,-10)])
    hp=Polygon([(p1[0]+(-10-p1[1])*dx/dz,-10),(p1[0]+(far-p1[1])*dx/dz,far),(-far,far),(-far,-10)])
    out=hull.intersection(hp).union(Point(J).buffer(16*s,quad_segs=64).intersection(hull))
    S1=(-105.9*s,50.3*s); S2=(-12.3*s,313.1*s); Sb=6.9*s
    spalte=LineString([S1,S2]).buffer(Sb,quad_segs=32)
    return out, spalte, J
def plate_mass(s, midlag=True):
    out,spalte,J=geo(s)
    base=out.difference(spalte)
    hol=Point(J).buffer(5.1,quad_segs=32)
    # front: hol + bogespor R12 75..196 grader, 3.4 brei
    arc=LineString([(J[0]+12*math.cos(math.radians(a)),J[1]+12*math.sin(math.radians(a))) for a in range(75,197,3)]).buffer(1.7)
    front=base.difference(hol).difference(arc)
    back=base.difference(hol).difference(box(-50*s,4,-30*s,14))
    parts=[(front,1.5,1.5*0.5+0.75),(back,1.5,-1.5)]
    if midlag:
        kam=Point(J).buffer(8.5,quad_segs=32)
        # kanal 3.4 brei: frå vindauget (-40s, 9) vassrett til x 4s, så opp langs høgresida til kammeret
        xr=lambda z: 25.6*s+(z)*(10.4*s-25.6*s)/(314.1*s)
        k=LineString([(-40*s,9),(xr(9)-8,9),(xr(300*s)-7, 300*s),(J[0]+3,J[1]-6)]).buffer(1.7)
        mid=base.difference(kam).difference(k).difference(box(-500,-10,500,3))
        parts.append((mid,1.5,0.0))
    m=0;mx=0;mz=0;my=0;info={}
    for poly,t,y in parts:
        mm=poly.area*t*ST; c=poly.centroid
        m+=mm; mx+=mm*c.x; mz+=mm*c.y; my+=mm*y
    info=dict(areal_brutto=out.area, areal_netto=base.area, front=front.area)
    return m, (mx/m, my/m, mz/m), info, out, spalte
def lampe(s=1.0, th=0.0, midlag=True, flens=22.0, mu=0.25):
    pts=[]
    mp,cp,info,out,sp=plate_mass(s,midlag)
    if not midlag: pass
    pts.append(('plate',mp,cp))
    fl=flens*s; xl,xr=-154.2*s,25.6*s; Lf=xr-xl
    t_y=2.25 if midlag else 1.5
    mf=fl*Lf*1.5*ST
    pts.append(('framflens',mf,((xl+xr)/2, t_y+fl/2, 1.0+0.75)))
    pts.append(('bakflens',mf,((xl+xr)/2, -(t_y+fl/2), 1.0+0.75)))
    if not midlag: pts.append(('U-profil kabel',20.0,(5*s,-t_y-4,170*s)))
    pts.append(('epoksy, sparkel, lakk',(info['areal_netto']*0.2*EP if midlag else info['areal_netto']*0.1*EP)+6,(cp[0],0,cp[2])))
    pts.append(('lomme med elektronikk',24.0,(-40*s,-(t_y+10),14)))
    pts.append(('leidning i plata',2.0,(-10*s,0,150*s)))
    pts.append(('filt',2*Lf*fl*1.0*0.3e-3,((xl+xr)/2,0,0.5)))
    J=(0,330*s)
    pts.append(('aksel, mutrar, fjører, skiver, knott',21.0,(0,1.0,J[1])))
    arm=[('øyre Al',24.0,(12*s,5.25,332*s)),
         ('profil',90.2*s,(254.5*s,13.25,326.3*s)),('deksel',8.1*s,(254.5*s,13.25,326.3*s)),
         ('COB',5.8*s,(290*s,13.25,318.5*s)),('endelokk',2.0,(481.5*s,13.25,326.3*s)),
         ('popnaglar',1.0,(40*s,9,326*s)),('leidning i arm',0.5,(65*s,13,320*s))]
    c,sn=math.cos(math.radians(th)),math.sin(math.radians(th))
    am=0;amx=0
    for n,m,(x,y,z) in arm:
        dz=z-J[1]; X=x*c-dz*sn; Z=J[1]+x*sn+dz*c
        pts.append((n,m,(X,y,Z)))
        am+=m; amx+=m*x  # moment med vassrett arm
    M=sum(p[1] for p in pts)
    cg=[sum(p[1]*p[2][i] for p in pts)/M for i in range(3)]
    xe=xr-1; xb=xl+1; ye=t_y+fl-1
    ang=dict(mot_armen=math.degrees(math.atan((xe-cg[0])/cg[2])),fra_armen=math.degrees(math.atan((cg[0]-xb)/cg[2])),
             framover=math.degrees(math.atan((ye-cg[1])/cg[2])),bakover=math.degrees(math.atan((ye+cg[1])/cg[2])))
    Marm=am*G*1e-6*(amx/am)
    return dict(M=M,cg=cg,ang=ang,arm_m=am,arm_cg=amx/am,Marm=Marm,mp=mp,info=info,pts=pts,xe=xe,ye=ye,Lf=Lf)
if __name__=='__main__':
    r=lampe()
    print('plate',round(r['mp'],1),{k:round(v,1) for k,v in r['info'].items()})
    for n,m,p in r['pts']: print(f'  {n:40s} {m:7.1f}  ({p[0]:7.1f},{p[1]:6.1f},{p[2]:6.1f})')
    print('total',round(r['M'],1),[round(v,2) for v in r['cg']],{k:round(v,2) for k,v in r['ang'].items()})
    print('arm',round(r['arm_m'],1),'cg',round(r['arm_cg'],1),'M',round(r['Marm'],3))
    reff=2/3*(10**3-5.25**3)/(10**2-5.25**2); print('reff',reff)
    for mu in (0.2,0.25,0.3): print('T',mu,round(2*mu*140*reff/1000,3))
    T=2*0.25*140*reff/1000
    # tippekraft mot armen, vassrett arm
    Ltip=480-r['xe']
    Ftip=r['M']/1000*G*(r['xe']-r['cg'][0])/1000/(Ltip/1000)
    print('tippkraft',round(Ftip,2),'ned',round((T-r['Marm'])/0.48,2),'opp',round((T+r['Marm'])/0.48,2),'Ltip',Ltip)
    worst={}
    for s in (0.85,1.0,1.15):
        for th in (-30,0,75):
            q=lampe(s,th)
            print(s,th,round(q['M']),[round(v,1) for v in q['cg']],{k:round(v,1) for k,v in q['ang'].items()},'Marm',round(q['Marm'],3))
    print('--- utan midtlag (plan B, 2x1.5)')
    for s in (0.85,1.0,1.15):
        for th in (-30,0,75):
            q=lampe(s,th,midlag=False)
            print(s,th,round(q['M']),[round(v,1) for v in q['cg']],{k:round(v,1) for k,v in q['ang'].items()})
