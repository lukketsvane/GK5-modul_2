import math
import json
import csv
from pathlib import Path
import cadquery as cq

OUT = Path(__file__).resolve().parent
P = dict(head_a=162, head_b=132, tilt_deg=33, head_cx=30, head_cz=158,
         pivot_x=-77, pivot_z=207, base_x=196, base_y=118, base_h=27,
         canopy_t=1.1, stem_w=34, stem_d=44, body_x=-77, head_lip_depth=23)
a = math.radians(P['tilt_deg'])
c, s = math.cos(a), math.sin(a)
dx, dz = P['pivot_x']-P['head_cx'], P['pivot_z']-P['head_cz']
P['pivot_local_x'] = c*dx-s*dz
P['pivot_local_z'] = s*dx+c*dz
D = {}
META = {}

def part(key, solid, material, process, note):
    D[key] = solid.val() if isinstance(solid,cq.Workplane) else solid
    META[key] = dict(material=material, process=process, note=note)

def ec(a,b,z,t,cx=0,cy=0):
    return cq.Workplane('XY').workplane(offset=z).center(cx,cy).ellipse(a,b).extrude(t)

def rounded_box(l,w,h,r,center=(0,0,0)):
    return cq.Workplane('XY').box(l,w,h,centered=(True,True,False)).edges('|Z').fillet(r).translate(center)

def crescent(outer_a, outer_b, inner_a, inner_b, start_deg, end_deg, z, h):
    n=90
    phi=[math.radians(start_deg+(end_deg-start_deg)*i/n) for i in range(n+1)]
    pts=[(outer_a*math.cos(t),outer_b*math.sin(t)) for t in phi]
    pts += [(inner_a*math.cos(t),inner_b*math.sin(t)) for t in reversed(phi)]
    return cq.Workplane('XY').workplane(offset=z).polyline(pts).close().extrude(h)

def head(solid):
    return solid.rotate((0,0,0),(0,1,0),P['tilt_deg']).translate((P['head_cx'],0,P['head_cz']))

def bore_y(x,z,r,from_y=38,length=76):
    return cq.Workplane('XZ',origin=(0,from_y,0)).center(x,z).circle(r).extrude(length)

base=rounded_box(P['base_x'],P['base_y'],P['base_h'],29)
base=base.cut(rounded_box(P['base_x']-5,P['base_y']-5,25.5,26.5,center=(0,0,-1.5)))
for x in (-68,68):
    for y in (-36,36):
        boss=cq.Workplane('XY').workplane(offset=3).center(x,y).circle(5).extrude(23)
        base=base.union(boss)
        base=base.cut(cq.Workplane('XY').workplane(offset=-1).center(x,y).circle(1.65).extrude(25.6))
for y in (-14,14):
    base=base.cut(cq.Workplane('XY').workplane(offset=19).center(-77,y).circle(2.1).extrude(11))
port=cq.Workplane('XZ',origin=(0,64,0)).center(43,13.5).rect(10,4.8).extrude(13)
base=base.cut(port)
elbow=(cq.Workplane('XZ',origin=(0,19,0)).moveTo(-63,26).lineTo(-45,26).lineTo(-45,27).threePointArc((-57.73,32.27),(-63,45)).close().extrude(38))
base=base.union(elbow)
part('01_base_casting',base,'Al 6063-T5 or die cast Al','CNC prototype, casting DFM','Shell, stem attachment and M3 service hatch bosses')

hatch=rounded_box(189,111,1.5,25.5,center=(0,0,1))
for x in (-68,68):
    for y in (-36,36):
        hatch=hatch.cut(cq.Workplane('XY').workplane(offset=0.5).center(x,y).circle(1.8).extrude(3))
part('02_service_hatch',hatch,'Al 5052 2.1 mm','laser cut / CNC','Underside accessible battery and electronics')
for x in (-68,68):
    for y in (-36,36):
        headcut=cq.Workplane('XY').workplane(offset=0.8).center(x,y).circle(3.05).extrude(0.9)
        hatch=hatch.cut(headcut)
D['02_service_hatch']=hatch.val()

ballast=cq.Workplane('XY').box(42,72,11,centered=(True,True,False)).translate((-35,0,4))
part('03_ballast',ballast,'S235 steel','laser cut plates / steel block','Prototype weight; may conflict with 1.2 kg target')

stem=(cq.Workplane('XZ',origin=(0,19,0))
      .moveTo(-91,27).lineTo(-91,202)
      .threePointArc((-87,213),(-77,218))
      .threePointArc((-67,213),(-63,202))
      .lineTo(-63,27).close().extrude(38))
