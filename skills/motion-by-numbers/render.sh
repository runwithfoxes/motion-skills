#!/bin/sh
# Render one composition folder to MP4 with HyperFrames, then cut the QA pictures.
#   ./render.sh my-film            (expects my-film/index.html; hyperframes installed in this folder or on PATH)
# The exports turn off usage reporting, update checks and auto-installs. Never run `hyperframes init`.
set -e
here="$(cd "$(dirname "$0")" && pwd)"
name="${1:?composition folder}"
export HYPERFRAMES_NO_TELEMETRY=1 DO_NOT_TRACK=1 HYPERFRAMES_NO_UPDATE_CHECK=1 HYPERFRAMES_NO_AUTO_INSTALL=1 HYPERFRAMES_SKIP_SKILLS=1
hf="$here/node_modules/.bin/hyperframes"; [ -x "$hf" ] || hf="$(command -v hyperframes)"
[ -n "$hf" ] || { echo "install it first: npm i hyperframes@0.8.143 --ignore-scripts"; exit 1; }
# use Playwright's headless Chrome if it is there (npx playwright install chromium-headless-shell)
[ -n "$HYPERFRAMES_BROWSER_PATH" ] || HYPERFRAMES_BROWSER_PATH="$(ls -d "$HOME"/Library/Caches/ms-playwright/chromium_headless_shell-*/chrome-headless-shell-*/chrome-headless-shell "$HOME"/.cache/ms-playwright/chromium_headless_shell-*/chrome-headless-shell-*/chrome-headless-shell 2>/dev/null | tail -1)"
[ -n "$HYPERFRAMES_BROWSER_PATH" ] && export HYPERFRAMES_BROWSER_PATH
fps="${FPS:-30}"
cd "$name"
base="$(basename "$(pwd)")"
mkdir -p renders qa
"$hf" lint
v=1; while [ -e "renders/$base-v$v.mp4" ]; do v=$((v+1)); done   # never overwrite a render
out="renders/$base-v$v.mp4"
"$hf" render --output "$out" --fps "$fps" --quality high
ffmpeg -y -v error -i "$out" -vf "fps=3,scale=360:-1,tile=6x4" -frames:v 1 qa/sheet.png
ffmpeg -y -v error -i "$out" -vf "select=eq(n\,0)" -frames:v 1 qa/first.png
ffmpeg -y -v error -sseof -0.1 -i "$out" -frames:v 1 -update 1 qa/last.png
echo "$out"
echo "now read qa/sheet.png, qa/first.png and qa/last.png, then look at every move frame by frame:"
echo "  ffmpeg -y -i $out -vf \"select='between(t,A,B)',scale=400:-1,tile=6x6\" -frames:v 1 qa/window.png"
