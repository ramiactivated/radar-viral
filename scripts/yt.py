import os, json, time, urllib.request, urllib.parse, urllib.error
KEY = os.environ["YT_API_KEY"]
def api(path, **p):
    p["key"] = KEY
    u = f"https://www.googleapis.com/youtube/v3/{path}?" + urllib.parse.urlencode(p)
    for intento in range(6):
        try:
            with urllib.request.urlopen(u, timeout=30) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503) and intento < 5:
                time.sleep(5 * 2 ** intento)   # 5, 10, 20, 40, 80 s
                continue
            raise
