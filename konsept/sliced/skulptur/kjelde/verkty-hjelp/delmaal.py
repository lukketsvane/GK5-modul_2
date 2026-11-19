import zipfile, re, sys
z = zipfile.ZipFile(sys.argv[1])
for f in z.namelist():
    if not f.endswith('.model'):
        continue
    m = z.read(f).decode()
    for n, b in re.findall(r'<object id="\d+"[^>]*?name="([^"]*)"[^>]*>(.*?)</object>', m, re.S):
        V = [tuple(map(float, v)) for v in re.findall(r'<vertex x="([-\d.e]+)" y="([-\d.e]+)" z="([-\d.e]+)"', b)]
        if V:
            print(n, ' x '.join(f'{max(c) - min(c):.0f}' for c in zip(*V)))
