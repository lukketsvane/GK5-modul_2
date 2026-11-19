import argparse, base64, json, mimetypes, os, re, sys, time, urllib.error, urllib.request

API = "https://api.openai.com/v1"
H = {"Authorization": "Bearer " + os.environ["OPENAI_API_KEY"], "Content-Type": "application/json"}


def call(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(API + path, data, H, method=method)
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"HTTP {e.code}: {e.read().decode(errors='replace')[:3000]}")


def start(a):
    text = open(a.prompt[0], encoding="utf-8").read()
    for p in a.prompt[1:]:
        text += f"\n\n=== {os.path.basename(p)} ===\n" + open(p, encoding="utf-8-sig").read()
    content = [{"type": "input_text", "text": text}]
    for p in a.image:
        mime = mimetypes.guess_type(p)[0] or "image/png"
        b64 = base64.b64encode(open(p, "rb").read()).decode()
        content.append({"type": "input_image", "image_url": f"data:{mime};base64,{b64}", "detail": "high"})
    body = {"model": a.model, "reasoning": {"effort": a.effort}, "background": True,
            "max_output_tokens": 128000, "input": [{"role": "user", "content": content}]}
    if a.prev:
        body["previous_response_id"] = a.prev
    r = call("POST", "/responses", body)
    open(a.out + ".id", "w").write(r["id"])
    print(r["id"], r["status"])


def poll(a):
    rid = open(a.out + ".id").read().strip()
    t0 = time.time()
    while True:
        r = call("GET", f"/responses/{rid}")
        if r["status"] not in ("queued", "in_progress") or time.time() - t0 > a.wait:
            break
        time.sleep(10)
    print("status:", r["status"], r.get("incomplete_details") or "", r.get("error") or "")
    if r["status"] in ("queued", "in_progress"):
        return
    text = "".join(c.get("text", "") for o in r.get("output", []) if o.get("type") == "message"
                   for c in o.get("content", []))
    open(a.out + ".txt", "w", encoding="utf-8").write(text)
    blocks = re.findall(r"```(?:python|py)?[ \t]*\r?\n(.*?)```", text, re.S)
    code = max(blocks, key=len) if blocks else text
    open(a.out + ".py", "w", encoding="utf-8").write(code)
    u = r.get("usage") or {}
    cached = (u.get("input_tokens_details") or {}).get("cached_tokens", 0)
    reasoning = (u.get("output_tokens_details") or {}).get("reasoning_tokens", 0)
    cost = (u.get("input_tokens", 0) - cached) * 8e-6 + cached * 0.4e-6 + u.get("output_tokens", 0) * 40e-6
    print(f"tokens in={u.get('input_tokens')} cached={cached} out={u.get('output_tokens')} "
          f"reasoning={reasoning} cost=${cost:.2f}")
    print("code lines:", code.count("\n") + 1, "| chars outside code:", len(text) - len(code))


p = argparse.ArgumentParser()
s = p.add_subparsers(dest="cmd", required=True)
a1 = s.add_parser("start")
a1.add_argument("prompt", nargs="+")
a1.add_argument("--out", required=True)
a1.add_argument("-i", "--image", action="append", default=[])
a1.add_argument("--prev")
a1.add_argument("--effort", default="max")
a1.add_argument("--model", default="gpt-6.2-astra")
a2 = s.add_parser("poll")
a2.add_argument("--out", required=True)
a2.add_argument("--wait", type=int, default=100)
a = p.parse_args()
start(a) if a.cmd == "start" else poll(a)
