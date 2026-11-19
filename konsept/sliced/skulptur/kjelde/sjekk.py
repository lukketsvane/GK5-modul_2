import json, os, sys, urllib.request
k = os.environ.get("OPENAI_API_KEY")
if not k and sys.platform == "win32":
    import winreg
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as n:
        k = winreg.QueryValueEx(n, "OPENAI_API_KEY")[0]
print("nøkkel:", bool(k))
H = {"Authorization": f"Bearer {k}"}
def get(p):
    with urllib.request.urlopen(urllib.request.Request("https://api.openai.com/v1" + p, headers=H), timeout=60) as r:
        return json.load(r)
f = get("/files?purpose=vision")["data"]
sd = sorted(x["filename"] for x in f if x["filename"].startswith("sd_p"))
print("sd-referansar:", len(sd), sd[:12])
m = get("/models")["data"]
img = sorted(((x.get("created", 0), x["id"]) for x in m if "image" in x["id"] or "astra" in x["id"]), reverse=True)
for c, i in img[:14]:
    print(c, i)
