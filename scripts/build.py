import json, os
ROOT = os.path.join(os.path.dirname(__file__), "..")
d = json.load(open("data.json", encoding="utf-8"))
KW = ["estafa","fraude","ciberseg","hacker","seguridad","phishing","scam","engaño","timador"]
d["niche"]["channels"] = [c for c in d["niche"]["channels"] if any(k in (c["n"]+" "+c["d"]).lower() for k in KW)]
F = ("id","t","c","views","likes","com","vph","h","f","cat","subs","img")
keep = lambda v: {k: v[k] for k in F if k in v} | ({"ratio": v["ratio"]} if "ratio" in v else {})
out = {"updated": d["updated"], "me": d["me"],
       "trends": {cc: [keep(v) for v in d["trends"][cc]] for cc in ("ES", "US")},
       "channels": d["niche"]["channels"][:12], "niche": [keep(v) for v in d["niche"]["videos"][:24]]}
t = open(os.path.join(ROOT, "scripts", "template.html"), encoding="utf-8").read()
os.makedirs("_site", exist_ok=True)
html = t.replace("__DATA__", json.dumps(out, ensure_ascii=False).replace("</", "<\\/"))
html = html.replace("__GEMINI_KEY__", os.environ.get("GEMINI_API_KEY", "")).replace("__YT_WEB_KEY__", os.environ.get("YT_WEB_KEY", ""))
open("_site/index.html", "w", encoding="utf-8").write(html)
print("ok", len(html))
