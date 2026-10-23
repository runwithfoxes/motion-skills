#!/bin/sh
# Render the writing and lay it on the film.
#   ./compose.sh <film.mp4> <out name> [start second] [length] [white|yellow|orange]
# start and length are the part of the film the writing covers (T0 and DUR in build.py). The writing is white on
# black; a screen blend makes the black clear, and it is softened a little so it sits on the wall.
set -e
here="$(cd "$(dirname "$0")" && pwd)"; cd "$here"
film="$1"; name="$2"; t0="${3:-66.6}"; len="${4:-6.16}"; col="${5:-white}"
export HYPERFRAMES_NO_TELEMETRY=1 DO_NOT_TRACK=1 HYPERFRAMES_NO_UPDATE_CHECK=1 HYPERFRAMES_NO_AUTO_INSTALL=1 HYPERFRAMES_SKIP_SKILLS=1
[ -n "$HYPERFRAMES_BROWSER_PATH" ] || HYPERFRAMES_BROWSER_PATH="$(ls -d "$HOME"/Library/Caches/ms-playwright/chromium_headless_shell-*/chrome-headless-shell-*/chrome-headless-shell "$HOME"/.cache/ms-playwright/chromium_headless_shell-*/chrome-headless-shell-*/chrome-headless-shell 2>/dev/null | tail -1)"
[ -n "$HYPERFRAMES_BROWSER_PATH" ] && export HYPERFRAMES_BROWSER_PATH
hf="$here/node_modules/.bin/hyperframes"; [ -x "$hf" ] || hf="$(command -v hyperframes)"
[ -n "$hf" ] || { echo "install it first: npm i hyperframes@0.8.143 --ignore-scripts"; exit 1; }
mkdir -p renders
"$hf" render --output renders/_writing.mp4 --fps 24 --quality high
case "$col" in yellow) tint="colorchannelmixer=rr=1:gg=0.84:bb=0.12," ;; orange) tint="colorchannelmixer=rr=0.957:gg=0.459:bb=0.129," ;; *) tint="" ;; esac
ffmpeg -v error -y -ss "$t0" -t "$len" -i "$film" -i renders/_writing.mp4 -filter_complex \
  "[1:v]${tint}gblur=sigma=1.1,format=gbrp[w];[0:v]fps=24,format=gbrp[f];[f][w]blend=all_mode=screen:all_opacity=0.92,format=yuv420p[v]" \
  -map "[v]" -map 0:a? -c:v libx264 -crf 17 -c:a aac -shortest "renders/$name.mp4"
echo "renders/$name.mp4"
