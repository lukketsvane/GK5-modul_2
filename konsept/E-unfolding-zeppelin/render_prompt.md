Act as gpt-6.2-astra expert in CadQuery and VTK scientific render pipelines. Write one fully executable Python 3.13 script render.py which loads the ACTUAL geometry built by build.py in the same folder, uses no artificial image generation, and produces real studio product renders as PNG. Output code only with no fences, no comments, no docstrings, no additional explanation.

Existing build.py has:
- import build
- build.catalogue() returns dict name -> (cq.Solid, pigment_key, category, material)
- build.layout(t) returns (items, excluded_contact_pairs) with items dict instance_name -> (part_key, cq.Location, group); choose t=0 closed, 0.5 middle, 1 open
- build.PALETTE returns per-pigment RGBA values (0..1)
- pose from user ref: elongated one-piece matte ivory Zeppelin-like hood above a separate concave luminous lower dish, U-shaped base with TWO end posts, visible four-bar joints and torque tube.
- build.validate() already gave ok true at 9 samples, 21 unique parts, 63 instances.
- all manufacturing and geometry from cadquery 2.8, installed Python has vtk and PIL. Import code but do not call build.export_all on import.

Implement:
1. Use VTK (vtkPolyData vtkPoints vtkTriangle vtkPolyDataMapper vtkPolyDataNormals vtkActor) to triangulate REAL cq.Solid geometry at tolerance 0.7mm/angular 0.18 using cq.Solid.tessellate(0.7,0.18). Convert Vector coords to vtk points, faces with indices; apply cq.Location by using shape.moved(loc) BEFORE tessellation. Set scene colors according to build.PALETTE, use PBR-ish actor properties SetInterpolationToPhong, SetDiffuse 0.8, SetAmbient 0.15, SetSpecular 0.15, SetSpecularPower 35. For opal + light use warmer color and ambient 0.55, but no fake glowing shapes, retain actual solids.
2. Setup 1400x1000 VTK offscreen renderer with deliberate 3 area/studio lights and ambient plus offwhite/black background. Camera position approx (620,-690,345) facing focal (0,0,110), vertical view_up (0,0,1), and profile camera (0,-850,120). ResetCameraClippingRange, parallel projection, parallelScale approx 175. Fill 65-80% of frame, no cropped parts.
3. Save 6 high quality PNGs, render/closed_studio.png, middle_studio.png, open_studio.png (neutral warm-gray background RGB .92,.90,.86) and render/closed_black.png, middle_black.png, open_black.png (near-black pure background). Also side profile render/open_side.png. Use vtkWindowToImageFilter and vtkPNGWriter. No text, labels, collage, watermarks, or panels, one actual CAD model per image. Camera after render suitable.
4. Verify each image output exists and PIL inspect image pixels: foreground fraction >0.02, RGB variation >3%. Save render_validation.json with file name, resolution, meaningful pixel coverage. Print JSON summary. If VTK fails to render on Windows with offscreen, do NOT silently substitute a generated illustrative image. Raise meaningful error. Keep source standalone, runtime ideally <2 minutes by caching tessellated part geometries from build.catalogue() and transforming vtk actor via vtkTransform from cq.Location matrices instead of remeshing shapes every pose.
5. Restrict to this folder. No changes to build.py or other repo files.
6. Do not present these renders as photometric simulations; they are CAD material renders.

Ensure correct cq.Location transform handling for VTK from OCP gp_Trsf via loc.wrapped.Transformation().Value(i,j) or loc.toTuple as available. If not sure, simply use solid.moved(loc).tessellate(...) which is more reliable but slower. VTK actor pipeline SetUserMatrix optional. Keep render robust.