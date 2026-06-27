"""Stamp 'Page X of Y' (and optional footer text) onto an existing PDF.

Chromium headless cannot render CSS @page margin-box page numbers, so numbering
is added here as a post-process.

Usage:  python stamp_pagenum.py <file.pdf> [--footer "Networks 1 - Quiz 2"]
Overwrites the input file.
"""
import argparse
import io
import sys
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("--footer", default="")
    args = ap.parse_args()

    src = Path(args.pdf)
    reader = PdfReader(src)
    writer = PdfWriter()
    total = len(reader.pages)

    for i, page in enumerate(reader.pages, start=1):
        w = float(page.mediabox.width)
        buf = io.BytesIO()
        c = canvas.Canvas(buf, pagesize=(w, float(page.mediabox.height)))
        c.setFont("Helvetica", 9)
        c.setFillColor(HexColor("#555555"))
        c.drawCentredString(w / 2, 24, f"Page {i} of {total}")
        if args.footer:
            c.drawString(40, 24, args.footer)
        c.save()
        buf.seek(0)
        page.merge_page(PdfReader(buf).pages[0])
        writer.add_page(page)

    with open(src, "wb") as f:
        writer.write(f)
    print(f"Stamped {total} pages: {src}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
