"""
ocr.py — Windows built-in OCR for analyze-image skill.

Uses Windows.Media.Ocr via the winrt Python package (Windows 10+ only).
No external OCR engine (Tesseract, etc.) required.
"""

import asyncio
import json
import sys
from pathlib import Path

from winrt.windows.storage import StorageFile
from winrt.windows.graphics.imaging import BitmapDecoder, BitmapPixelFormat
from winrt.windows.media.ocr import OcrEngine


async def _ocr(path: str) -> list[dict]:
    file = await StorageFile.get_file_from_path_async(path)
    stream = await file.open_read_async()
    decoder = await BitmapDecoder.create_async(stream)
    sb = await decoder.get_software_bitmap_async()

    engine = OcrEngine.try_create_from_user_profile_languages()
    if engine is None:
        print("ERROR: Could not create OCR engine (try an en-US system language).")
        sys.exit(1)

    result = await engine.recognize_async(sb)
    lines = []
    for line in result.lines:
        lines.append({
            "text": line.text,
            "words": [w.text for w in line.words],
        })
    return lines, result.text


def ocr_image(image_path: str) -> tuple[list[dict], str]:
    """Run Windows OCR on *image_path*. Returns (lines, full_text)."""
    return asyncio.run(_ocr(image_path))


def main():
    if len(sys.argv) < 2:
        print("Usage: python ocr.py <image.png> [--json]")
        print("  --json  Output as JSON (default: human-readable)")
        sys.exit(1)

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"ERROR: file not found: {path}")
        sys.exit(1)

    lines, text = ocr_image(str(path.resolve()))

    if "--json" in sys.argv:
        print(json.dumps({"text": text, "lines": lines}, indent=2))
    else:
        print(f"--- OCR: {path.name} ---")
        print(text)
        print(f"--- {len(lines)} lines ---")
        for i, line in enumerate(lines):
            print(f"  [{i:3d}] {line['text']}")


if __name__ == "__main__":
    main()
