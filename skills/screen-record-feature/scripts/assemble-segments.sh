#!/usr/bin/env bash
# Build one MP4 from explicit segments, in the order given.
#
#   assemble-segments.sh <out.mp4> <file.webm>[:start[:end]] ...
#     start/end are seconds within that file; omit end for "to the end", omit both for the whole file.
#
# Use this instead of assemble-video.sh when tabs interleave: Playwright records every page for its
# whole lifetime, so a parent tab that waits while a popup works shows a long frozen stretch. Find
# the boundaries with frame grabs, or with:
#   ffmpeg -i video.webm -vf "freezedetect=n=0.01:d=6" -map 0:v -f null - 2>&1 | grep freeze_
set -euo pipefail
OUT=${1:?out.mp4}; shift
[ $# -ge 1 ] || { echo "need at least one segment"; exit 1; }
FF=${FFMPEG:-$(command -v ffmpeg || true)}   # set FFMPEG=/path/to/ffmpeg if it is not on PATH
[ -n "$FF" ] && [ -x "$FF" ] || { echo "ffmpeg not found (brew install ffmpeg, or set FFMPEG=...)"; exit 1; }
probe() { "$FF" -i "$1" 2>&1 || true; }

inputs=(); filter=""; labels=""; i=0
for seg in "$@"; do
  IFS=: read -r file start end <<<"$seg"
  [ -f "$file" ] || { echo "missing $file"; exit 1; }
  opts=()
  [ -n "${start:-}" ] && opts+=(-ss "$start")
  [ -n "${end:-}" ] && opts+=(-to "$end")
  # ${opts[@]+...}: macOS bash 3.2 treats an empty array as unbound under `set -u`.
  inputs+=(${opts[@]+"${opts[@]}"} -i "$file")
  filter+="[$i:v]scale=1280:800,setsar=1,fps=25[v$i];"; labels+="[v$i]"; i=$((i+1))
done
filter+="${labels}concat=n=$i:v=1:a=0[v]"
mkdir -p "$(dirname "$OUT")"
"$FF" -v error -y "${inputs[@]}" -filter_complex "$filter" -map "[v]" \
  -c:v libx264 -pix_fmt yuv420p -crf 23 -preset medium -movflags +faststart "$OUT"
probe "$OUT" | grep -o "Duration: [0-9:.]*" || true
echo "wrote $OUT from $i segment(s)"

# 8-frame contact sheet next to the MP4 for a visual check.
dur=$(probe "$OUT" | sed -n 's/.*Duration: \([0-9]*\):\([0-9]*\):\([0-9.]*\).*/\1 \2 \3/p' | awk '{print $1*3600+$2*60+$3}')
SHEET="${OUT%.mp4}-contact.png"; tmp=$(mktemp -d); args=(); k=0
for frac in 0.03 0.15 0.3 0.45 0.6 0.75 0.88 0.98; do
  t=$(awk -v d="$dur" -v f="$frac" 'BEGIN{printf "%.2f", d*f}')
  "$FF" -v error -y -ss "$t" -i "$OUT" -frames:v 1 -vf scale=480:-1 "$tmp/$k.png"
  args+=(-i "$tmp/$k.png"); k=$((k+1))
done
"$FF" -v error -y "${args[@]}" -filter_complex "[0][1][2][3]hstack=4[a];[4][5][6][7]hstack=4[b];[a][b]vstack" "$SHEET"
rm -rf "$tmp"
echo "contact sheet $SHEET"
