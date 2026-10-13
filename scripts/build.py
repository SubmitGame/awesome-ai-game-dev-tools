#!/usr/bin/env python3
"""Filter + section data/enriched.json using data/curation.json, merge data/media.json and data/examples.json -> data/tools.json.
Inclusion: 100+ GitHub stars and a push within the last year. Archived repos or repos with no push for 2+ years go to Inactive.
Repos in between (1-2 years) are left out until they become active again or cross the 2-year line."""
import json, os, re, time
from datetime import datetime, timezone
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = lambda *p: os.path.join(ROOT, *p)
def load(p, d):
    try: return json.load(open(D(p)))
    except FileNotFoundError: return d
SECTIONS = {
 "reverse":     ("1", "AI reverse engineering", "MCP servers and agent tools that let a coding agent read, label and explain binaries of games you own."),
 "modding":     ("1", "Agent-driven modding", "Agents that find a game's engine, read its code and build mods for it."),
 "mashups":     ("1", "Mashups & remixes", "Crossovers and remixes of existing games."),
 "replacement": ("1", "AI replacement assets", "Upscalers and remaster toolkits for making new textures, models and lighting for games you own."),
 "agents":      ("2", "Agents & MCP servers", "Coding agents, agent skills, multi-agent game studios and MCP bridges into Unity, Godot, Unreal and Blender."),
 "gamegen":     ("3", "Game generation & world models", "Interactive world models, playable video generation and procedural world/level generators."),
 "code":        ("4", "Code & engines", "Engines that agents write well for, plus LLM integrations for engines."),
 "art":         ("5", "Art", "Image, sprite, texture and UI generation and editing."),
 "3d":          ("6", "3D, animation & shaders", "Image/text-to-3D, motion generation, video and shader tools."),
 "audio":       ("7", "Audio", "Sound effects, music and voice."),
 "npc":         ("8", "NPCs & narrative", "LLM characters, generative agents, talking avatars and story tools."),
 "qa":          ("9", "Testing, QA & analytics", "Game-playing agents, RL environments and automated testing."),
 "showcase":    ("10", "Showcase", "Playable games made or remade with AI, with source code."),
}
TAGS = [(r"\bmcp\b|model context protocol", "MCP"), (r"unity", "Unity"), (r"godot", "Godot"), (r"unreal|\bue5\b", "Unreal"), (r"blender", "Blender"),
 (r"three\.?js|webgl|webgpu|browser", "Web"), (r"ghidra", "Ghidra"), (r"\bida\b", "IDA"), (r"world model", "World model"), (r"text-to-3d|image-to-3d|3d (asset|object|generation)|mesh", "3D gen"),
 (r"tts|text-to-speech|voice", "Voice"), (r"music|song", "Music"), (r"sound|audio|foley|sfx", "SFX"), (r"pixel|sprite", "Pixel art"), (r"texture|pbr|material", "Textures"),
 (r"animation|motion|mocap|pose", "Animation"), (r"video", "Video"), (r"npc|character|roleplay|role-play", "NPC"), (r"agent", "Agent"), (r"\brl\b|reinforcement", "RL"),
 (r"upscal|esrgan|super-resolution", "Upscaling"), (r"diffusion|text-to-image|image generation", "Image gen"), (r"local|offline|on-device|cpu", "Local")]
def age(iso): return (datetime.now(timezone.utc) - datetime.fromisoformat(iso.replace("Z", "+00:00"))).days / 365.25
def main():
    cur = load("data/curation.json", {}); media = load("data/media.json", {}); ex = load("data/examples.json", {})
    E = {}
    for e in load("data/enriched.json", []):
        E[e["repo"].lower()] = e
        if e.get("github"): E[e["github"]["repo"].lower()] = e
    out, dropped, seen = [], [], set()
    for sec, repos in cur.items():
        for r in repos:
            e = E.get(r.lower()); g = (e or {}).get("github")
            if not g: dropped.append({"repo": r, "reason": "not found on GitHub"}); continue
            if g["repo"].lower() in seen: continue
            seen.add(g["repo"].lower())
            if g["stars"] < 100: dropped.append({"repo": g["repo"], "stars": g["stars"], "reason": "<100 stars"}); continue
            a = age(g["pushed_at"])
            inactive = g["archived"] or a > 2
            if not inactive and a > 1: dropped.append({"repo": g["repo"], "pushed_at": g["pushed_at"], "reason": "no push in 1-2 years"}); continue
            text = " ".join([g["repo"], g["description"], " ".join(g["topics"])]).lower()
            tags = [t for p, t in TAGS if re.search(p, text)]
            m = media.get(g["repo"], {}); x = ex.get(g["repo"])
            out.append({"id": re.sub(r"[^a-z0-9]+", "-", g["repo"].lower()), "repo": g["repo"], "title": g["repo"].split("/")[1], "url": f"https://github.com/{g['repo']}",
              "section": sec, "description": g["description"][:240], "stars": g["stars"], "pushed_at": g["pushed_at"], "archived": g["archived"],
              "license": g["license"], "homepage": g["homepage"] or None, "tags": tags, "inactive": inactive, "sources": sorted(set(e["sources"])),
              "example": x, "screenshot": m.get("screenshot"), "screenshot_source": m.get("source")})
    order = list(SECTIONS)
    out.sort(key=lambda e: (e["inactive"], order.index(e["section"]), -e["stars"]))
    counts = {s: sum(1 for e in out if e["section"] == s and not e["inactive"]) for s in order}
    cutoff = time.strftime("%Y-%m-%d", time.gmtime(time.time() - 2 * 365.25 * 86400))
    doc = {"generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "inactive_cutoff": cutoff,
           "sections": {k: {"num": v[0], "name": v[1], "description": v[2]} for k, v in SECTIONS.items()},
           "counts": counts, "active": sum(counts.values()), "inactive": sum(1 for e in out if e["inactive"]), "tools": out}
    json.dump(doc, open(D("data/tools.json"), "w"), indent=1, ensure_ascii=False)
    json.dump(dropped, open(D("data/dropped.json"), "w"), indent=1)
    print("active", doc["active"], "inactive", doc["inactive"], "dropped", len(dropped), counts)
if __name__ == "__main__": main()
