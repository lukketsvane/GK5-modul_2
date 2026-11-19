import base64
import io
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
LOG_DIR = ROOT / "kontroll"
LOG_DIR.mkdir(exist_ok=True)
LOG = LOG_DIR / "astra_agent.jsonl"
MODEL = "gpt-6.2-astra"
MAX_ROUNDS = 22
MAX_TOKENS = 135000
PYTHON = sys.executable
BLENDER = Path(r"C:\Program Files\Blender Foundation\Blender 5.3\blender.exe")

def log(kind, value):
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"time": time.strftime("%Y-%m-%d %H:%M:%S"), "kind": kind, "value": value}, ensure_ascii=False, default=str) + "\n")

def resolve(name, write=False):
    p = (ROOT / name).resolve()
    base = ROOT if write else REPO
    if not p.is_relative_to(base):
        raise ValueError("Utanfor tillaten GK5-område")
    if any(piece.lower() in (".git", ".env", ".codex", ".ssh", "node_modules") for piece in p.parts):
        raise ValueError("Sperra system- eller hemmelig fil")
    return p

def list_files(path="."):
    p = resolve(path)
    if not p.is_dir():
        return "Ikkje ei mappe"
    files = sorted(p.rglob("*"))
    out = []
    for x in files:
        if len(out) >= 250:
            break
        if ".git" in x.parts or "node_modules" in x.parts:
            continue
        out.append(str(x.relative_to(REPO)) + ("/" if x.is_dir() else " [" + str(x.stat().st_size) + " B]"))
    return "\n".join(out)[:21000]

def read_text(path):
    p = resolve(path)
    if p.suffix.lower() not in (".md", ".txt", ".py", ".json", ".csv", ".toml", ".html", ".ps1", ".yaml", ".yml", ".log", ".xml"):
        raise ValueError("Les berre tekstfiler; bruk CAD-skript til binære kjelder")
    return p.read_text(encoding="utf-8-sig", errors="replace")[:50000]

def write_text(path, content):
    p = resolve(path, True)
    if p.suffix.lower() not in (".md", ".txt", ".py", ".json", ".csv", ".scad", ".svg", ".ps1", ".yaml", ".yml", ".html", ".xml", ".bat"):
        raise ValueError("Bruk Python/CAD-skript til produksjon av binære filer")
    if p.name in ("AGENT_OPPDRAG.md", "astra_agent.py", "start_astra_api.ps1"):
        raise ValueError("Ikkje overskriv agentkontrollfilene")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return str(p.relative_to(ROOT)) + " (" + str(p.stat().st_size) + " B)"

def run_script(path, engine="python"):
    p = resolve(path, True)
    if p.suffix != ".py" or not p.is_file():
        raise ValueError("Skriptet må vere ei eksisterande .py-fil i RAUP")
    cmd = [PYTHON, str(p)] if engine == "python" else [str(BLENDER), "-b", "--python", str(p)]
    if engine not in ("python", "blender"):
        raise ValueError("Vel python eller blender")
    try:
        r = subprocess.run(cmd, cwd=str(ROOT), text=True, encoding="utf-8", errors="replace", stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=210)
        return json.dumps({"exit_code": r.returncode, "output": r.stdout[-14000:]}, ensure_ascii=False)
    except subprocess.TimeoutExpired as exc:
        return json.dumps({"error": "Køyring avbraut etter 210 sekund", "output": str(exc)}, ensure_ascii=False)

def image_part(path):
    p = resolve(path)
    try:
        from PIL import Image
        img = Image.open(p).convert("RGB")
        img.thumbnail((1152, 1152))
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=81)
        data = buf.getvalue()
    except ImportError:
        data = p.read_bytes()
    return {"type": "input_image", "image_url": "data:image/jpeg;base64," + base64.b64encode(data).decode("ascii"), "detail": "high"}

PARAM_STR = {"type": "string"}
TOOLS = [
    {"type": "function", "name": "list_files", "description": "List relevant GK5 and RAUP source and generated files recursively.", "parameters": {"type": "object", "properties": {"path": PARAM_STR}, "required": ["path"], "additionalProperties": False}},
    {"type": "function", "name": "read_text", "description": "Read a text document or code file in the GK5 repository. Relative paths are resolved from RAUP.", "parameters": {"type": "object", "properties": {"path": PARAM_STR}, "required": ["path"], "additionalProperties": False}},
    {"type": "function", "name": "write_text", "description": "Write a file only within RAUP. Use for actual parametric CAD code and concise docs.", "parameters": {"type": "object", "properties": {"path": PARAM_STR, "content": PARAM_STR}, "required": ["path", "content"], "additionalProperties": False}},
    {"type": "function", "name": "run_script", "description": "Execute an existing Python script within RAUP using installed CadQuery/OCP, or Blender 5.3 Python. Capture exit status and output. Script must create and validate real files in RAUP.", "parameters": {"type": "object", "properties": {"path": PARAM_STR, "engine": {"type": "string", "enum": ["python", "blender"]}}, "required": ["path", "engine"], "additionalProperties": False}}
]

