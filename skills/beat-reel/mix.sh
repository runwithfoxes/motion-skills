#!/bin/sh
# Master score.wav to about -14 LUFS with true peak under -1 dB, and lay it under the newest render.
#   ./mix.sh      (run after ../motion-by-numbers/render.sh on this folder)
set -e
cd "$(dirname "$0")"
v=$(ls renders/*-v*.mp4 | grep -v sound | sort -V | tail -1)
ffmpeg -v error -y -i score.wav -af "loudnorm=I=-14:TP=-1.5:LRA=7,volume=3.6dB,alimiter=limit=0.891:level=disabled,aresample=48000" -ac 2 renders/_score.wav
ffmpeg -v error -y -i "$v" -i renders/_score.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -t 15 "${v%.mp4}-sound.mp4"
ffmpeg -i "${v%.mp4}-sound.mp4" -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+(I:|Peak:)" | tail -2
echo "${v%.mp4}-sound.mp4"
