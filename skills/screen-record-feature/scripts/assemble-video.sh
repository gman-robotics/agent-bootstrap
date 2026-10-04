#!/usr/bin/env bash
# Join a Playwright run's per-page webm files into one MP4 in page-creation order.
#
#   assemble-video.sh <playwright-test-output-dir> <out.mp4> [partner-tab-seconds]
#
# Playwright writes one video per page: video.webm = first page (partner portal), video-1..N =
# later pages (client portal popups, OneNotary tab), in the order the pages were opened. The
# partner tab stays recorded but idle after the client popup opens, so trim it to roughly the
# moment the popup appeared (default 31s; check a frame first and adjust).
set -euo pipefail
DIR=${1:?test output dir}; OUT=${2:?out.mp4}; FIRST=${3:-31}
FF=${FFMPEG:-$(command -v ffmpeg || true)}   # set FFMPEG=/path/to/ffmpeg if it is not on PATH
[ -n "$FF" ] && [ -x "$FF" ] || { echo "ffmpeg not found (brew install ffmpeg, or set FFMPEG=...)"; exit 1; }

inputs=(-t "$FIRST" -i "$DIR/video.webm"); n=1
for i in $(seq 1 20); do
  [ -f "$DIR/video-$i.webm" ] || break
  inputs+=(-i "$DIR/video-$i.webm"); n=$((n+1))
done
filter=""; labels=""
for i in $(seq 0 $((n-1))); do
  filter+="[$i:v]scale=1280:800,setsar=1,fps=25[v$i];"; labels+="[v$i]"
done
filter+="${labels}concat=n=$n:v=1:a=0[v]"
mkdir -p "$(dirname "$OUT")"
"$FF" -v error -y "${inputs[@]}" -filter_complex "$filter" -map "[v]" \
  -c:v libx264 -pix_fmt yuv420p -crf 23 -preset medium -movflags +faststart "$OUT"
# `ffmpeg -i` with no output always exits 1 — probe via a helper that ignores that.
probe() { "$FF" -i "$1" 2>&1 || true; }
probe "$OUT" | grep -o "Duration: [0-9:.]*" || true
echo "wrote $OUT from $n segment(s)"

# Contact sheet for a quick visual check (8 frames evenly spaced) next to the MP4.
dur=$(probe "$OUT" | sed -n 's/.*Duration: \([0-9]*\):\([0-9]*\):\([0-9.]*\).*/\1 \2 \3/p' | awk '{print $1*3600+$2*60+$3}')
SHEET="${OUT%.mp4}-contact.png"; tmp=$(mktemp -d); args=(); k=0
for frac in 0.03 0.15 0.3 0.45 0.6 0.75 0.88 0.98; do
  t=$(awk -v d="$dur" -v f="$frac" 'BEGIN{printf "%.2f", d*f}')
  "$FF" -v error -y -ss "$t" -i "$OUT" -frames:v 1 -vf scale=480:-1 "$tmp/$k.png"
  args+=(-i "$tmp/$k.png"); k=$((k+1))
done
"$FF" -v error -y "${args[@]}" -filter_complex "[0][1][2][3]hstack=4[a];[4][5][6][7]hstack=4[b];[a][b]vstack" "$SHEET"
rm -rf "$tmp"
echo "contact sheet $SHEET (frames at 3/15/30/45/60/75/88/98% of ${dur}s)"