stem=stem.cut(cq.Workplane('XY').box(23,32,167).translate((-77,0,113.5)))
for y in (-14,14):
    stem=stem.union(cq.Workplane('XY').workplane(offset=30).center(-77,y).circle(5.0).extrude(24))
stem=stem.cut(bore_y(-77,207,2.65,from_y=28,length=56))
stem=stem.cut(bore_y(-69,202,1.65,from_y=25,length=50))
for y in (-14,14):
    stem=stem.cut(cq.Workplane('XY').workplane(offset=24).center(-77,y).circle(1.7).extrude(27))
stem=stem.cut(cq.Workplane('YZ',origin=(-60,0,0)).center(0,185).circle(3).extrude(15))
part('04_pedestal',stem,'Al 6063-T5','extrusion + CNC top and holes','Hollow stem with pivot and cable exit')
for y in (-14,14):
    bolt=cq.Workplane('XY').workplane(offset=20).center(-77,y).circle(1.9).extrude(24)
    bolt=bolt.union(cq.Workplane('XY').workplane(offset=18.3).center(-77,y).circle(3.4).extrude(1.7))
    part('20_stem_M4_'+str(y),bolt,'A2 stainless','purchased','M4 from underside, clearance hole in base and tapped stem')

plx, plz = P['pivot_local_x'],P['pivot_local_z']
ears=None
for y in (-24,24):
    w=cq.Workplane('XY').box(33,5,34).translate((plx+3,y,plz+6.5))
    ears=w if ears is None else ears.union(w)
bridge=cq.Workplane('XY').box(39,53,3.0).translate((plx+2,0,5.45))
ears=ears.union(bridge)
ears=ears.cut(bore_y(plx,plz,2.8,from_y=38,length=76))
for deg in range(15,38):
    t=math.radians(deg)
    cx=plx+math.cos(t)*8-math.sin(t)*(-5)
    cz=plz+math.sin(t)*8+math.cos(t)*(-5)
    ears=ears.cut(bore_y(cx,cz,2.0,from_y=38,length=76))
ears=ears.cut(cq.Workplane('XY').workplane(offset=2).center(plx+12,0).circle(2.8).extrude(7))
for y in (-20.5,20.5):
    ears=ears.cut(cq.Workplane('XY').workplane(offset=plz+24).center(plx+6,y).circle(1.65).extrude(8))
part('05_hinge_yoke',head(ears),'Al 6061-T6','CNC','Two ears, bridge and M5 pivot bore')

pivot_axle=cq.Workplane('XZ',origin=(0,33,0)).center(-77,207).circle(2.5).extrude(66)
pivot_axle=pivot_axle.union(cq.Workplane('XZ',origin=(0,34.2,0)).center(-77,207).circle(5).extrude(1.8))
part('06_pivot_axle_M5',pivot_axle,'Steel, ISO 7380-2 equivalent','purchased / shortened','Simplified hardware, locking torque mechanism TBD')
stop_pin=cq.Workplane('XZ',origin=(0,23,0)).center(-69,202).circle(1.6).extrude(46)
part('19_tilt_stop_pin',stop_pin,'A2 stainless','purchased','Slot-in-yoke end stops nominally 15–37 degrees')
for sign in (-1,1):
    y=sign*20.3
    washer=(cq.Workplane('XZ',origin=(0,y+1.1,0)).center(-77,207).circle(8.5).circle(2.7).extrude(2.2))
    part('07_friction_washer_'+('L' if sign<0 else 'R'),washer,'POM/friction laminate','purchased','Friction test required to set holding torque')

sidewall=ec(157.8,127.8,-12,23.5).cut(ec(155.7,125.7,-12.5,25))
top_flange=ec(157.8,127.8,9.5,2).cut(ec(143.5,113.5,9,3))
bottom_lip=ec(157.8,127.8,-12,2.6).cut(ec(136,105.5,-12.5,4))
front_slot=crescent(154.5,124.5,140,110,195,345,-12.7,4)
bottom_lip=bottom_lip.cut(front_slot)
bottom_lip=bottom_lip.cut(crescent(158.4,128.4,152.8,122.8,194,346,-12.7,4.0))
rear_slot=crescent(158.1,128.1,154.7,124.7,20,160,4.0,5.6)
sidewall=sidewall.cut(rear_slot)
front_side_slot=crescent(158.3,128.3,154.6,124.6,194,346,-10.7,5.5)
sidewall=sidewall.cut(front_side_slot)
tray=sidewall.union(top_flange).union(bottom_lip)
for x,y in ((-111,-73),(-111,73),(112,-73),(112,73)):
    rib=cq.Workplane('XY').workplane(offset=2).center(x,y).circle(6.5).extrude(8.4)
    tray=tray.union(rib)
    tray=tray.cut(cq.Workplane('XY').workplane(offset=2).center(x,y).circle(1.65).extrude(12))
