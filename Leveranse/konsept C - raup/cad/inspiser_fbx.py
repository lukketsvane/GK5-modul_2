"""Køyr med Blender i bakgrunn. Importerer berre lokal FBX; skriv ikkje .blend."""
import bpy, bmesh, json, hashlib
from pathlib import Path
import numpy as np
root=Path(__file__).resolve().parents[1]; out=root/'kontroll'; out.mkdir(exist_ok=True)
f=root/'modell'/'modern_table_lamp_3d_model.fbx'
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
res=bpy.ops.import_scene.fbx(filepath=str(f),global_scale=1.0,use_custom_normals=True)
report={'kjelde':f.name,'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'blender':bpy.app.version_string,'scene_units':[bpy.context.scene.unit_settings.system,bpy.context.scene.unit_settings.scale_length],'objekt':[]}; clouds={}; n=0
for o in bpy.context.scene.objects:
    d={'namn':o.name,'type':o.type,'parent':o.parent.name if o.parent else None,'matrix_world':[list(row) for row in o.matrix_world]}; report['objekt'].append(d)
    if o.type!='MESH': continue
    bm=bmesh.new(); bm.from_mesh(o.data); bm.transform(o.matrix_world); d['original_VEF']=[len(bm.verts),len(bm.edges),len(bm.faces)]; d['original_opne_kantar']=sum(e.is_boundary for e in bm.edges)
    xyz=np.array([v.co[:] for v in bm.verts]); lo=xyz.min(axis=0); hi=xyz.max(axis=0); d['bbox']=[lo.tolist(),hi.tolist()]; diag=float(np.linalg.norm(hi-lo)); d['sveise_eps']=max(1e-9,diag*1e-7); bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=d['sveise_eps']); bm.verts.index_update(); bm.faces.index_update()
    d['sveisa_delar']=[]; done=set()
    for v in bm.verts:
        if v.index in done:continue
        stack=[v]; done.add(v.index); vs=[]; es=set(); fs=set()
        while stack:
            q=stack.pop(); vs.append(q); fs.update(q.link_faces)
            for e in q.link_edges:
                es.add(e); p=e.other_vert(q)
                if p.index not in done: done.add(p.index); stack.append(p)
        a=np.array([p.co[:] for p in vs]); key='c%03d'%n; n+=1; stat={'id':key,'VEF':[len(vs),len(es),len(fs)],'ikkje_manifold_kantar':sum(not e.is_manifold for e in es),'bbox':[a.min(axis=0).tolist(),a.max(axis=0).tolist()]}; d['sveisa_delar'].append(stat)
        if len(vs)>5:
            clouds[key]=a; vid={p.index:i for i,p in enumerate(vs)}; tri=[]
            for face in fs:
                ix=[vid[p.index] for p in face.verts]; tri.extend((ix[0],ix[i],ix[i+1]) for i in range(1,len(ix)-1))
            clouds[key+'_tri']=np.array(tri,dtype=np.int32)
    bm.free()
np.savez_compressed(out/'fbx_malenett.npz',**clouds); (out/'fbx.json').write_text(json.dumps(report,indent=1),encoding='utf-8'); assert clouds and (out/'fbx_malenett.npz').stat().st_size>0
for d in report['objekt']:
    print(d['namn'],d['type'],d.get('original_VEF'),d.get('bbox'),str(sorted(d.get('sveisa_delar',[]),key=lambda c:-c['VEF'][0])[:12]))
print('Blender',report['blender'],'samanhengande øyar',n)
