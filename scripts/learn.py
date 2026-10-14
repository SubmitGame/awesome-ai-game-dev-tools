#!/usr/bin/env python3
"""Build data/learn.json from data/learn_sources.json + video metadata, and fetch thumbnails.
Video metadata (channel, views, date) comes from the YouTube Data API when YOUTUBE_API_KEY is set,
otherwise the committed snapshot in data/youtube_raw.json is used as-is (shown with an 'as of' date)."""
import json, os, re, sys, time, io, requests
sys.path.insert(0, os.path.dirname(__file__))
import media
ROOT = media.ROOT; D = media.D
src = json.load(open(D("data/learn_sources.json")))
raw = json.load(open(D("data/youtube_raw.json")))
meta = raw.get("_meta", {"as_of": time.strftime("%Y-%m-%d"), "source": "YouTube video pages (yt-dlp)"})
ids = [i for s in src["subsections"] for i in s["items"] if isinstance(i, str)]
key = os.environ.get("YOUTUBE_API_KEY")
if key:
    r = requests.get("https://www.googleapis.com/youtube/v3/videos", params={"part": "snippet,statistics", "id": ",".join(ids), "key": key}, timeout=30)
    if r.ok:
        for it in r.json().get("items", []):
            v = raw.setdefault(it["id"], {}); s = it["snippet"]
            v.update(title=s["title"], channel=s["channelTitle"], published=s["publishedAt"][:10].replace("-", ""), views=int(it["statistics"].get("viewCount", 0)))
        meta = {"as_of": time.strftime("%Y-%m-%d"), "source": "YouTube Data API"}
        raw["_meta"] = meta; json.dump(raw, open(D("data/youtube_raw.json"), "w"), indent=1, ensure_ascii=False)
os.makedirs(D("screenshots/learn"), exist_ok=True)
out = []
for s in src["subsections"]:
    for it in s["items"]:
        if isinstance(it, str):
            v = raw[it]; fn = f"screenshots/learn/yt-{it}.jpg"
            if not os.path.exists(D(fn)):
                b = requests.get(f"https://i.ytimg.com/vi/{it}/hqdefault.jpg", timeout=20).content; open(D(fn), "wb").write(b)
            p = v["published"]
            out.append({"sub": s["key"], "kind": "Video", "title": v["title"], "url": f"https://youtu.be/{it}", "by": v["channel"],
                        "views": v["views"], "date": f"{p[:4]}-{p[4:6]}-{p[6:]}", "image": fn})
        else:
            fn = f"screenshots/learn/{re.sub(r'[^a-z0-9]+', '-', it['url'].lower().split('//')[1]).strip('-')[:70]}.jpg"
            if not os.path.exists(D(fn)):
                im = media.fetch(it["image"]) if it.get("image") else None
                if im: media.save(im, fn)
                else: media.capture(it.get("image_from") or it["url"], fn)
            out.append({"sub": s["key"], "kind": it["kind"], "title": it["title"], "url": it["url"], "by": it["by"], "desc": it["desc"], "image": fn if os.path.exists(D(fn)) else None})
doc = {"as_of": meta["as_of"], "source": meta["source"], "subsections": {s["key"]: s["name"] for s in src["subsections"]}, "items": out, "trend": src["trend"]}
json.dump(doc, open(D("data/learn.json"), "w"), indent=1, ensure_ascii=False)
print(len(out), "learn items;", sum(1 for x in out if x["kind"] == "Video"), "videos; missing images:", [x["title"] for x in out if not x["image"]])
if media._pw: media._pw.browser.close(); media._pw.stop()
