def make_scoop(halfwidth, up, down, side, layer, direction):
    import math
    import cadquery as cq

    L = 2.0 * halfwidth
    if L <= 0 or min(up, down) < 0 or up + down <= 0:
        raise ValueError("Invalid scoop dimensions")
    if direction not in (-1, 1) or side not in (-1, 1):
        raise ValueError("direction and side must be +1 or -1")

    sag = min(10.0, 0.16 * L)
    r = min(5.0, 0.09 * L, 0.25 * (up + down))
    y0 = side * (12.0 + 1.2 * layer)
    V = cq.Vector

    def profile(t, a, b):
        peak = a / (a + b)
        return (t / peak) ** a * ((1.0 - t) / (1.0 - peak)) ** b

    stations = [-0.99999 * r]
    stations += [-r * math.cos(math.pi * i / 24) for i in range(1, 25)]
    stations += [r + (0.999999 * L - r) * math.sin(math.pi * i / 128) ** 2
                 for i in range(1, 65)]

    wires = []
    for u in stations:
        t = max(0.0, u / L)
        ear = r * math.sqrt(max(0.0, 1.0 - (u / r) ** 2))
        hi = max(ear, up * profile(t, 0.84, 0.60))
        lo = -max(ear, down * profile(t, 1.02, 0.64))
        slope = 4.0 * sag / L * (1.0 - 2.0 * t)
        bow = 4.0 * sag * t * (1.0 - t) if u >= 0 else slope * u
        y = y0 + side * bow
        h = 0.30 * math.hypot(1.0, slope)
        x = direction * u
        wires.append(cq.Wire.makePolygon([
            V(x, y - h, lo), V(x, y + h, lo),
            V(x, y + h, hi), V(x, y - h, hi)
        ], close=True))

    sheet = cq.Solid.makeLoft(wires, ruled=True)
    reach = sag + r + 2.0
    bore = cq.Solid.makeCylinder(2.72, 2.0 * reach,
                                 V(0, y0 - reach, 0), V(0, 1, 0))
    return sheet.cut(bore).Solids()[0]