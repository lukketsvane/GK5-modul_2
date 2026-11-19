#!/usr/bin/env python3
"""Northern-lamper frå skulpturformene i slicerman, tenkte og teikna av gpt-6.2-astra (reasoning max).

Steg 1 (tenk): Astra les briefen, formspråket, dei tolv skulpturformene og tre forsøk skorne i slicerman,
og svarar med fire design som JSON.
Steg 2 (teikn N): Astra teiknar design N som speculative drawing (Töpfer-referansane sd_pNNN.png i
OpenAI Files) med image_generation: gpt-image-2.6-sunburst, quality max, 1920 x 1920.

Bruk:  python astra_nord.py tenk
       python astra_nord.py teikn 1-4 -j 2
"""
import argparse, base64, io, json, os, sys, threading, time, urllib.error, urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from PIL import Image

HER = Path(__file__).resolve().parent
UT = Path(os.environ.get("ASTRA_UT", HER / "ut"))
BASE = "https://api.openai.com/v1"
MODELL = "gpt-6.2-astra"
VERKTØY = {"type": "image_generation", "model": "gpt-image-2.6-sunburst", "quality": "max",
           "size": "1920x1920", "background": "opaque", "output_format": "png"}
REFS = "206 153 067 066 269 043"
USD = {"inn": 8, "inn_cache": 0.4, "ut": 40}
BILETE_USD = 0.46
LÅS = threading.Lock()


def nøkkel() -> str:
    k = os.environ.get("OPENAI_API_KEY")
    if not k and sys.platform == "win32":
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as n:
            k = winreg.QueryValueEx(n, "OPENAI_API_KEY")[0]
    return k


HODE = {"Authorization": f"Bearer {nøkkel()}", "Content-Type": "application/json"}


def api(sti, data=None):
    req = urllib.request.Request(BASE + sti, json.dumps(data).encode() if data else None, HODE)
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code}: {e.read().decode(errors='replace')[:1500]}")