FUNCTIONS = {"list_files": list_files, "read_text": read_text, "write_text": write_text, "run_script": run_script}

def api(payload):
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key:
        raise RuntimeError("OPENAI_API_KEY manglar")
    request = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(request, timeout=280) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError("HTTP " + str(exc.code) + ": " + body[:1700]) from None

def run():
    brief = (ROOT / "AGENT_OPPDRAG.md").read_text(encoding="utf-8")
    directions = ("Du er Astra 6.2, ein CAD- og produksjonsingeniør som utfører RAUP-oppdraget. "
                  "Les kjelder, undersøk original FBX i Blender, bygg reell parametrisk CadQuery/OCP B-rep, "
                  "eksporter STEP/STL/DXF, valider og iterer. Ikkje nøg deg med plan. "
                  "Køyr reelle script i workspace og rett eventuelle feil. "
                  "Behald berre RAUP som skriveområde, ikkje generer med betalte Tripo-funksjonar, "
                  "ikkje bruk ny AI-genererte bilete som dokumentasjon på CAD. "
                  "Du har allereie tilgang til CadQuery/OCP, ezdxf, numpy og Blender. "
                  "Merk uavklara materialdata, faktisk lys, termiske målingar og tryggleik tydeleg. "
                  "Ver kort i tekst og omfattande i faktisk geometri. "
                  "Når du er ferdig, rapporter filene og utførte verifikasjonar.\n\n"
                  + brief + "\n\nTripo sin delte prosjekt-URL er "
                  + "https://studio.tripo3d.ai/canvas/share/01a1f071-f9dc-7b9f-adce-f2430908441a "
                  + "men berre originalfilene lokalt er verifiserte.")
    refs = [
        "referanse/cad_visning_1.jpeg",
        "referanse/cad_visning_2.jpeg",
        "referanse/cad_visning_3.jpeg",
        "render/01_hero.png",
        "render/04_back.png"
    ]
    content = [{"type": "input_text", "text": directions}]
    for name in refs:
        if (ROOT / name).exists():
            content.append({"type": "input_text", "text": "Referanse: " + name})
            content.append(image_part(name))
    inputs = [{"role": "user", "content": content}]
    previous = None
    total_tokens = 0
    last_call = None
    for step in range(1, MAX_ROUNDS + 1):
        payload = {"model": MODEL, "reasoning": {"effort": "max"}, "max_output_tokens": 13000, "store": True, "tools": TOOLS, "input": inputs}
        if previous:
            payload["previous_response_id"] = previous
        print("Astra steg", step, "start", flush=True)
        answer = api(payload)
        previous = answer.get("id")
        usage = answer.get("usage", {})
        total_tokens += usage.get("total_tokens", 0)
        calls = [x for x in answer.get("output", []) if x.get("type") == "function_call"]
        messages = [p.get("text", "") for o in answer.get("output", []) for p in o.get("content", []) if p.get("type") == "output_text"]
        log("response", {"step": step, "id": previous, "status": answer.get("status"), "usage": usage, "calls": [c.get("name") for c in calls], "text": "\n".join(messages)[:12000]})
        print("Astra steg", step, "status", answer.get("status"), "calls", len(calls), "tokens", total_tokens, flush=True)
        if total_tokens > MAX_TOKENS:
            log("limit", "Token cap nådd: " + str(total_tokens))
            break
        if not calls:
            if messages:
                (LOG_DIR / "astra_svar.md").write_text("\n".join(messages), encoding="utf-8")
                break
            inputs = [{"role": "user", "content": "Fortset med konkrete CAD-verktøykall og filproduksjon."}]
            continue
        outputs = []
        for c in calls:
            name = c.get("name")
            args = json.loads(c.get("arguments", "{}"))
            try:
                if name not in FUNCTIONS:
                    result = "Ukjent funksjon"
                else:
                    result = FUNCTIONS[name](**args)
                status = "ok"
            except Exception as exc:
                result = type(exc).__name__ + ": " + str(exc)
                status = "error"
            log("tool", {"step": step, "name": name, "args": {k: (v[:180] + "..." if isinstance(v, str) and len(v) > 180 else v) for k, v in args.items()}, "status": status, "result": result[:4000]})
            outputs.append({"type": "function_call_output", "call_id": c["call_id"], "output": str(result)[:30000]})
            print(" ", name, status, str(result)[:160], flush=True)
        inputs = outputs
        last_call = calls[-1].get("name")
    else:
        log("limit", "Maksimum rundar nådd")
    print("Astra avslutta; sjå kontroll/astra_agent.jsonl", flush=True)

if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        log("fatal", type(e).__name__ + ": " + str(e))
        print("Agentfeil:", type(e).__name__, str(e)[:1200], file=sys.stderr, flush=True)
        raise
