import json, re, base64, urllib.request, datetime as dt
from yt import api
import os
CFG=json.load(open(os.path.join(os.path.dirname(__file__),'..','config.json'),encoding='utf-8'))
now = dt.datetime.now(dt.timezone.utc)
def iso_dur(s):
    m = re.match(r'P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', s or '')
    d,h,mi,se = [int(x or 0) for x in m.groups()] if m else (0,0,0,0)
    return d*86400+h*3600+mi*60+se
def thumb(vid):
    try:
        with urllib.request.urlopen(f"https://i.ytimg.com/vi/{vid}/mqdefault.jpg", timeout=10) as r:
            return "data:image/jpeg;base64,"+base64.b64encode(r.read()).decode()
    except Exception: return ""
def vids(ids):
    out=[]
    for k in range(0,len(ids),50):
        out+=api('videos',part='snippet,statistics,contentDetails',id=','.join(ids[k:k+50]),maxResults=50).get('items',[])
    return out
def chans(ids):
    out={}
    for k in range(0,len(ids),50):
        for c in api('channels',part='snippet,statistics',id=','.join(ids[k:k+50]),maxResults=50).get('items',[]):
            out[c['id']]=c
    return out
def norm(v, cats, subs):
    s=v['snippet']; st=v.get('statistics',{})
    pub=dt.datetime.fromisoformat(s['publishedAt'].replace('Z','+00:00'))
    hrs=max(1,(now-pub).total_seconds()/3600); views=int(st.get('viewCount',0))
    dur=iso_dur(v['contentDetails'].get('duration'))
    sc=subs.get(s['channelId'])
    return dict(id=v['id'],t=s['title'],c=s['channelTitle'],cid=s['channelId'],views=views,
        likes=int(st.get('likeCount',0) or 0),com=int(st.get('commentCount',0) or 0),
        vph=round(views/hrs),h=round(hrs),dur=dur,f='short' if dur and dur<=180 else 'video',
        cat=cats.get(s.get('categoryId'),'Otros'),subs=sc,img=thumb(v['id']))
data={"updated":now.isoformat(),"trends":{},"niche":{}}
allc=[]
for cc in ("ES","US"):
    cats={c['id']:c['snippet']['title'] for c in api('videoCategories',part='snippet',regionCode=cc,hl='es_ES')['items']}
    items=api('videos',part='snippet,statistics,contentDetails',chart='mostPopular',regionCode=cc,maxResults=50,hl='es_ES')['items']
    data["trends"][cc]=(items,cats); allc+= [i['snippet']['channelId'] for i in items]
# --- tu canal ---
me=api('channels',part='snippet,statistics',forHandle=CFG['handle'])['items'][0]
data["me"]=dict(id=me['id'],name=me['snippet']['title'],handle=CFG['handle'],
   subs=int(me['statistics'].get('subscriberCount',0)),views=int(me['statistics'].get('viewCount',0)),videos=int(me['statistics'].get('videoCount',0)))
# --- canales parecidos ---
Q=CFG["channel_queries"]
hits={}
for q in Q:
    for it in api('search',part='snippet',type='channel',q=q,regionCode='ES',relevanceLanguage='es',maxResults=15)['items']:
        cid=it['snippet']['channelId']; hits[cid]=hits.get(cid,0)+1
cinfo=chans(list(hits))
KW=["estafa","timos","timador","fraude","ciberseg","hacker","seguridad","phishing","scam","engaño"]
sim=[]
for cid,c in cinfo.items():
    if cid==me['id']: continue
    st=c['statistics']; subs=int(st.get('subscriberCount',0)); vids_=int(st.get('videoCount',0))
    if subs<500 or vids_<3: continue
    txt=(c['snippet']['title']+' '+c['snippet'].get('description','')).lower()
    kw=sum(1 for k in KW if k in txt)
    if kw==0: continue
    score=min(99,round(45+hits[cid]*9+kw*7))
    th=c['snippet']['thumbnails'].get('default',{}).get('url','')
    img=""
    try:
        with urllib.request.urlopen(th,timeout=10) as r: img="data:image/jpeg;base64,"+base64.b64encode(r.read()).decode()
    except Exception: pass
    sim.append(dict(id=cid,n=c['snippet']['title'],h=c['snippet'].get('customUrl',''),subs=subs,views=int(st.get('viewCount',0)),
        videos=vids_,d=c['snippet'].get('description','')[:140],m=score,country=c['snippet'].get('country',''),img=img))
sim.sort(key=lambda x:(-x['m'],-x['subs']))
data["niche"]["channels"]=sim[:15]
# --- virales de tu tipo (últimos 30 días) ---
after=(now-dt.timedelta(days=30)).strftime('%Y-%m-%dT%H:%M:%SZ')
vid_ids=set()
for q,extra in CFG["video_queries"]:
    for it in api('search',part='snippet',type='video',q=q,order='viewCount',publishedAfter=after,relevanceLanguage='es',regionCode='ES',maxResults=20,**extra)['items']:
        vid_ids.add(it['id']['videoId'])
nv=vids(list(vid_ids))
data["niche_raw"]=nv
allc+=[v['snippet']['channelId'] for v in nv]
csubs={cid:int(c['statistics'].get('subscriberCount',0)) for cid,c in chans(list(set(allc))).items()}
for cc in ("ES","US"):
    items,cats=data["trends"][cc]
    data["trends"][cc]=[norm(v,cats,csubs) for v in items]
cats=dict((c['id'],c['snippet']['title']) for c in api('videoCategories',part='snippet',regionCode='ES',hl='es_ES')['items'])
nvn=[norm(v,cats,csubs) for v in nv]
for v in nvn: v['ratio']=round(v['views']/max(v['subs'] or 1,1),1)
import re as _re
NK=CFG["keywords"]
def ok(v):
    t=v['t'].lower()+' '
    if _re.search(r'[\u0600-\u06FF\u0900-\u097F\u4e00-\u9fff\u0400-\u04FF]', v['t']): return False
    if v['cat'] in ('Videojuegos','Música'): return False
    if _re.search(r'ção|ções|bancária|ã ', t) or (v['subs'] or 0) < 300: return False
    return any(k in t for k in NK)
nvn=[v for v in nvn if ok(v)]
nvn.sort(key=lambda v:-v['views'])
data["niche"]["videos"]=nvn[:24]
del data["niche_raw"]
json.dump(data,open('data.json','w',encoding='utf-8'),ensure_ascii=False)
print("ES",len(data["trends"]["ES"]),"US",len(data["trends"]["US"]),"similar",len(sim),"nicho",len(nvn))
