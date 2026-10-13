#!/usr/bin/env python3
"""Give every tool and featured item a thumbnail in screenshots/ (640px JPEG) and record it in data/media.json.
Order: custom social preview -> first good README image -> headless-Chrome capture of homepage/demo -> GitHub's generated social card.
Also checks each homepage once (status recorded) so it can be shown as a verified demo link. Usage: media.py [--missing-only]"""
import json, os, re, sys, io, subprocess
from urllib.parse import urljoin
import requests
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = lambda *p: os.path.join(ROOT, *p)
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) awesome-ai-game-dev-tools/1.0"}
SKIP = re.compile(r"shields\.io|badge|\.svg|logo|icon|discord|patreon|ko-fi|paypal|sponsor|button|avatar|star-history|starchart|contrib\.rocks|emoji|favicon|workflow|codecov|wechat|qrcode|trendshift|api\.star|visitor|hits\.|deepwiki|qr|wechat|group|dingtalk|dingding|feishu", re.I)
def fetch(u, minb=6000):
    try:
        r = requests.get(u, headers=UA, timeout=(10, 20), stream=True)
        if r.status_code != 200: return None
        buf = b""
        for ch in r.iter_content(65536):
            buf += ch
            if len(buf) > 25_000_000: break
        if len(buf) < minb: return None
        im = Image.open(io.BytesIO(buf)); im.seek(0); im = im.convert("RGB")
        return im if im.width >= 200 and 0.5 <= im.width / im.height <= 3.2 else None
    except Exception: return None
def save(im, fn):
    im.thumbnail((640, 640 * 3)); h = min(im.height, 480)
    im = im.crop((0, 0, im.width, h)); im.save(D(fn), "JPEG", quality=80, optimize=True, progressive=True); return fn
def readme_imgs(repo):
    p = subprocess.run(["gh", "api", f"repos/{repo}/readme"], capture_output=True, text=True, timeout=60)
    if p.returncode: return []
    base = json.loads(p.stdout).get("download_url") or ""
    md = subprocess.run(["gh", "api", f"repos/{repo}/readme", "-H", "Accept: application/vnd.github.raw"], capture_output=True, text=True, timeout=60).stdout
    out = []
    for u in re.findall(r"!\[[^\]]*\]\(\s*<?([^)\s>]+)", md) + re.findall(r"<img[^>]+src=[\"']([^\"']+)", md, re.I):
        u = re.sub(r"https://github\.com/([^/]+/[^/]+)/blob/", r"https://raw.githubusercontent.com/\1/", urljoin(base, u.strip()))
        if not SKIP.search(u) and u not in out: out.append(u)
    return out[:6]
_pw = None
def capture(url, fn):
    global _pw
    try:
        from playwright.sync_api import sync_playwright
        if _pw is None:
            _pw = sync_playwright().start()
            kw = {"executable_path": "/usr/bin/google-chrome"} if os.path.exists("/usr/bin/google-chrome") else {}
            _pw.browser = _pw.chromium.launch(**kw)
        pg = _pw.browser.new_page(viewport={"width": 1280, "height": 800}, user_agent=UA["User-Agent"])
        pg.set_default_timeout(30000); pg.goto(url, timeout=30000, wait_until="domcontentloaded"); pg.wait_for_timeout(3000)
        b = pg.screenshot(type="jpeg", quality=80); pg.close()
        im = Image.open(io.BytesIO(b)).convert("RGB")
        if len(set(im.resize((32, 20)).getdata())) < 6: return None  # blank page
        return save(im, fn)
    except Exception as ex:
        print("  capture failed", url, str(ex)[:80]); return None
def status(u):
    try: return requests.get(u, headers=UA, timeout=(10, 15), allow_redirects=True, stream=True).status_code
    except Exception: return 0
def main():
    only_missing = "--missing-only" in sys.argv
    os.makedirs(D("screenshots"), exist_ok=True)
    mp = D("data/media.json"); media = json.load(open(mp)) if os.path.exists(mp) else {}
    E = {}
    for e in json.load(open(D("data/enriched.json"))):
        if e.get("github"): E[e["github"]["repo"]] = e["github"]
    tools = json.load(open(D("data/tools.json")))["tools"]
    global SHOWCASE; SHOWCASE = {t["repo"] for t in tools if t["section"] == "showcase"}
    items = [(t["repo"], E[t["repo"]], None) for t in tools] + [(f["id"], None, f) for f in json.load(open(D("data/featured.json")))]
    for key, g, f in items:
        m = media.setdefault(key, {})
        if g and g.get("homepage") and "homepage_status" not in m: m["homepage_status"] = status(g["homepage"])
        if only_missing and m.get("screenshot") and os.path.exists(D(m["screenshot"])): continue
        fn = f"screenshots/{re.sub(r'[^a-z0-9]+', '-', key.lower()).strip('-')[:70]}.jpg"; got = None
        if f:
            if f.get("image") and (im := fetch(f["image"])): got = (save(im, fn), f["image"])
            elif f.get("capture") and capture(f["capture"], fn): got = (fn, "capture:" + f["capture"])
        else:
            if key in SHOWCASE and g.get("homepage") and capture(g["homepage"], fn): got = (fn, "capture:" + g["homepage"])  # playable games: show the game
            if not got and g.get("og_image") and (im := fetch(g["og_image"])): got = (save(im, fn), "social-preview")
            if not got:
                for u in readme_imgs(g["repo"]):
                    if (im := fetch(u)): got = (save(im, fn), u); break
            hp = g.get("homepage")
            if not got and hp and not re.search(r"github\.com|arxiv\.org|huggingface\.co/papers", hp) and 200 <= m.get("homepage_status", 0) < 400 and capture(hp, fn): got = (fn, "capture:" + hp)
            if not got and g.get("og_auto") and (im := fetch(g["og_auto"], 1000)): got = (save(im, fn), "github-social-card")
            if not got and capture(f"https://github.com/{g['repo']}", fn): got = (fn, "capture:repo-page")
        if got: m["screenshot"], m["source"] = got; print(key, "->", got[1][:90])
        else: print(key, "-> NO IMAGE")
        json.dump(media, open(mp, "w"), indent=1)
    if _pw: _pw.browser.close(); _pw.stop()
if __name__ == "__main__": main()