part('08_head_chassis',head(tray),'Al 6061-T6','CNC / thin-wall casting','Ventilated shell with front rim and rear halo slit')

lid=ec(162,132,11.7,P['canopy_t'])
for x,y in ((-111,-73),(-111,73),(112,-73),(112,73)):
    lid=lid.union(cq.Workplane('XY').workplane(offset=7).center(x,y).circle(5.0).extrude(4.7))
    lid=lid.cut(cq.Workplane('XY').workplane(offset=6.8).center(x,y).circle(1.45).extrude(4.5))
for y in (-20.5,20.5):
    lid=lid.union(cq.Workplane('XY').workplane(offset=7).center(plx+6,y).circle(5).extrude(4.7))
    lid=lid.cut(cq.Workplane('XY').workplane(offset=6.7).center(plx+6,y).circle(1.45).extrude(4.5))
part('09_canopy_top',head(lid),'Al 5052 H32, 1.1 mm','formed sheet + CNC trim','Broad uninterrupted top, screws on underside subject to review')

front_lens=crescent(154.3,124.3,140.2,110.2,195,345,-11.9,2.1)
front_lens=front_lens.union(crescent(157.9,127.9,155.7,125.7,196,344,-10.45,4.85))
front_lens=front_lens.union(crescent(156.5,126.5,153.5,123.5,196,344,-10.5,0.9))
part('10_front_lens',head(front_lens),'opal polycarbonate','injection mould / milled prototype','Transparent optical geometry; actual transmission unmeasured')
rear_lens=crescent(158.0,128.0,155.0,125.0,20,160,4.2,5.2)
part('11_rear_halo_lens',head(rear_lens),'opal polycarbonate','injection mould / milled prototype','Indirect rear rim glow')

work_lens=ec(108,74,-7.1,1.8,cx=20)
part('12_recessed_work_lens',head(work_lens),'opal microprismatic PC','CNC prototype / injection mould','Work light recessed inside opaque rim; photometry TBD')
work_board=ec(98,62,-2.5,1.6,cx=20)
part('13_LED_MCPCB',head(work_board),'Al MCPCB 1.6 mm','PCB fabrication','Thermal bonding to integrated aluminum spreader TBD')
front_led=crescent(153,123,144.5,114.5,198,342,-7.1,1.3)
part('14_ambient_LED_strip',head(front_led),'Al MCPCB linear segments','PCB fabrication','Warm 2200K rear + front channel conceptual')
heat=ec(102,68,-0.9,1.2,cx=20)
heat=heat.union(cq.Workplane('XY').box(38,10,1.5).translate((139,0,0.05)))
heat=heat.union(cq.Workplane('XY').box(76,10,1.5).translate((-119,0,0.05)))
part('18_heat_spreader',head(heat),'Al 6061-T6','CNC / stamped','Thermal path from MCPCB to head rim pending conduction test')

battery=(cq.Workplane('YZ',origin=(1.5,18,13)).circle(9).extrude(65)).union(
    rounded_box(71,23,19,4,center=(34,18,3.5)))
part('15_battery_pack',battery,'1x protected 18650 cell, pouch carrier','purchased / certified pack','13 Wh nominal target, exact pack and charging PCB TBD')
control=rounded_box(46,24,2,2,center=(40,-21,16))
for x,y in ((22,-28),(58,-28)):
    control=control.union(cq.Workplane('XY').workplane(offset=18).center(x,y).box(9,5,5))
part('16_control_PCB',control,'FR4 + LED driver + USB-C PD/CC','electronics assembly','Placeholder PCB volume only; circuit not designed')

for x in (-68,68):
    for y in (-36,36):
        screw=cq.Workplane('XY').workplane(offset=1.65).center(x,y).circle(1.4).extrude(11.4)
        screw=screw.union(cq.Workplane('XY').workplane(offset=0.75).center(x,y).circle(2.75).extrude(0.9))
        part('21_hatch_M3_%d_%d'%(x,y),screw,'A2 stainless','purchased','Recessed screw from underside')

for x,y in ((-111,-73),(-111,73),(112,-73),(112,73),(plx+6,-20.5),(plx+6,20.5)):
    hinge_mount=abs(y)==20.5
    screw=cq.Workplane('XY').workplane(offset=3.8 if hinge_mount else 3).center(x,y).circle(1.5).extrude(6.7 if hinge_mount else 7.5)
    screw=screw.union(cq.Workplane('XY').workplane(offset=2.75 if hinge_mount else 2).center(x,y).circle(2.75).extrude(1.25))
    part('17_canopy_M3_%d_%d'%(x,y),head(screw),'A2 stainless','purchased','M3 screw simplified')

