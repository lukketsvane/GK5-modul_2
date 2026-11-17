import json
import math
from pathlib import Path
import cadquery as cq
from generate_cad import D, P

OUT=Path(__file__).resolve().parent
rho={'01_base_casting':2.7,'02_service_hatch':2.7,'03_ballast':7.85,'04_pedestal':2.7,
 '05_hinge_yoke':2.7,'06_pivot_axle_M5':7.85,'19_tilt_stop_pin':7.85,'07_friction_washer_L':1.3,
 '07_friction_washer_R':1.3,'08_head_chassis':2.7,'09_canopy_top':2.7,
 '10_front_lens':1.2,'11_rear_halo_lens':1.2,'12_recessed_work_lens':1.2,
 '13_LED_MCPCB':2.1,'14_ambient_LED_strip':2.1,'15_battery_pack':1.5,
 '16_control_PCB':1.8,'18_heat_spreader':2.7}
for k in D:
    if k.startswith(('17_canopy_M3_','20_stem_M4_','21_hatch_M3_')): rho[k]=7.85

solidcheck={k:{'valid': sh.isValid(),'solid_count':len(sh.Solids())} for k,sh in D.items()}
mmg={k:sh.Volume()/1000*rho[k] for k,sh in D.items()}
M=sum(mmg.values())
centroid=[sum(mmg[k]*getattr(D[k].Center(),a) for k in D)/M for a in ('x','y','z')]
headparts=['05_hinge_yoke','08_head_chassis','09_canopy_top','10_front_lens','11_rear_halo_lens','12_recessed_work_lens','13_LED_MCPCB','14_ambient_LED_strip','18_heat_spreader']
headmass=sum(mmg[k] for k in headparts)
headcx=sum(mmg[k]*D[k].Center().x for k in headparts)/headmass
lever_x=headcx-P['pivot_x']
hinge_Nm=headmass/1000*9.81*lever_x/1000
checkpairs=[('01_base_casting','02_service_hatch'),('01_base_casting','03_ballast'),('01_base_casting','15_battery_pack'),('01_base_casting','16_control_PCB'),('01_base_casting','04_pedestal'),('04_pedestal','09_canopy_top'),('04_pedestal','08_head_chassis'),('04_pedestal','05_hinge_yoke'),('05_hinge_yoke','08_head_chassis'),('05_hinge_yoke','09_canopy_top'),('08_head_chassis','10_front_lens'),('08_head_chassis','11_rear_halo_lens'),('08_head_chassis','12_recessed_work_lens'),('08_head_chassis','18_heat_spreader'),('13_LED_MCPCB','18_heat_spreader'),('03_ballast','15_battery_pack'),('15_battery_pack','16_control_PCB')]
collisions={a+' / '+b:round(D[a].intersect(D[b]).Volume(),1) for a,b in checkpairs}
sweep={}
for deg in (15,20,25,30,33,37,40,45):
    t=cq.Workplane('XY').newObject([D['08_head_chassis']]).rotate((P['pivot_x'],0,P['pivot_z']),(P['pivot_x'],1,P['pivot_z']),deg-P['tilt_deg']).val()
    top=cq.Workplane('XY').newObject([D['09_canopy_top']]).rotate((P['pivot_x'],0,P['pivot_z']),(P['pivot_x'],1,P['pivot_z']),deg-P['tilt_deg']).val()
    yoke=cq.Workplane('XY').newObject([D['05_hinge_yoke']]).rotate((P['pivot_x'],0,P['pivot_z']),(P['pivot_x'],1,P['pivot_z']),deg-P['tilt_deg']).val()
    sweep[str(deg)]={'mm_below_table_min':round(min(t.BoundingBox().zmin,top.BoundingBox().zmin),1),
                     'collision_with_stem_mm3':round(sum(x.intersect(D['04_pedestal']).Volume() for x in (t,top,yoke)),1),
                     'collision_with_foot_mm3':round(sum(x.intersect(D['01_base_casting']).Volume() for x in (t,top,yoke)),1)}
report={
 'solidcheck':solidcheck,
 'non_manifold_or_invalid':[k for k,v in solidcheck.items() if not v['valid'] or v['solid_count']!=1],
 'mass_g_estimate':round(M,1),
 'center_of_mass_mm':list(map(lambda v:round(v,1),centroid)),
 'head_mass_g_estimate':round(headmass,1),
 'head_cg_x_mm':round(headcx,1),
 'hinge_static_torque_Nm_estimate':round(hinge_Nm,3),
 'worst_y_tip_restoring_Nm':round(M/1000*9.81*(P['base_y']/2-abs(centroid[1]))/1000,3),
 'worst_x_tip_restoring_Nm':round(M/1000*9.81*(P['base_x']/2-abs(centroid[0]))/1000,3),
 'moment_from_10N_push_at_hinge_Nm':round(10*P['pivot_z']/1000,3),
 'max_static_lateral_push_N_at_hinge':round(M/1000*9.81*(P['base_y']/2-abs(centroid[1]))/P['pivot_z'],2),
 'minimum_mass_for_10N_push_y_at_pivot_kg':round(10*P['pivot_z']/1000/ (9.81*(P['base_y']/2-abs(centroid[1]))/1000),2),
 'collision_volumes_mm3':collisions,
 'tilt_sweep':sweep}
(OUT/'validation.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='solidcheck'},indent=2))