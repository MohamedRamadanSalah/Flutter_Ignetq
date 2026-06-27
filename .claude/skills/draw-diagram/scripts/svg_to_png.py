"""Render an SVG to PNG via headless Microsoft Edge, for visual verification.

Usage:  python svg_to_png.py <file.svg> [--scale 2]
Writes: <file.svg>.png  (e.g. topology.svg.png)
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"


def svg_size(svg_text: str) -> tuple[int, int]:
    m = re.search(r'viewBox\s*=\s*"[\d.\-]+\s+[\d.\-]+\s+([\d.]+)\s+([\d.]+)"', svg_text)
    if m:
        return int(float(m.group(1))), int(float(m.group(2)))
    w = re.search(r'<svg[^>]*\bwidth\s*=\s*"([\d.]+)', svg_text)
    h = re.search(r'<svg[^>]*\bheight\s*=\s*"([\d.]+)', svg_text)
    if w and h:
        return int(float(w.group(1))), int(float(h.group(1)))
    return 1000, 700


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("svg")
    ap.add_argument("--scale", type=float, default=2.0)
    args = ap.parse_args()

    src = Path(args.svg).resolve()
    if not src.exists():
        print(f"ERROR: not found: {src}", file=sys.stderr)
        return 1
    out = src.with_suffix(src.suffix + ".png")
    w, h = svg_size(src.read_text(encoding="utf-8"))
    w, h = int(w * args.scale), int(h * args.scale)

    cmd = [
        EDGE, "--headless", "--disable-gpu", "--no-sandbox",
        f"--screenshot={out}", f"--window-size={w},{h}",
        f"--force-device-scale-factor={args.scale}",
        "--default-background-color=FFFFFFFF", "--hide-scrollbars",
        src.as_uri(),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if not out.exists():
        print(res.stderr[-2000:], file=sys.stderr)
        print(f"ERROR: Edge produced no PNG at {out}", file=sys.stderr)
        return 1
    print(str(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
