#!/usr/bin/env bash
# One-time setup in a fresh workspace: free voice engine (Kokoro) + its model files (from GitHub releases).
set -e
cd "$(dirname "$0")"
pip install --break-system-packages -q kokoro-onnx soundfile playwright 2>/dev/null || pip install -q kokoro-onnx soundfile playwright
for f in kokoro-v1.0.onnx voices-v1.0.bin; do
  [ -f "$f" ] || curl -sSL -o "$f" "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/$f"
done
echo "ready: python3 reel.py spec.json out.mp4  |  python3 adbuild.py out.mp4 clip.mp4 sound.mp3 'Line'"
