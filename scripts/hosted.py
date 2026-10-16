#!/usr/bin/env python3
"""Thumbnails for hosted (closed-source) entries in data/hosted.json -> data/media.json key 'hosted:<url>'.
Hosted entries have no stars, are hand-curated and are not touched by the star/inactive rules or the daily refresh."""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(__file__)); import media
D = media.D; mp = D("data/media.json"); M = json.load(open(mp))
os.makedirs(D("screenshots/hosted"), exist_ok=True)
import time, requests
H = json.load(open(D("data/hosted.json")))
for e in H:  # live Hugging Face likes for open-weights entries
    if e.get("hf"):
        try:
            r = requests.get(f"https://huggingface.co/api/models/{e['hf']}", timeout=20)
            if r.ok and isinstance(r.json().get("likes"), int):
                e["signals"] = [{"text": f"{r.json()['likes']:,} likes on Hugging Face", "url": f"https://huggingface.co/{e['hf']}"}]; e["signal_as_of"] = time.strftime("%Y-%m-%d")
        except Exception as ex: print("HF fetch failed", e["hf"], ex)
json.dump(H, open(D("data/hosted.json"), "w"), indent=1, ensure_ascii=False)
for e in H:
    k = "hosted:" + e["url"]; fn = f"screenshots/hosted/{re.sub(r'[^a-z0-9]+', '-', e['url'].split('//')[1].lower()).strip('-')}.jpg"
    if M.get(k, {}).get("screenshot") and os.path.exists(D(M[k]["screenshot"])): continue
    if media.capture(e["url"], fn): M[k] = {"screenshot": fn, "source": "capture:" + e["url"]}; print(e["title"], "->", fn)
    else: print(e["title"], "-> NO IMAGE")
json.dump(M, open(mp, "w"), indent=1)
if media._pw: media._pw.browser.close(); media._pw.stop()
