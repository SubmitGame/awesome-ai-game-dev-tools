#!/usr/bin/env bash
# Download the source lists' READMEs into raw/ (candidates only; nothing is copied into the list).
set -euo pipefail
cd "$(dirname "$0")/.."; mkdir -p raw
for r in Yuan-ManX/ai-game-devtools simoninithomas/awesome-ai-tools-for-game-dev AgentsLoop/awesome-ai-game-maker Anil-matcha/awesome-ai-game-generation aviaryan/awesome-ai-games bowen-aigame/awesome-ai-game; do
  gh api "repos/$r/readme" -H "Accept: application/vnd.github.raw" > "raw/${r/\//_}.md" || echo "fetch failed: $r"
done
