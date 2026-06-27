"""Zoom into a region of an image for verification / fine-detail reading.

Use after prep.py when a tile is still too dense, when a claim must be checked
against the exact pixels, or to read tiny text / thin lines. The crop is
upscaled with a high-quality kernel so the model sees an enlarged, sharper view
of just that area, with optional enhancement for hostile images.

Specify the region one of two ways:
  --box X Y W H        pixel box in ORIGINAL image coordinates (use a tile core)
  --frac L T R B       fractional box, 0..1 (left top right bottom)

Enhancement (compose freely):
  --clahe              adaptive local contrast (best for faint scans/screenshots)
  --denoise            edge-preserving denoise (heavy JPG / sensor noise)
  --sharpen            unsharp mask
  --grayscale          drop colour (sometimes crisper for text)
  --grid N             overlay a coordinate grid every N original px, with labels
                       (for precise localization / measurement / pointing)

Usage:
    python zoom.py <img> --box 1200 800 400 300 --scale 3 --clahe
    python zoom.py <img> --frac 0 0.9 1 1 --scale 2 --grid 50
Prints crop info + measured quality, and the output path on the last line.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

import imgutil
from imgutil import DOWNSAMPLE_EDGE, load_normalized, quality_metrics

try:
    import cv2  # type: ignore
except Exception:
    cv2 = None

MAX_OUT_EDGE = DOWNSAMPLE_EDGE * 2  # no point exceeding ~2x the downsample limit


def resize_hq(pil_img: Image.Image, new_wh) -> Image.Image:
    """High-quality resize: cv2 LANCZOS4 (upscale) when available, else PIL."""
    if cv2 is not None:
        arr = np.asarray(pil_img)
        interp = cv2.INTER_LANCZOS4 if new_wh[0] >= pil_img.width else cv2.INTER_AREA
        out = cv2.resize(arr, new_wh, interpolation=interp)
        return Image.fromarray(out)
    return pil_img.resize(new_wh, Image.LANCZOS)


def apply_clahe(pil_img: Image.Image) -> Image.Image:
    if cv2 is None:
        from PIL import ImageOps
        return ImageOps.autocontrast(pil_img, cutoff=1)
    lab = cv2.cvtColor(np.asarray(pil_img), cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)
    l = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8)).apply(l)
    rgb = cv2.cvtColor(cv2.merge((l, a, b)), cv2.COLOR_LAB2RGB)
    return Image.fromarray(rgb)


def apply_denoise(pil_img: Image.Image) -> Image.Image:
    if cv2 is None:
        from PIL import ImageFilter
        return pil_img.filter(ImageFilter.MedianFilter(3))
    arr = cv2.fastNlMeansDenoisingColored(np.asarray(pil_img), None, 5, 5, 7, 21)
    return Image.fromarray(arr)


def apply_sharpen(pil_img: Image.Image) -> Image.Image:
    if cv2 is None:
        from PIL import ImageFilter
        return pil_img.filter(ImageFilter.UnsharpMask(2, 130, 2))
    arr = np.asarray(pil_img)
    blur = cv2.GaussianBlur(arr, (0, 0), 1.0)
    out = cv2.addWeighted(arr, 1.5, blur, -0.5, 0)
    return Image.fromarray(out)


def draw_grid(pil_img: Image.Image, step_orig: int, x0: int, y0: int,
              scale_x: float, scale_y: float) -> Image.Image:
    """Overlay a labeled coordinate grid in ORIGINAL-image pixel units."""
    img = pil_img.convert("RGB")
    d = ImageDraw.Draw(img)
    W, H = img.size
    try:
        font = ImageFont.truetype("arial.ttf", 14)
    except Exception:
        font = ImageFont.load_default()
    color = (220, 30, 30)
    # vertical lines at multiples of step in original coords
    start_x = ((x0 // step_orig) + 1) * step_orig
    ox = start_x
    while ox * 1 <= x0 + W / scale_x:
        px = int((ox - x0) * scale_x)
        if 0 <= px < W:
            d.line([(px, 0), (px, H)], fill=color, width=1)
            d.text((px + 2, 2), str(ox), fill=color, font=font)
        ox += step_orig
    start_y = ((y0 // step_orig) + 1) * step_orig
    oy = start_y
    while oy <= y0 + H / scale_y:
        py = int((oy - y0) * scale_y)
        if 0 <= py < H:
            d.line([(0, py), (W, py)], fill=color, width=1)
            d.text((2, py + 2), str(oy), fill=color, font=font)
        oy += step_orig
    return img


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("image")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--box", nargs=4, type=int, metavar=("X", "Y", "W", "H"))
    g.add_argument("--frac", nargs=4, type=float, metavar=("L", "T", "R", "B"))
    ap.add_argument("--scale", type=float, default=3.0, help="upscale factor")
    ap.add_argument("--clahe", action="store_true")
    ap.add_argument("--denoise", action="store_true")
    ap.add_argument("--sharpen", action="store_true")
    ap.add_argument("--grayscale", action="store_true")
    ap.add_argument("--grid", type=int, default=0,
                    help="overlay coordinate grid every N original px")
    ap.add_argument("--enhance", action="store_true",
                    help="shorthand for --clahe --sharpen")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    src = Path(args.image)
    if not src.exists():
        print(f"ERROR: file not found: {src}", file=sys.stderr)
        return 2
    try:
        img = load_normalized(src)
    except Exception as e:
        print(f"ERROR: cannot open image: {e}", file=sys.stderr)
        return 2
    W, H = img.size

    if args.box:
        x, y, w, h = args.box
        box = (x, y, x + w, y + h)
    else:
        l, t, r, b = args.frac
        box = (int(l * W), int(t * H), int(r * W), int(b * H))
    x0 = max(0, min(W - 1, box[0]))
    y0 = max(0, min(H - 1, box[1]))
    x1 = max(x0 + 1, min(W, box[2]))
    y1 = max(y0 + 1, min(H, box[3]))
    crop = img.crop((x0, y0, x1, y1))
    cw, ch = crop.size

    # upscale (capped so we never exceed ~2x the downsample limit)
    new = [max(1, round(cw * args.scale)), max(1, round(ch * args.scale))]
    if max(new) > MAX_OUT_EDGE:
        f = MAX_OUT_EDGE / max(new)
        new = [max(1, round(new[0] * f)), max(1, round(new[1] * f))]
    eff_scale_x = new[0] / cw
    eff_scale_y = new[1] / ch
    crop = resize_hq(crop, (new[0], new[1]))

    if args.enhance:
        args.clahe = True
        args.sharpen = True
    if args.denoise:
        crop = apply_denoise(crop)
    if args.clahe:
        crop = apply_clahe(crop)
    if args.sharpen:
        crop = apply_sharpen(crop)
    if args.grayscale:
        crop = crop.convert("L").convert("RGB")
    if args.grid > 0:
        crop = draw_grid(crop, args.grid, x0, y0, eff_scale_x, eff_scale_y)

    out = Path(args.out) if args.out else src.with_name(
        f"{src.stem}_zoom_{x0}_{y0}_{x1}_{y1}.png")
    crop.save(out)

    q = quality_metrics(crop)
    print(f"crop=({x0},{y0})-({x1},{y1}) src_px={cw}x{ch} out_px={new[0]}x{new[1]} "
          f"sharpness={q['sharpness_lapvar']} flags={q['flags'] or 'none'}")
    print(str(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
