**Select two end-mounted parallelograms, synchronized through the moving hood.** Put each linkage in a transverse vertical plane. The hood then rises 28 mm while walking sideways only 2.23 mm; it does not pitch, and the lower blade carries no mechanism load. Two vertical slides would eliminate the walk, but guides 460 mm apart need alignment and anti-racking hardware and do not reproduce the visible arms. A clamshell needs fewer parts but tilts the reflector and opens a wedge rather than a uniform light slot.

### Nominal layout

Dimensions in mm. Origin is the base centre at tabletop level; \(x\) is length, \(+y\) faces the work area, \(z\) is up. Base: \(420\times115\times16\). The fixed \(400\times125\) blade has its highest luminous rim at \(z=124\), with a nominal 10 mm concave sag. Two formed-metal uprights rise from the base top to \(z=171\); their feet bolt inside the base ends and their heads offset **outboard** of the shell tips. Separate inboard brackets on the uprights support the blade heat sink.

At each end use the following pivot centres, all axes parallel to \(x\). Set \(x=-231\) at the master end and \(+231\) at the follower. With \(b=\sqrt{45^2-14^2}=42.767\):

- Fixed lower and upper pivots: \(A=(x,-b,138)\), \(B=(x,-b,160)\).
- Moving lower and upper pivots: \(C=A+d,\ D=B+d\), where \(d=(0,45\cos\theta,45\sin\theta)\).
- Arms \(AC=BD=45.00\) centre-to-centre; both pivot pairs have **22.00 vertical spacing**. The nonrotating moving cheek joins \(C\) to \(D\). The hood is centred at \(x=0,\ y=D_y\), with its horizontal trim plane 10 mm below \(D\).

| Pose | Arm angle \(\theta\) | \(C_y=D_y\) | \(C_z/D_z\) | Hood trim \(z\) | Vertical rim gap |
|---|---:|---:|---:|---:|---:|
| Closed | \(-\arcsin(14/45)\) | 0 | 124 / 146 | 136 | 12 |
| Intermediate | 0° | 2.233 | 138 / 160 | 150 | 26 |
| Open | \(+\arcsin(14/45)\) | 0 | 152 / 174 | 164 | 40 |

Use a \(440\times155\) hood with 36 mm crown above trim. Its highest point is \(z=200\); its maximum \(+y\) extent is 79.73. Budget the guarded assembly at **\(482\times160\times200\)** nominal, within \(485\times175\times300\). The tabulated gaps are trim-to-rim dimensions, not minimum distances between every pair of parts.

### Load path, synchronization and restraint

Run a **rotating Ø12 × 2 wall aluminium torque tube** on axis \(D\) between the upper arms. Clamp each arm to a solid-plugged tube end. Around it, a separate **nonrotating Ø18 × 1.5 carrier tube** rides on two Ø15 OD plain bushes. Clamp the moving cheeks and three transverse shell saddles to that carrier. Thus lifting at either end drives both cranks, but neither synchronization torque nor pivot preload passes through the cosmetic shell. Provide radiused, trimmed exits and removable end shoes where the carrier emerges through the tapered hood tips.

Use 4 mm aluminium arms, Ø6 shoulder screws and flanged bushes at \(A,B,C\); retain on the shoulder, not against the rotating arm. Target 0.04–0.10 diametral running clearance. Jig-bore pivot spacings to ±0.05. Locate the carrier axially at the master only. At the follower allow ±0.75 axial float on the ground pins and use metal-sleeved elastomer ground eyes with ±0.35 radial accommodation. Align the follower head with both ends jigged at mid-stroke before tightening it. Axial float alone does **not** correct an in-plane spacing error. Check unloaded travel torque before installing the holding device.

Vacuum-form the 1.5 PETG hood with positive release draft; drill after trimming. Attach its inward-facing bonded tabs to the saddles with M3 screws, broad washers and compression sleeves. Locate one central tab; slot the others radially with ±1 mm travel for thermal growth. For 0.8 formed aluminium use riveted tabs instead. Printed PETG is suitable for saddles and bezels; use metal for pivot journals, stops and spring reactions.

### Stops, effort and guarding

Fit two locknutted M4 tangential stops against a tab at 32 mm radius on the master lower crank. Set with 12 and 40 mm gap gauges; use thin urethane snubbers immediately before metal backup contact. Do not stop travel against the diffuser or independently hard-stop both ends.

Assume effective lifted mass \(m=0.55\)–0.65 kg, including half the uniform arm masses. Gravity torque is \(mg(0.045)\cos\theta\), at most 0.287 N·m. Specify an opening-assist torsion spring at \(A\), nominal torque \(0.251-0.12\theta\) N·m (\(\theta\) in radians), plus an adjustable friction pack with **0.11 ± 0.02 N·m breakaway**. Calculated residual gravity/spring torque is under 0.061 N·m. Target under 6 N vertical operating force at the centre grip and no drift at any angle; weigh the assembly and set preload before accepting those figures.

Enclose each end linkage in a removable clear pod, inner wall at \(|x|=224\), outer face at 241. Cover the moving carrier aperture with an overlapping travelling escutcheon. Keep 2 mm nominal clearance to unrelated rigid parts, excluding designed bearings, washers and guards with controlled running gaps. Round both exposed blade and hood edges. The 12 mm closed slot is **not** evidence of finger safety; test access throughout travel, including behind the escutcheon. Guard or revise the stop if an accessible trapping point remains.

### Light engine and validation

Use one fixed 24 V, approximately 8 W warm-white strip on a removable aluminium rear-edge heat sink, facing into a white mixing cavity. The 1 mm milky PC upper leaf provides ambient light; a baffled forward/downward exit in the fixed tray supplies task light without relying on transmission through an opaque blade back. Dim electrically, independently of pose. Route the SELV lead through a grommeted base entry and hollow upright to a keyed service connector. Nothing electrical crosses a pivot.

- **CAD:** Model trimmed solids, screw heads, stops, guards and end shoes in CadQuery. Rotate arms about \(A,B\); translate the carrier and hood by \(d(\theta)-d(\theta_\text{closed})\). Sweep at 0.25° including exact endpoints. Use OCP `BRepExtrema_DistShapeShape` for gaps and boolean common volume for interference, excluding only intentional contacts. Refine near minima: a sampled gap can fall by up to \(v_{\rm rel}\Delta\theta/2\) between samples, using a conservative pairwise speed bound in mm/radian. Repeat with tolerance offsets, shell trim error and hot dimensions.
- **Bench:** Measure rim gaps at both ends and sides, skew under one-ended actuation, breakaway and drift before and after 10,000 cycles. Check pinch access with probes, not fingers. At full power measure desk illuminance on a \(300\times200\) patch centred 250 mm forward; target ≥300 lx average and no direct LED image from seated eye positions. Thermocouple the strip board, sink, PC and touch surfaces to steady state in both extreme poses.
- **Stability/service:** Use feet near \(x=\pm196,\ y=\pm51\) and start with 1.9 kg of low steel ballast. Test both poses on an incline and under a separate 5 N horizontal crown load in every direction. Verify the diffuser and LED tray can be removed from below with the hood supported, without disturbing pivot alignment.

**Status:** poses, swept hood extents and ideal torque estimates are calculated. Shell profile, mass, friction, guard packaging, photometry, temperatures and safety margins are design inputs or acceptance targets—not measured or certified results.