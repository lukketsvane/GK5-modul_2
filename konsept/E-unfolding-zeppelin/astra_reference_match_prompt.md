You are GPT-6.2 Astra, at the highest supported xhigh reasoning effort, acting as senior product CAD and Blender rendering engineer. Edit EXISTING concept E CAD to visually reproduce the exact supplied reference as closely as one view permits, using REAL CAD solids; do not create/generate/substitute any images, designs, fake light surfaces, or collage. The image is a 1536 x 1024 warm grey/ivory product rendering of a table lamp. The reference geometry is the design authority.

Reference front-side 3/4 appearance, carefully transcribed from original pixels:
- A single continuous smooth ivory opaque upper airship canopy, from image x≈150 to 1390, y≈155 crown to ~385 at tip; dramatically long, a little asymmetrically tapered, subtly cambered, warm matte ivory, no segmented ribs.
- A SINGLE separate luminous milky white shallow BOAT-SHAPED LOWER DISH or lens suspended below, tips at image x≈365 and 1160 near y≈415, while its broad lower rim visibly descends to y≈565 at the centre: deep smooth LONGITUDINAL downward drape across the span, not a one-pixel horizontal stripe. Large luminous concave front-facing surface, softly warm diffuse white, huge visible area, not a narrow glowing gap. Its lowest point sits much higher than tabletop but well below hood. Top lip hidden toward shell, lower edge clearly visible.
- Two almost-vertical squared pale end uprights from the shared base to top hinge regions; reference left post ~x335..405 and right ~x1160..1295. A single horizontal lower joining bar across x≈330..1250 close to tabletop, no long U-shaped feet sticking toward the camera. No central pedestal.
- Four short articulated pivot links total, two on each end, read as the natural load path, small warm-metal pivots; upper canopy lifted above static lens, maintaining approximately level attitude. Visible open slot between hood and lens, especially near right.
- The reference product camera sees a LONG projected length, gently from front at an elevated 3/4 angle, NOT a view down the length. Backdrop matte warm mid-grey/taupe, not almost-white washed-out stage. Soft 3000K emission concentrated on the exposed curved lower diffuser with believable bounce onto nearby supports.

Current faulty CAD render from existing build.py/render_blender.py: hood appears like narrow gray flat wing; lower diffuser a horizontal thin line, side links look oversized and copper, two long U-foot protrusions face camera. This is demonstrably NOT the reference.

Existing movement is the double-end 4-bar parallelogram. Preserve the nominal link endpoints and kinematics unless you can prove an alternative necessary; do NOT invent hinges or break correct mating constraints. Prior QA correctly says not production-ready. We are doing a visually verified CAD prototype revision, NOT claiming product release. Preserve original project directory and all other concepts.

Critical shape fix: build.leaf_blank() currently makes shallow transverse (across Y) sag but virtually NO LONGITUDINAL (along X) drape. Introduce the reference's substantial z drop toward x=0 on the forward visible lip of the diffuser, around 35-45 mm at midspan while its two end anchors retain ~z124. Build a real thin, manifold, vacuum-formable PC sheet as CadQuery solid, with complete end attachment points, smooth longitudinal curve and soft front-facing luminous portion. The fixed electronics and heat sink can remain near the upper rim at z≈123, with diffuser following below; do not create floating unsupported luminous panels. Where needed provide a subtle narrow rib/frame to carry the sheet, but avoid changing nominal end anchoring. Ensure light engine remains fixed, electrical wires do not cross pivots. Existing loft has x stations from -200..200, edge contours in YZ: preserve concept, adjust longitudinal envelope and front lip. Check collision vs hood over all poses; no intersection with plinth and posts.

Critical base fix: existing U footprint opens toward FRONT +Y, causing projecting feet. Reverse its U footprint so horizontal 25mm thick joiner is FRONT (+Y), with hidden rear support arms toward -Y, preserving the 420x115x16 envelope and original x/y bolt coordinates x±196, y≈-42.77. If that risks fixture placement, create a stable low continuous base bar and retain hidden support structure without changing outer bounds. Do not accidentally erase real support or screw holes.

Critical view fix: in render_blender.py move camera from diagonal end-on x=0.55,y=0.7,z=.33 toward front-dominant x≈0.12..0.22,y≈0.75,z≈0.30-0.38 looking at approx z0.11. Use 65mm orthographic product frame. The goal is visible longitudinal vertical lens curve matching supplied reference, with full length not severely foreshortened. Ensure real lens has brighter milky opal emission or convincingly lit transparent PC. Keep single seamless hood. Adjust studio world/background from washed-out to warm gray with enough contrast to perceive the luminance. Maintain black render too. Render only true CAD geometry.

Produce ONLY executable Python3 patch code, no markdown fences, comments, docstrings, or explanation. This patch executes from the E project root and surgically modifies build.py and render_blender.py. It MUST:
1. Save unmodified originals as build_before_reference_match.py and render_blender_before_reference_match.py if backups do not exist.
2. Modify only the required shapes, material/view props. Use safe exact string anchors / AST-function line replacements with assertions rather than broad rewriting.
3. Preserve all other parts and export API; ensure output passes compile() and import build.
4. Print concise JSON of edited files and expected differences. Do not run long renders in the patch.
5. Stay compatible with Python3.13 CadQuery2.8 and Blender5.3. Preserve existing script conventions and no new dependencies.

Below are COMPLETE CURRENT SOURCE FILES. Implement exact patch based on these, do not guess names.

=== BUILD.PY ===
{BUILD_SOURCE}
=== END BUILD ===

=== RENDER_BLENDER.PY ===
{RENDER_SOURCE}
=== END RENDER ===

=== EXISTING QA VERDICT ===
{QA_SOURCE}
=== END QA ===