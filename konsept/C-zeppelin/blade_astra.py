def blade(kind, sign):
    k = abs(kind)
    height = (65.0, 62.0, 55.0, 41.0, 22.0)[k]
    depth = (37.0, 35.0, 31.0, 24.0, 13.0)[k]
    span = 70.0 - 1.25 * k
    sections = []

    def section(z, left, right):
        reach, sag = (height, 6.0) if z >= 0.0 else (depth, 5.5)
        radius = (reach * reach + sag * sag) / (2.0 * sag)
        rise = z * z / (radius + math.sqrt(max(0.0, radius * radius - z * z)))
        y = sign * (24.0 + rise)
        front, back = y - SHEET / 2.0, y + SHEET / 2.0
        sections.append(cq.Wire.makePolygon([
            cq.Vector(left, front, z),
            cq.Vector(right, front, z),
            cq.Vector(right, back, z),
            cq.Vector(left, back, z)
        ], close=True))

    n = 24

    def fan_section(side, i):
        angle = (math.pi / 2.0) * i / n
        u = math.sin(angle)
        if side > 0:
            reach, width, sweep = height, span, 11.0
        else:
            reach, width, sweep = depth, span - 2.0, 7.5
        z = side * (8.0 + (reach - 8.0) * u)
        center = -12.0 + width / 2.0 + sweep * u
        half = max(0.04, width * math.cos(angle) / 2.0)
        section(z, center - half, center + half)

    for i in range(n, -1, -1):
        fan_section(-1, i)
    for z in (-7.75, -7.0, -5.0, -2.5, 0.0, 2.5, 5.0, 7.0, 7.75):
        section(z, -5.0, 5.0)
    for i in range(n + 1):
        fan_section(1, i)

    body = cq.Solid.makeLoft(sections, ruled=True)
    axis = cq.Vector(0, 1, 0)
    for z, radius in ((-7.0, 1.2), (0.0, 2.0), (7.0, 1.2)):
        bore = cq.Solid.makeCylinder(radius, 24.0, cq.Vector(0, sign * 24.0 - 12.0, z), axis)
        body = body.cut(bore)
    return body.clean().Solids()[0]