# Contributing

This list is **generated**: don't edit `README.md` by hand, it's rebuilt daily from `data/`.

## Add a tool
Add the repo (`owner/name`) to the right section in [`data/curation.json`](data/curation.json) and open a PR.
Sections: `reverse`, `modding`, `mashups`, `replacement`, `agents`, `gamegen`, `code`, `art`, `3d`, `audio`, `npc`, `qa`, `showcase`.

Optionally add a verified example (a game, mod or demo made with the tool) to [`data/examples.json`](data/examples.json):
```json
"owner/name": {"label": "What it is", "url": "https://..."}
```

**What qualifies**
- A public GitHub repo that's useful for making, modding or reverse engineering games with AI.
- **100+ stars** and a **push within the last year** (checked automatically; stale repos move to Inactive after 2 years).
- Never links to ROMs, ISOs, disc images or tools whose purpose is piracy or cheating in online games.

Stars, dates, licenses and thumbnails are filled in automatically.
