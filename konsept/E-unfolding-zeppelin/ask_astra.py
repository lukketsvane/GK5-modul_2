import os, json, urllib.request, pathlib
folder = pathlib.Path(__file__).resolve().parent
brief = (folder / "design_prompt.txt").read_text(encoding="utf-8")
body = {"model":"gpt-6.2-astra","reasoning":{"effort":"xhigh"},"max_output_tokens":6500,"input":[{"role":"user","content":[{"type":"input_text","text":brief}]}]}
req=urllib.request.Request("https://api.openai.com/v1/responses",data=json.dumps(body).encode(),headers={"Authorization":"Bearer "+os.environ["OPENAI_API_KEY"],"Content-Type":"application/json"},method="POST")
try:
    with urllib.request.urlopen(req,timeout=180) as r: result=json.load(r)
    text="\n".join(p.get("text","") for o in result.get("output",[]) for p in o.get("content",[]) if p.get("type")=="output_text")
    (folder/"astra_6_2_review.md").write_text(text,encoding="utf-8")
    print("status=ok model="+result.get("model","")+" output_chars="+str(len(text))+" usage="+json.dumps(result.get("usage",{})))
    print(text[:12500])
except Exception as e:
    print("error="+type(e).__name__+" "+str(e)[:250])

