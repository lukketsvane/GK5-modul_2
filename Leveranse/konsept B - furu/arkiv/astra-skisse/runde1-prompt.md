You are a senior industrial designer and an expert Blender Python (bpy) developer. Write ONE complete Python script for Blender 5.3 that models, materials, lights and frames the table lamp described below as a precise, production-quality product model. Return only the script, in a single ```python code block, with minimal comments.

# Reference
The attached photo is the reference lamp, seen exactly side-on from the front against a black background. Match its proportions, profile, details, materials, lighting mood and camera framing as closely as possible, EXCEPT for the mandatory design changes below.

The designer's brief (Norwegian Nynorsk), verbatim:
«Den skal ha to parallelle rør ein bruker for å vinkle skjella, så den er meir eller mindre open, litt som ei kongle. Den skal ikkje ha to parallelle sett med skjel, men i staden ha seks samanhengande skjel totalt.»
Translation: "It shall have two parallel tubes that are used to angle the shells, so that it is more or less open, a bit like a pine cone. It shall not have two parallel sets of shells, but instead six continuous shells in total."

# Measured from the photo (Blender units = metres; values below in mm)
Axes: X = length of the body (left to right in the photo), Y = depth (camera at -Y), Z = up, table at Z = 0.
- Body: a horizontal spindle, 600 mm tip to tip, 163 mm tall. Both pointed tips lie on the "tip line" at Z = 155. The profile is asymmetric: a tall dome above the tip line (max 105 mm above it, peak near X = +20) and a shallower belly below it (max 58 mm below it, lowest near X = -30).
  Approximate side silhouette, X relative to body centre, Z relative to the tip line:
  top:    (-300,0) (-270,33) (-226,65) (-167,80) (-98,95) (21,105) (120,83) (194,63) (258,37) (300,0)
  bottom: (-300,0) (-251,-36) (-137,-53) (-28,-58) (70,-51) (194,-36) (268,-11) (300,0)
  The top view is not visible: give every cross-section a smooth oval whose width is about 0.9 x its height.
- Body underside at the centre: Z = 97. Top of the body: Z = 260.
- Pedestal: oval base plate 195 (X) x 130 (Y) x 11 mm thick with softly rounded edges; a turned, flared stem (trumpet/hyperbolic profile) from the plate to the body underside, ~57 mm at the waist (Z ~ 45), ~85 mm at the foot and ~81 mm at the top, with smooth fillets. A small round dimmer knob (diameter 10 mm, 3 mm proud) on the front of the stem at Z ~ 45, slightly right of centre.
- The reference has one visible straight brushed-steel rod (about 9 mm diameter) along the front on the tip line, with a small domed bolt head at every shell, ending at both tips.

# Mandatory design changes
1. Exactly SIX shells in total, forming ONE continuous series along the body. Not two mirrored or parallel sets, and not split into upper and lower halves: each shell is a single continuous piece of thin (2 mm) curved sheet that goes all the way around the cross-section, like one ring of scales of a pine cone. All six lean the same way and overlap like roof tiles toward one end. Largest in the middle, smaller toward the tips; the first and last shells form the two pointed tips. Give the shells the gently cupped, dish-like curvature seen in the reference.
2. Two parallel straight tubes (diameter 10 mm, brushed stainless) run the full length of the body on the tip line: Tube_Front on the front (the reference rod) and Tube_Back as its mirror on the back. They project ~8 mm past each tip and end in small domed caps. They are the fixed frame of the lamp, carried by a slim yoke that rises from the top of the stem through a gap in the shell series and clamps both tubes.
3. Each shell hangs on both tubes with one pivot pin per tube (domed bolt head visible on the outside of each tube, as in the reference). A shell's two pins are coaxial on a horizontal axis parallel to Y, so each shell tilts about that axis: the tubes are what the shells are angled on. Where a shell's edge does not reach a tube, extend it with a neat tab of the same sheet to the pin.
4. One parameter `open` (0..1) tilts all six shells together:
   - open = 0 (closed): every shell leans about 35 degrees from vertical, all in the same direction, overlapping like the scales of a closed pine cone so the body reads as a near-continuous scaled spindle with the reference silhouette.
   - open = 1 (open): every shell is close to upright (about 0-5 degrees); gaps open between them like an open pine cone and the glowing interior is revealed.
   - No intersections at any value of `open`: shell vs shell, shell vs tubes/pins/caps, shell vs yoke/stem, shell vs light. Choose shell spacing, pin positions, cup depth, tab shapes and the closed angle to guarantee this, and keep a clear gap for the yoke.
5. Light: warm white (2700 K) emission so that the inside of the shells and the gaps glow softly like the reference, with the brightest glow along the underside. The light hardware must never collide with the moving shells: for example a slim opal LED rod along the hinge-centre line through small clearance holes at each shell's pivot centre (where tilting does not sweep), and/or compact emitters on the yoke. Your choice, but justify it with the collision test.

# Rig
- An empty named LAMP_CTRL with a custom float property "open" (default 0.0, min 0, max 1, with UI min/max/soft limits set via id_properties_ui). Drive every shell's tilt from it using drivers with simple expressions only (no Python functions beyond Blender's simple-expression set), so they work with Python auto-run disabled.
- Put each shell's pivot on its pin axis (object origin on the axis, or parent to an empty there) so the tilt is a pure rotation about that axis.
- Clear names: Shell_1 .. Shell_6 (left to right), Tube_Front, Tube_Back, Pin_*, Cap_*, Yoke, Stem, Base, Dimmer_Knob, LED_*, Floor, Camera, Key/Fill/Rim lights.

# Build quality
- Pure bpy + bmesh + mathutils. No bpy.ops for geometry, no add-ons, no external files. It must run headless with: blender --background --factory-startup --python script.py -- C:/path/lampe.blend
- Start from an empty scene: remove all existing objects, meshes, curves, materials, lights, cameras and worlds.
- Smooth, high-quality, watertight surfaces with real thickness: shells 2 mm with slightly rounded edges (live Subdivision and Solidify/Bevel modifiers are fine), tubes as true cylinders, smooth shading. Real-world scale.
- Materials (Principled BSDF): shells, stem, base, yoke and knob in matte warm light-grey powder coat (sRGB ~ #B9B6AF, roughness ~ 0.5, very subtle fine-grain bump); tubes, pins and caps in brushed stainless (metallic 1, roughness ~ 0.28, anisotropy along the tube); LED emission 2700 K.
- Studio lighting on a pure black background like the photo: large soft key area light from upper front-left, soft fill from the right, rim light from behind, world colour black. A black, almost non-reflective Floor plane under the base so it stays grounded without visible horizon.
- Camera "Camera": side-on from the front (at -Y looking +Y), 16:9 at 1536 x 864, ~100 mm lens, ~9 degrees above horizontal so the top face of the base plate is just visible, framing the lamp at the same size and position as in the photo (lamp ~79 % of frame width, centred).
- Render: Cycles, CPU, 96 samples, OpenImageDenoise, AgX view transform with a medium-high contrast look. Set it up but do not render.
- Be defensive about API differences between Blender 4.2 and 5.3: wrap version-specific settings (socket names, colour-management looks, render settings) in try/except so the script never aborts on a renamed setting.

# Self-test and output
- At the end, for open in (0, 0.25, 0.5, 0.75, 1): set the property, update the depsgraph (view_layer.update() and frame_set), build world-space BVH trees from the evaluated meshes, and test every shell pair and every shell against tubes, pins, caps, yoke, stem and LED. Print one line per value: "SELFTEST open=0.50 OK" or "SELFTEST open=0.50 COLLISION Shell_3/Yoke ...". Then set open back to 0.
- Print "DIMS" lines with overall length, height, base size, shell pin X positions and the closed/open angles.
- If a .blend path is given after "--", save to it (bpy.ops.wm.save_as_mainfile is fine for saving).
