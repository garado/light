#!/usr/bin/env bash
set -euo pipefail

usage() {
    echo "Usage: $0 <dir> --artist <artist> --album <album>"
    exit 1
}

[ $# -lt 1 ] && usage

DIR="$1"; shift
ARTIST=""; ALBUM=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --artist) ARTIST="$2"; shift 2 ;;
        --album)  ALBUM="$2";  shift 2 ;;
        *) echo "Unknown option: $1"; usage ;;
    esac
done

[ -z "$ARTIST" ] || [ -z "$ALBUM" ] && usage

TMPFILE=$(mktemp --suffix=.mp3)
trap 'rm -f "$TMPFILE"' EXIT

LIST=$(mktemp)
trap 'rm -f "$LIST"' EXIT

find "$DIR" -maxdepth 1 -type f \( \
    -iname "*.mp3" -o -iname "*.flac" -o -iname "*.m4a" \
    -o -iname "*.wav" -o -iname "*.ogg" -o -iname "*.aac" \
\) | sort | while read -r f; do
    escaped="${f//\'/\'\\\'\'}"
    echo "file '$escaped'"
done > "$LIST"

[ -s "$LIST" ] || { echo "No audio files found in '$DIR'"; exit 1; }

N=$(wc -l < "$LIST")
echo "Concatenating $N tracks..."
ffmpeg -f concat -safe 0 -i "$LIST" -c:a libmp3lame -q:a 2 \
    -metadata title="$ALBUM" -metadata artist="$ARTIST" -metadata album="$ALBUM" \
    "$TMPFILE" -loglevel warning || exit 1
echo "Finished concatenating $N tracks"

SIZE=$(du -h "$TMPFILE" | cut -f1)
echo "Starting upload of $TMPFILE ($SIZE)..."
light music upload "$TMPFILE"

echo "Done: $ARTIST - $ALBUM"
