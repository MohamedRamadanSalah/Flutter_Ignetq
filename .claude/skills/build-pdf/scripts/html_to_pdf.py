"""Render an HTML file to PDF via headless Microsoft Edge.

Usage:  python html_to_pdf.py <file.html> [-o out.pdf]
Default output: same name with .pdf extension.
"""
import argparse
import subprocess
import sys
from pathlib import Path

EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("html")
    ap.add_argument("-o", "--out")
    args = ap.parse_args()

    src = Path(args.html).resolve()
    if not src.exists():
        print(f"ERROR: not found: {src}", file=sys.stderr)
        return 1
    out = Path(args.out).resolve() if args.out else src.with_suffix(".pdf")

    cmd = [
        EDGE, "--headless", "--disable-gpu", "--no-sandbox",
        f"--print-to-pdf={out}", "--no-pdf-header-footer",
        "--virtual-time-budget=10000",
        src.as_uri(),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if not out.exists():
        print(res.stderr[-2000:], file=sys.stderr)
        print(f"ERROR: Edge produced no PDF at {out}", file=sys.stderr)
        return 1
    print(str(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
