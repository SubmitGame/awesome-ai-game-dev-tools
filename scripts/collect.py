#!/usr/bin/env python3
"""Extract GitHub repo candidates (with a section hint from the source heading) from raw/*.md into data/candidates.json."""
import re, json, os, glob
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HINT = [(r"reverse|decomp|ghidra|ida\b", "reverse"), (r"mashup|crossover|mod", "mashups"),
 (r"agent|mcp|llm|tool\b|skill", "agents"), (r"world model|game \(|generation|prompt-to-game|generator|pcg|level", "gamegen"),
 (r"code|engine|librar", "code"), (r"image|visual|vlm|sprite|texture|2d|pixel", "art"),
 (r"3d|model|avatar|animation|shader|mocap|video", "3d"), (r"audio|music|voice|speech|sfx|sound|singing", "audio"),
 (r"npc|dialog|story|narrative|conversation|roleplay", "npc"), (r"analytic|test|qa|benchmark|dataset", "qa"),
 (r"game|remake|original|showcase|built with|example", "showcase")]
SKIP = {"sponsors", "topics", "features", "settings", "orgs", "apps", "marketplace", "collections", "about", "login", "site", "readme"}
out = {}
for f in sorted(glob.glob(os.path.join(ROOT, "raw", "*.md"))):
    src = os.path.basename(f)[:-3].replace("_", "/", 1)
    head = ""
    for line in open(f, errors="ignore"):
        if line.lstrip().startswith("#"): head = line.strip("# \n").lower()
        for o, n in re.findall(r"github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)", line):
            n = re.sub(r"\.git$", "", n).rstrip(".")
            if o.lower() in SKIP or n.lower() in ("issues", "pulls"): continue
            k = f"{o}/{n}"
            hint = next((h for p, h in HINT if re.search(p, head)), "")
            e = out.setdefault(k.lower(), {"repo": k, "sources": [], "hints": []})
            if src not in e["sources"]: e["sources"].append(src)
            if hint and hint not in e["hints"]: e["hints"].append(hint)
json.dump(list(out.values()), open(os.path.join(ROOT, "data", "candidates.json"), "w"), indent=1)
print(len(out), "candidates")