if __name__=='__main__':
    (OUT/'parts').mkdir(exist_ok=True)
    palette={'Al':'#777674','S235':'#444443','Steel':'#333332','POM':'#c1bcb1','opal':'#ffe2a5','FR4':'#4b5653','1x protected':'#72756b'}
    assembly=cq.Assembly(name='B Tilted Disc / Concept B - Rev A')
    for k,shape in D.items():
        color=next((v for prefix,v in palette.items() if META[k]['material'].startswith(prefix)), '#77736e')
        assembly.add(shape,name=k,color=cq.Color(color))
        cq.exporters.export(shape,str(OUT/'parts'/(k+'.step')),exportType='STEP')
        if k in ('01_base_casting','02_service_hatch','04_pedestal','05_hinge_yoke','08_head_chassis',
                 '09_canopy_top','10_front_lens','11_rear_halo_lens','12_recessed_work_lens'):
            cq.exporters.export(shape,str(OUT/'parts'/(k+'.stl')),exportType='STL',tolerance=0.18,angularTolerance=0.20)
    assembly.save(str(OUT/'B_tilta_skive_revA_assembly.step'))
    with (OUT/'BOM.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.writer(f)
        writer.writerow(['part','qty','material','process','prototype volume cm3','note'])
        for k,shape in D.items():
            writer.writerow([k,1,META[k]['material'],META[k]['process'],round(shape.Volume()/1000,2),META[k]['note']])
    volume={k:round(sh.Volume(),1) for k,sh in D.items()}
    density={
        '01_base_casting':2.7,'02_service_hatch':2.7,'03_ballast':7.85,'04_pedestal':2.7,
        '05_hinge_yoke':2.7,'06_pivot_axle_M5':7.85,'07_friction_washer_L':1.3,
        '07_friction_washer_R':1.3,'08_head_chassis':2.7,'09_canopy_top':2.7,
        '10_front_lens':1.2,'11_rear_halo_lens':1.2,'12_recessed_work_lens':1.2,
        '13_LED_MCPCB':2.1,'14_ambient_LED_strip':2.1,'15_battery_pack':1.5,'16_control_PCB':1.8,'18_heat_spreader':2.7,'19_tilt_stop_pin':7.85
    }
    for k in D:
        if k.startswith(('17_canopy_M3_','20_stem_M4_','21_hatch_M3_')):
            density[k]=7.85
    mass={k:round(volume[k]/1000*density[k],2) for k in D}
    headkeys=['05_hinge_yoke','08_head_chassis','09_canopy_top','10_front_lens','11_rear_halo_lens','12_recessed_work_lens','13_LED_MCPCB','14_ambient_LED_strip','18_heat_spreader']
    headmass=sum(mass[k] for k in headkeys)
    totalmass=sum(mass.values())
    impact_force=10
    tipping_moment=impact_force*(P['pivot_z']/1000)
    restoring_moment=totalmass/1000*9.81*(P['base_y']/2/1000)
    collisions={}
    for k1,k2 in [('04_pedestal','05_hinge_yoke'),('04_pedestal','08_head_chassis'),('03_ballast','15_battery_pack'),('08_head_chassis','10_front_lens'),('04_pedestal','09_canopy_top'),('05_hinge_yoke','09_canopy_top'),('08_head_chassis','11_rear_halo_lens'),('08_head_chassis','12_recessed_work_lens')]:
        collisions[k1+' vs '+k2]=round(D[k1].intersect(D[k2]).Volume(),2)
    headbottom=min((p.Z for k in ('08_head_chassis','09_canopy_top') for p in D[k].Vertices()))
    report={'params_mm':P,'prototype_estimated_mass_grams':round(totalmass,1),'head_estimated_mass_grams':round(headmass,1),
            'mass_by_part_g':mass,'head_lowest_vertex_z_mm':round(headbottom,1),
            '10N_horizontal_push_at_pivot_moment_Nm':round(tipping_moment,2),
            'max_restore_about_depth_foot_edge_Nm_optimistic':round(restoring_moment,2),
            'collisions_mm3':collisions, 'NOTE':'Gross volume times nominal material density; electronics and fasteners placeholders; preliminary mass only. Tipping moment omits CoM offsets; optimistic estimate.'}
    (OUT/'checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k in ('prototype_estimated_mass_grams','head_estimated_mass_grams','head_lowest_vertex_z_mm','10N_horizontal_push_at_pivot_moment_Nm','max_restore_about_depth_foot_edge_Nm_optimistic','collisions_mm3')},indent=2))