#!/usr/bin/env python3
"""Generate README.md from data/tools.json + data/featured.json + data/media.json. Do not edit README.md by hand."""
import json, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = lambda *p: os.path.join(ROOT, *p)
doc = json.load(open(D("data/tools.json"))); T, S = doc["tools"], doc["sections"]
F = json.load(open(D("data/featured.json"))); media = json.load(open(D("data/media.json")))
SITE = "https://submitgame.github.io/awesome-ai-game-dev-tools/"
def esc(s): return (s or "").replace("|", "\\|").replace("\n", " ").strip()
def k(n): return f"{n/1000:.1f}k" if n >= 1000 else str(n)
def anchor(s): return re.sub(r"[^a-z0-9 -]", "", s.lower()).replace(" ", "-")
def example(e):
    if e.get("example"): return f"[{esc(e['example']['label'])}]({e['example']['url']})"
    m = media.get(e["repo"], {})
    if e.get("homepage") and 200 <= m.get("homepage_status", 0) < 400: return f"[site / demo]({e['homepage']})"
    return ""
def table(rows):
    L = ["| | Tool | ⭐ | Last push | What it does | Verified example |", "|---|---|---|---|---|---|"]
    for e in rows:
        img = f'<a href="{e["url"]}"><img src="{e["screenshot"]}" width="120" alt=""></a>' if e.get("screenshot") else ""
        badges = (" 🗄️" if e["archived"] else "")
        L.append(f"| {img} | **[{esc(e['repo'])}]({e['url']})**{badges} | {k(e['stars'])} | {e['pushed_at'][:10]} | {esc(e['description'])}{' <br>*Note: ' + esc(e['note']) + '*' if e.get('note') else ''} | {example(e)} |")
    return L + [""]
def feat_cells(items):
    L = ["<table><tr>"]
    for i, f in enumerate(items):
        img = media.get(f["id"], {}).get("screenshot")
        L.append(f'<td align="center" valign="top" width="33%"><a href="{f["url"]}"><img src="{img}" width="240" alt=""></a><br><b><a href="{f["url"]}">{f["title"]}</a></b>' + (f' <code>{f["label"]}</code>' if f.get("label") else "") + '<br><sub>{f["description"]}</sub>' + (f'<br><a href="{f["site"]}">website</a>' if f.get("site") else "") + "</td>")
        if i % 3 == 2 and i + 1 < len(items): L.append("</tr><tr>")
    return L + ["</tr></table>", ""]
act = [e for e in T if not e["inactive"]]; old = [e for e in T if e["inactive"]]
sec = lambda s: [e for e in act if e["section"] == s]
L = ["<!-- GENERATED FILE: edit data/ and run scripts/refresh, not this file -->",
"# Awesome AI Game Dev Tools [![Awesome](https://awesome.re/badge.svg)](https://awesome.re)", "",
"> Open-source AI tools for making games, and for **decompiling, remixing and mashing up the games you already own**. Every entry is a GitHub repo with **100+ stars and a push in the last year**, with real star counts pulled from the GitHub API and refreshed daily.", "",
f"**{doc['active']} active tools** · {doc['inactive']} inactive · updated {doc['generated_at'][:10]} · browse with tag filters on the **[website]({SITE})** · data in [`data/tools.json`](data/tools.json)", "",
"## ⭐ Featured", ""] + feat_cells([f for f in F if f["section"] == "top"]) + ["## Contents", "", "1. [Decompile, remix & mash up games](#1-decompile-remix--mash-up-games)"]
for sub, name in [("a", "Ground rules"), ("b", "AI reverse engineering"), ("c", "Decomp & recomp projects"), ("d", "Agent-driven modding"), ("e", "Mashups & remixes"), ("f", "AI replacement assets")]:
    L.append(f"   - [{sub}. {name}](#1{sub}-{anchor(name)})")
for s, v in S.items():
    if v["num"] != "1": L.append(f"{v['num']}. [{v['name']}](#{v['num']}-{anchor(v['name'])}) ({len(sec(s))})")
