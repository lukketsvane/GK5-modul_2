import bpy
ob=bpy.data.objects['Upper uninterrupted dish | 342 x 322 mm']
m=ob.data
print('POLYGONS',len(m.polygons))
for i in [0,255,2560-256,2560-1,2560,2561,2814,2815]:
 p=m.polygons[i]
 print('POLY',i,'NORMAL',[round(v,3) for v in p.normal],'FACE_VERTICES',list(p.vertices)[:4])
print('DOT_LAST',m.polygons[2559].normal.dot(m.polygons[2560].normal))
