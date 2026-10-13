#!/usr/bin/env python3
"""Fetch real GitHub metadata (stars, push date, license, social preview) for every candidate via gh GraphQL -> data/enriched.json."""
import json, os, subprocess, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = lambda *p: os.path.join(ROOT, *p)
cands = {c["repo"].lower(): c for c in json.load(open(D("data/candidates.json")))}
for hint, repos in json.load(open(D("data/additions.json"))).items():
    for r in repos:
        c = cands.setdefault(r.lower(), {"repo": r, "sources": [], "hints": []})
        if "curated" not in c["sources"]: c["sources"].append("curated")
        c.setdefault("pin", hint)
        c["pin"] = hint
F = "nameWithOwner url description homepageUrl stargazerCount forkCount isArchived isFork pushedAt openGraphImageUrl usesCustomOpenGraphImage licenseInfo{spdxId} repositoryTopics(first:10){nodes{topic{name}}} defaultBranchRef{target{...on Commit{committedDate}}}"
keys, out = list(cands), {}
for i in range(0, len(keys), 40):
    chunk = keys[i:i+40]
    q = "{" + " ".join(f'r{j}: repository(owner:{json.dumps(cands[k]["repo"].split("/")[0])}, name:{json.dumps(cands[k]["repo"].split("/")[1])}){{{F}}}' for j, k in enumerate(chunk)) + "}"
    p = subprocess.run(["gh", "api", "graphql", "-f", f"query={q}"], capture_output=True, text=True)
    data = (json.loads(p.stdout or "{}").get("data") or {})
    for j, k in enumerate(chunk):
        g = data.get(f"r{j}")
        c = dict(cands[k])
        if g:
            c["github"] = {"repo": g["nameWithOwner"], "stars": g["stargazerCount"], "forks": g["forkCount"], "archived": g["isArchived"], "fork": g["isFork"],
              "pushed_at": g["pushedAt"], "last_commit": ((g.get("defaultBranchRef") or {}).get("target") or {}).get("committedDate"),
              "description": g["description"] or "", "homepage": g["homepageUrl"] or "", "license": (g["licenseInfo"] or {}).get("spdxId"),
              "og_image": g["openGraphImageUrl"] if g["usesCustomOpenGraphImage"] else None, "og_auto": g["openGraphImageUrl"],
              "topics": [n["topic"]["name"] for n in g["repositoryTopics"]["nodes"]]}
        else: c["github"] = None
        out[(g or {}).get("nameWithOwner", c["repo"]).lower()] = {**out.get((g or {}).get("nameWithOwner", c["repo"]).lower(), {}), **c}
json.dump(list(out.values()), open(D("data/enriched.json"), "w"), indent=1)
ok = [c for c in out.values() if c["github"]]
print(len(out), "enriched;", len(ok), "resolved;", sum(1 for c in ok if c["github"]["stars"] >= 100), ">=100 stars")
