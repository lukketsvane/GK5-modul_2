def make_louver(halfwidth, up, down, side, layer):
    import cadquery as cq
    import math

    w, t = float(halfwidth), 0.6
    s = -1.0 if side < 0 else 1.0
    edge = 0.8 * (1.0 + float(layer))
    sag = min(12.0, max(8.0, 0.21 * w))
    radius = ((0.994 * w) ** 2 + sag ** 2) / (2.0 * sag)
    limit = math.asin(0.994)
    rows = []

    for i in range(129):
        a = limit * (i - 64) / 64.0
        x = w * math.sin(a)
        h = math.sqrt(radius * radius - x * x)
        y = s * (edge + sag - x * x / (radius + h))
        xi, yi = x - t * x / radius, y - t * s * h / radius
        z0, z1 = -down * math.cos(a), up * math.cos(a)
        row = [(x, y, z0), (x, y, z1), (xi, yi, z1), (xi, yi, z0)]
        rows.append(row if s > 0 else row[::-1])

    def wire(points):
        return cq.Wire.makePolygon(points, close=True)

    try:
        solid = cq.Solid.makeLoft([wire(row) for row in rows], ruled=True)
        if not solid.isValid():
            raise ValueError("Invalid loft")
    except Exception:
        def face(points):
            return cq.Face.makeFromWires(wire(points))

        faces = [face(rows[0][::-1]), face(rows[-1])]
        for left, right in zip(rows, rows[1:]):
            for j in range(4):
                k = (j + 1) % 4
                faces.append(face([left[j], left[k], right[k]]))
                faces.append(face([left[j], right[k], right[j]]))
        solid = cq.Solid.makeSolid(cq.Shell.makeShell(faces))
        if not solid.isValid():
            raise ValueError("Invalid louver shell")

    reach = abs(edge) + sag + t + 2.0
    cutter = cq.Solid.makeCylinder(2.7, 2.0 * reach, (0, -reach, 0), (0, 1, 0))
    try:
        parts = solid.cut(cutter).Solids()
        if len(parts) == 1 and parts[0].isValid():
            return parts[0]
    except Exception:
        pass
    return solid