def bilete(sti, breidd=1600):
    im = Image.open(sti).convert("RGB")
    if im.width > breidd:
        im = im.resize((breidd, round(im.height * breidd / im.width)), Image.LANCZOS)
    b = io.BytesIO(); im.save(b, "JPEG", quality=88)
    return {"type": "input_image", "image_url": "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode(), "detail": "high"}


def køyr(innhald, verktøy=None, effort="max"):
    data = {"model": MODELL, "input": [{"role": "user", "content": innhald}], "reasoning": {"effort": effort},
            "background": True, "store": True}
    if verktøy:
        data["tools"] = [verktøy]; data["tool_choice"] = {"type": "image_generation"}
    svar = api("/responses", data)
    while svar["status"] in ("queued", "in_progress"):
        time.sleep(10)
        svar = api(f"/responses/{svar['id']}")
    if svar["status"] != "completed":
        raise RuntimeError(f"status {svar['status']}: {json.dumps(svar.get('error') or svar.get('incomplete_details'))}")
    u = svar.get("usage") or {}
    cache = (u.get("input_tokens_details") or {}).get("cached_tokens", 0)
    usd = ((u.get("input_tokens", 0) - cache) * USD["inn"] + cache * USD["inn_cache"] + u.get("output_tokens", 0) * USD["ut"]) / 1e6
    return svar, usd, (u.get("output_tokens_details") or {}).get("reasoning_tokens", 0)


def logg(m):
    with LÅS:
        with open(UT / "logg.txt", "a", encoding="utf-8") as f:
            f.write(m + "\n")
        print(m, flush=True)


TENK = """Du er Astra, industridesignar. Oppgåva er designbriefen frå Northern under, saman med formspråket vi har lese ut av Northern-sortimentet og dei viktigaste krava.

Vi lagar lampene i slicerman (slicer.iverfinne.no): ein kropp vert skoren i 3 mm plater som går i kvarandre med halvt-i-halvt-spor, og kjem ut som skjerefiler. Bilete 1 er dei tolv formene i appen si «skulptur»-liste (skulptur-01 til skulptur-12, nummerert). Bilete 2 er tre forsøk eg skar i slicerman i går: Sopp (frå 07), Skygge (frå 03) og Kapsel (frå 12), kvar i arbeid og stemning, der det loddrette gitteret skjermar lyskjelda. Dei held reglane i motoren, men eg trur ikkje dei er gode nok.

Les briefen nøye og svar på kvart punkt i han, også mjukt ansiktslys i digitale møte, samspelet med skjerm og kamera, og at lampa er enkel, kompakt, flyttbar og gjerne oppladbar. Lag fire design som er briljante svar på briefen. Kvart design skal ta utgangspunkt i éi eller fleire av dei tolv skulpturformene og kunne lagast i slicerman. Tenk fritt; du treng ikkje byggje vidare på forsøka mine.

Svar berre med JSON: [{"namn": "", "skulptur": ["skulptur-NN"], "ide": "", "korleis_skoren": "", "stemning": "", "arbeid": "", "handling": "", "kvifor": "", "teikning": ""}]. Skriv på nynorsk. «teikning» er kva ei tenkjande teikning (speculative drawing) av designet skal tenkje gjennom, figur for figur."""

TEIKN = """Du er teiknaren og designaren. Dei første bileta er sider frå Andreas Töpfer, «Speculative Drawing». Studer dei nøye før du teiknar: dette er tenkjande teikningar, ikkje illustrasjonar. Ein gjenstand glir over i eit omgrep, ei form vert eit diagram, omgrep vert små biomorfe kroppar. Streken er svart tusj, litt skjelvande og ujamn, fri hand, med enkle konturar, nesten utan skravur. Teikningane står spreidde på kvitt papir med mykje luft. Merknadene er handskrivne, laust plasserte ved figurane, med bokstavar (A, B, C) og ei handskriven legende, piler og strekar som peikar.

Det siste biletet er skulpturforma designet tek utgangspunkt i, slik ho ligg i slicerman.

Teikn designet under som éi side i den stilen. Lat teikninga tenkje: skulpturen glir over i plater, platene i lys, lyset i stemning og arbeid, handlinga i handa. Kall image_generation éin gong med ein presis prompt som skildrar sida: kvar figur, kvar han står, kvar merknad står og kva han peikar på.

Krav til sida:
- Kvadratisk side (1:1), kvitt papir, berre svart tusj. Ingen gråtonar, ingen fargar, ingen skuggelegging.
- Handskrivne merknader i STORE BOKSTAVAR på rett nynorsk med Æ, Ø og Å, korte og henta frå designet. Bokstavar som A, B, C til ei legende er lov. Inga engelsk, ingen sidetal, ingen namn eller ord frå referansesidene.
- Ikkje kopier motiv, figurar eller oppsett frå referansesidene; berre strek, handskrift og tenkjemåte.

Designet:
"""


def tenk(a):
    innhald = [{"type": "input_text", "text": TENK + "\n\n## Briefen\n" + Path(a.brief).read_text(encoding="utf-8")
                + "\n\n## Formspråket og krava\n" + Path(a.ramme).read_text(encoding="utf-8")}]
    innhald += [bilete(a.former), bilete(a.forsok)]
    svar, usd, tenkt = køyr(innhald)
    tekst = "".join(c.get("text", "") for o in svar["output"] if o["type"] == "message" for c in o["content"])
    (UT / "design.txt").write_text(tekst, encoding="utf-8")
    s = tekst[tekst.find("["): tekst.rfind("]") + 1]
    json.loads(s)
    (UT / "design.json").write_text(s, encoding="utf-8")
    logg(f"tenk: ok ~${usd:.2f} resonnering {tenkt} {svar['id']}")


def teikn(a):
    design = json.loads((UT / "design.json").read_text(encoding="utf-8"))
    ids = {f["filename"]: f["id"] for f in api("/files?purpose=vision")["data"]}
    fra, _, til = a.nr.partition("-")

    def ein(n):
        ut = UT / f"design-{n}.png"
        if ut.exists():
            return
        d = design[n - 1]
        try:
            innhald = [{"type": "input_text", "text": TEIKN + json.dumps(d, ensure_ascii=False, indent=1)}]
            innhald += [{"type": "input_image", "file_id": ids[f"sd_p{r}.png"], "detail": "high"} for r in REFS.split()]
            for s in d.get("skulptur", [])[:2]:
                nr = "".join(ch for ch in s if ch.isdigit())[-2:]
                innhald.append(bilete(Path(a.formmappe) / f"s{nr}.png", 900))
            svar, usd, tenkt = køyr(innhald, VERKTØY)
            b = [o for o in svar["output"] if o["type"] == "image_generation_call" and o.get("result")]
            if not b:
                raise RuntimeError("inga bilete i svaret")
            ut.write_bytes(base64.b64decode(b[0]["result"]))
            (UT / f"design-{n}.txt").write_text(b[0].get("revised_prompt") or "", encoding="utf-8")
            logg(f"design {n} {d['namn']}: ok ~${usd + BILETE_USD:.2f} resonnering {tenkt} {svar['id']}")
        except Exception as e:
            logg(f"design {n}: FEIL {e}")

    with ThreadPoolExecutor(a.j) as ex:
        list(ex.map(ein, range(int(fra), int(til or fra) + 1)))


p = argparse.ArgumentParser()
p.add_argument("steg", choices=["tenk", "teikn"])
p.add_argument("nr", nargs="?", default="1-4")
p.add_argument("-j", type=int, default=2)
p.add_argument("--brief"); p.add_argument("--ramme"); p.add_argument("--former"); p.add_argument("--forsok"); p.add_argument("--formmappe")
a = p.parse_args()
UT.mkdir(parents=True, exist_ok=True)
tenk(a) if a.steg == "tenk" else teikn(a)
