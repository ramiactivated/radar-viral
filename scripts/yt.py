import os, json, urllib.request, urllib.parse
KEY = os.environ["YT_API_KEY"]
def api(path, **p):
    p["key"] = KEY
    u = f"https://www.googleapis.com/youtube/v3/{path}?" + urllib.parse.urlencode(p)
    with urllib.request.urlopen(u, timeout=30) as r:
        return json.load(r)