L += [f"11. [Inactive / unmaintained](#11-inactive--unmaintained) ({len(old)})", "- [Inclusion rules](#inclusion-rules) · [Sources](#sources) · [Contributing](#contributing) · [License](#license)", ""]
L += ["## 1. Decompile, remix & mash up games", "", "Point an AI agent at a game you own: read its binary, rebuild it from a decomp, mod it, mash it up with another game, or regenerate its assets.", "",
"### 1a. Ground rules", "",
"> [!IMPORTANT]",
"> - **Only use games you own.** Work from your own legally obtained copy.",
"> - **No ROMs, ISOs or disc images.** This list does not host, link to or help find them, and neither should your mod.",
"> - Don't ship the original game's files or decompiled code; ship code, patches, converters and your own assets.",
"> - Stay out of online games with anti-cheat, and don't bypass DRM or ownership checks.", "",
"### 1b. AI reverse engineering", "", S["reverse"]["description"], ""] + table(sec("reverse"))
L += ["### 1c. Decomp & recomp projects", "", "Hundreds of decompiled and recompiled games are tracked in our companion list, so they are not duplicated here.", ""] + feat_cells([f for f in F if f["section"] == "decomp"])
L += ["### 1d. Agent-driven modding", "", S["modding"]["description"], ""] + table(sec("modding"))
L += ["### 1e. Mashups & remixes", "", "Mods built by AI agents with universal-modder, plus a curated list of human-made crossovers.", ""] + feat_cells([f for f in F if f["section"] == "mashups"]) + (table(sec("mashups")) if sec("mashups") else [])
L += ["### 1f. AI replacement assets", "", S["replacement"]["description"], ""] + table(sec("replacement"))
for s, v in S.items():
    if v["num"] == "1": continue
    L += [f"## {v['num']}. {v['name']}", "", v["description"], ""] + table(sec(s))
    if s == "showcase": L += ["More playable AI-made games without public source live in [aviaryan/awesome-ai-games](https://github.com/aviaryan/awesome-ai-games) and [AgentsLoop/awesome-opus-5.5-games](https://github.com/AgentsLoop/awesome-opus-5.5-games).", ""]
L += ["## 11. Inactive / unmaintained", "", f"{len(old)} tools that are archived (🗄️) or have had no push since {doc['inactive_cutoff']} (2 years). They may still work, but don't expect fixes.", ""]
for s, v in S.items():
    rows = [e for e in old if e["section"] == s]
    if rows: L += [f"<details><summary><b>{v['name']}</b> ({len(rows)})</summary>", ""] + table(rows) + ["</details>", ""]
L += ["## Inclusion rules", "",
"- A public GitHub repo with **100+ stars** and a **push within the last year**. Stars and dates come from the GitHub API on every daily refresh; nothing is typed in by hand.",
"- Archived repos, or ones with no push for 2+ years, move to [Inactive](#11-inactive--unmaintained). Repos last pushed 1-2 years ago are left out.",
"- Each tool is paired with a **verified example** where one exists: a showcase, a game or mod built with it, or its live site/demo (the link is checked on refresh).",
"- Thumbnails come from the repo's social preview, an image in its README, or a headless-Chrome capture of its homepage, and are stored in [`screenshots/`](screenshots).", "",
"## Sources", "", "Candidates were gathered from these lists (thank you to their maintainers). Entries, descriptions and ratings here are our own:", "",
"- [Yuan-ManX/ai-game-devtools](https://github.com/Yuan-ManX/ai-game-devtools): the largest catalog of AI game dev tools; go there for papers and models we don't cover",
"- [simoninithomas/awesome-ai-tools-for-game-dev](https://github.com/simoninithomas/awesome-ai-tools-for-game-dev)",
"- [AgentsLoop/awesome-ai-game-maker](https://github.com/AgentsLoop/awesome-ai-game-maker) (the tool + verified example format)",
"- [Anil-matcha/awesome-ai-game-generation](https://github.com/Anil-matcha/awesome-ai-game-generation)",
"- [aviaryan/awesome-ai-games](https://github.com/aviaryan/awesome-ai-games)",
"- [bowen-aigame/awesome-ai-game](https://github.com/bowen-aigame/awesome-ai-game)",
"- [r/aigamedev: \"What is the current meta for developing games with AI?\"](https://www.reddit.com/r/aigamedev/comments/1wz016q/)",
"- [SubmitGame/awesome-decomp-games](https://github.com/SubmitGame/awesome-decomp-games) and [bailo167/awesome-game-mashups](https://github.com/bailo167/awesome-game-mashups)", "",
"## Contributing", "", "Add a repo to the right section in [`data/curation.json`](data/curation.json) and open a PR; [CONTRIBUTING.md](CONTRIBUTING.md) has the details. README.md and the site are generated.", "",
"## License", "", "The list and data are released under [CC0 1.0](LICENSE). The scripts and website code are under the [MIT License](LICENSE-CODE).", ""]
open(D("README.md"), "w").write("\n".join(L)); print("README.md written", len("\n".join(L)) // 1024, "KB")
