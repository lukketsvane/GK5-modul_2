import bpy,math
from pathlib import Path
p=Path(__file__).resolve().parent
s=bpy.context.scene
for key in ['Surface | uninterrupted shallow crown','Continuous canopy | pole closure']:
    o=bpy.data.objects.get(key)
    if o:bpy.data.objects.remove(o,do_unlink=True)
tilt=math.radians(34)
co,si=math.cos(tilt),math.sin(tilt)
def hw(x,y,z):
    return ((34+co*x+si*z)*.001,y*.001,(175-si*x+co*z)*.001)
profiles=[(.0001,16.3),(.18,16.1),(.42,15.7),(.68,14.9),(.86,14.0),(.95,13.0),(.992,11.9),(1,11.3)]
n=192
v=[];f=[]
for frac,z in profiles:
    for i in range(n):
        q=2*math.pi*i/n
        v.append(hw(170*frac*math.cos(q),155.3*frac*math.sin(q),z))
for k in range(len(profiles)-1):
    for i in range(n):
        p0=k*n+i;p1=k*n+(i+1)%n
        f.append((p0,p0+n,p1+n,p1))
mesh=bpy.data.meshes.new('Corrected crown surface')
mesh.from_pydata(v,[],f);mesh.update()
o=bpy.data.objects.new('Surface | uninterrupted shallow crown',mesh)
bpy.context.collection.objects.link(o)
o.data.materials.append(bpy.data.materials['Graphite | soft mineral powdercoat'])
for face in mesh.polygons:face.use_smooth=True
s.cycles.samples=12
s.render.resolution_x=768
s.render.resolution_y=512
s.render.filepath=str(p/'renders'/'07_crown_fix_test.png')
bpy.ops.render.render(write_still=True)
print('RENDERED',s.render.filepath,flush=True)
