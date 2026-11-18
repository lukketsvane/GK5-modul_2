import cadquery as cq, trimesh, json, math
from pathlib import Path
ROOT=Path(__file__).resolve().parent
S={f.stem:cq.importers.importStep(str(f)).val() for f in (ROOT/'step').glob('C*.step') if f.stem != 'CONCEPT_C_ASSEMBLY_R02'}
f=S['C01_RIB_PETG'];b=S['C02_BASE_PETG'];d=S['C05_DIFFUSER_OPAL_PC'];u=S['C07_UPPER_COLLAR'];steel=S['C04_BALLAST_STEEL'];lid=S['C03_BOTTOM_PETG'];c=S['C06_DIFFUSER_CAP']
R=lambda s,a:s.rotate((0,0,0),(0,0,1),a)
I=lambda a,b:round(a.intersect(b).Volume(),3)
checks={}
checks['fin_base_interference_mm3']=I(R(f,22.5),b)
checks['fin_diffuser_interference_mm3']=I(R(f,22.5),d)
checks['adjacent_fin_interference_mm3']=I(R(f,22.5),R(f,67.5))
checks['top_collar_fin_interference_mm3']=I(R(f,22.5),u)
checks['base_ballast_interference_mm3']=I(b,steel)
checks['base_bottom_interference_mm3']=I(b,lid)
checks['base_core_interference_mm3']=I(b,S['C08_LED_CORE_ALUMINUM'])
checks['base_diffuser_interference_mm3']=I(b,d)
checks['core_socket_clearance_each_side_mm']=round((13.6*.915-12)/2,3)
checks['collar_cap_interference_mm3']=I(u,c)
checks['all_solids_valid']=all(x.isValid() for x in S.values())
checks['print_STL_watertight']=all(trimesh.load_mesh(str(p)).is_watertight for p in (ROOT/'stl').glob('*.stl'))
checks['fits_P1S']=all(max(x.BoundingBox().xlen,x.BoundingBox().ylen,x.BoundingBox().zlen) <=256 for k,x in S.items() if k not in ('C04_BALLAST_STEEL','C08_LED_CORE_ALUMINUM'))
angles=[i*45+22.5 for i in range(8)]
boxes=[R(f,a).BoundingBox() for a in angles]
checks['overall_diameter_x_mm']=round(max(x.xmax for x in boxes)-min(x.xmin for x in boxes),2)
checks['overall_diameter_y_mm']=round(max(x.ymax for x in boxes)-min(x.ymin for x in boxes),2)
checks['overall_height_mm']=round(max(x.zmax for x in boxes),2)
checks['model_height_diameter_ratio']=round(checks['overall_height_mm']/max(checks['overall_diameter_x_mm'],checks['overall_diameter_y_mm']),3)
checks['reference_height_diameter_ratio_approx']=1.89
checks['reference_ratio_difference_pct']=round(abs(checks['model_height_diameter_ratio']/1.89-1)*100,1)
checks['estimated_steel_mass_g']=round(steel.Volume()/1000*7.85,1)
checks['no_unexpected_intersection']=all(v<.1 for k,v in checks.items() if k.endswith('interference_mm3'))
(ROOT/'validation.json').write_text(json.dumps(checks,indent=2))
print(json.dumps(checks,indent=2))
assert checks['all_solids_valid'] and checks['print_STL_watertight'] and checks['fits_P1S']
assert checks['no_unexpected_intersection']
assert checks['reference_ratio_difference_pct']<4
