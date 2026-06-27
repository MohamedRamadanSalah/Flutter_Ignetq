"""Prepare ANY image for high-accuracy visual reading.

Vision models downsample large images (Claude resizes to ~1568 px long edge),
so small text, thin lines, and fine detail are LOST before the model ever sees
them. This script counters that and adds measured quality signals:

  * exact metadata (size, format, mode, dpi, EXIF, ICC, alpha, bit depth)
  * a whole-image overview (orientation pass only)
  * native-resolution tiles whose long edge fits under the downsample threshold,
    each carrying a non-overlap "core" box so objects can be counted across the
    full image without double-counting at tile seams
  * per-tile quality metrics + flags (LOW_SHARPNESS / DARK / NOISY ...) so the
    reader knows which regions to distrust and re-verify
  * an image-kind classification (document / screenshot / photo / graphic)

Usage:
    python prep.py <image> [--outdir DIR] [--maxedge 1400] [--overlap 0.10]
                           [--enhance] [--no-metrics]

Output (under <outdir>/<stem>/):
    meta.json        metadata + quality + tile manifest (boxes, cores, per-tile flags)
    overview.png     whole image, downscaled to <=1568 long edge
    tiles/rRcC.png   native-resolution tiles (pristine pixels for best OCR)
    tiles_enhanced/  (only with --enhance) CLAHE + denoise + deskew variants

Exit 0 on success; prints meta.json path on the last line. Exit 2 on bad input.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ExifTags

import imgutil
from imgutil import DOWNSAMPLE_EDGE, load_normalized, quality_metrics, classify_kind

try:
    import cv2  # type: ignore
except Exception:
    cv2 = None


def read_raw_meta(path: Path) -> dict:
    """Format-level metadata read from the original file (pre-normalization)."""
    img = Image.open(path)
    exif = {}
    try:
        raw = img.getexif()
        for tag_id, val in raw.items():
            tag = ExifTags.TAGS.get(tag_id, str(tag_id))
            if isinstance(val, bytes):
                val = val.decode("utf-8", "replace")
            exif[tag] = str(val)[:200]
    except Exception:
        pass
    return {
        "format": img.format,
        "mode": img.mode,
        "dpi": list(img.info["dpi"]) if "dpi" in img.info else None,
        "has_alpha": img.mode in ("RGBA", "LA") or "transparency" in img.info,
        "icc_profile": bool(img.info.get("icc_profile")),
        "animated": bool(getattr(img, "is_animated", False)),
        "n_frames": int(getattr(img, "n_frames", 1)),
        "exif": exif,
    }


def estimate_skew_deg(pil_img: Image.Image, search=15.0, step=0.5) -> float:
    """Estimate text skew via the projection-profile method (document standard).

    Binarize, then for each candidate angle in [-search, search] rotate and score
    the sharpness (sum of squared row-to-row differences) of the horizontal
    projection profile. Aligned text produces tight, alternating row sums -> a
    sharp profile; the maximizing angle is the skew. Robust on mixed text+diagram
    layouts (axis-aligned text dominates the profile) and bounded by `search`, so
    it can never flip orientation. Returns 0.0 if there is too little ink to trust.
    """
    if cv2 is None:
        return 0.0
    gray = cv2.cvtColor(np.asarray(pil_img), cv2.COLOR_RGB2GRAY)
    # estimate is scale-invariant -- downscale for speed
    h, w = gray.shape
    if max(h, w) > 800:
        s = 800 / max(h, w)
        gray = cv2.resize(gray, (int(w * s), int(h * s)), interpolation=cv2.INTER_AREA)
    thr = cv2.threshold(gray, 0, 255,
                        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    if (thr > 0).mean() < 0.003:        # almost no ink -> nothing to align
        return 0.0
    H, W = thr.shape
    best_angle, best_score = 0.0, -1.0
    for a in np.arange(-search, search + 1e-6, step):
        M = cv2.getRotationMatrix2D((W / 2, H / 2), a, 1.0)
        rot = cv2.warpAffine(thr, M, (W, H), flags=cv2.INTER_NEAREST,
                             borderMode=cv2.BORDER_CONSTANT, borderValue=0)
        proj = rot.sum(axis=1, dtype=np.float64)
        score = float(((proj[1:] - proj[:-1]) ** 2).sum())
        if score > best_score:
            best_score, best_angle = score, float(a)
    return best_angle


def deskew(pil_img: Image.Image, angle_deg: float) -> Image.Image:
    """Rotate by -angle to level the content. Clamped; no-op for tiny angles."""
    if cv2 is None or abs(angle_deg) < 0.3 or abs(angle_deg) > 15:
        return pil_img
    arr = np.asarray(pil_img)
    h, w = arr.shape[:2]
    M = cv2.getRotationMatrix2D((w / 2, h / 2), angle_deg, 1.0)
    out = cv2.warpAffine(arr, M, (w, h), flags=cv2.INTER_CUBIC,
                         borderMode=cv2.BORDER_REPLICATE)
    return Image.fromarray(out)


def enhance_for_legibility(pil_img: Image.Image, kind: str,
                           do_deskew: bool = False) -> Image.Image:
    """Produce a legibility-enhanced variant (a DERIVED view, not the source).

    Safe, content-preserving operations only: edge-preserving denoise (documents/
    screenshots), CLAHE local contrast, and an unsharp mask. Deskew is OFF by
    default -- it is the one geometry-changing step and only helps genuinely
    skewed scans; enable it explicitly with do_deskew, and even then it is
    Hough-estimated and clamped to +/-15 deg so it can never flip orientation.
    Falls back to PIL autocontrast + unsharp if cv2 is unavailable.
    """
    if cv2 is None:
        from PIL import ImageOps, ImageFilter
        out = ImageOps.autocontrast(pil_img, cutoff=1)
        return out.filter(ImageFilter.UnsharpMask(2, 120, 2))

    if do_deskew:
        pil_img = deskew(pil_img, estimate_skew_deg(pil_img))

    bgr = cv2.cvtColor(np.asarray(pil_img), cv2.COLOR_RGB2BGR)
    if kind in ("document", "screenshot"):
        bgr = cv2.fastNlMeansDenoisingColored(bgr, None, 3, 3, 7, 21)

    lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    l = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(l)
    bgr = cv2.cvtColor(cv2.merge((l, a, b)), cv2.COLOR_LAB2BGR)

    blur = cv2.GaussianBlur(bgr, (0, 0), 1.0)
    bgr = cv2.addWeighted(bgr, 1.5, blur, -0.5, 0)  # unsharp mask
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    return Image.fromarray(rgb)


def plan_tiles(W: int, H: int, maxedge: int, overlap: float):
    """Return tile specs with both the padded read box and the non-overlap core.

    The core box is the region the tile uniquely owns (no overlap); counting
    objects whose centre lies in a tile's core guarantees no double-counting.
    """
    cols = max(1, math.ceil(W / maxedge))
    rows = max(1, math.ceil(H / maxedge))
    step_x = W / cols
    step_y = H / rows
    ovx = step_x * overlap
    ovy = step_y * overlap
    tiles = []
    for r in range(rows):
        for c in range(cols):
            cx0, cy0 = int(round(c * step_x)), int(round(r * step_y))
            cx1, cy1 = int(round((c + 1) * step_x)), int(round((r + 1) * step_y))
            x0 = max(0, int(round(c * step_x - ovx)))
            y0 = max(0, int(round(r * step_y - ovy)))
            x1 = min(W, int(round((c + 1) * step_x + ovx)))
            y1 = min(H, int(round((r + 1) * step_y + ovy)))
            tiles.append({
                "row": r, "col": c,
                "box": [x0, y0, x1, y1],          # padded region actually shown
                "core": [cx0, cy0, cx1, cy1],     # unique region (count here)
            })
    return rows, cols, tiles


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("image")
    ap.add_argument("--outdir", default="_extracted")
    ap.add_argument("--maxedge", type=int, default=1400,
                    help="max long edge (px) of each native tile; capped at 1568")
    ap.add_argument("--overlap", type=float, default=0.10,
                    help="fractional overlap between adjacent tiles (0..0.5)")
    ap.add_argument("--enhance", action="store_true",
                    help="also write legibility-enhanced tile variants "
                         "(CLAHE + denoise + sharpen)")
    ap.add_argument("--deskew", action="store_true",
                    help="with --enhance: also straighten skewed SCANS "
                         "(Hough-estimated, clamped +/-15 deg; off by default)")
    ap.add_argument("--no-metrics", action="store_true",
                    help="skip per-tile quality metrics (faster)")
    args = ap.parse_args()

    src = Path(args.image)
    if not src.exists():
        print(f"ERROR: file not found: {src}", file=sys.stderr)
        return 2
    try:
        raw = read_raw_meta(src)
        img = load_normalized(src)
    except Exception as e:
        print(f"ERROR: cannot open image: {e}", file=sys.stderr)
        return 2

    W, H = img.size
    stem = src.stem
    out = Path(args.outdir) / stem
    tiles_dir = out / "tiles"
    tiles_dir.mkdir(parents=True, exist_ok=True)

    kind = classify_kind(img)
    whole_quality = None if args.no_metrics else quality_metrics(img)

    # --- overview ---
    ov = img.copy()
    if max(W, H) > DOWNSAMPLE_EDGE:
        s = DOWNSAMPLE_EDGE / max(W, H)
        ov = ov.resize((max(1, round(W * s)), max(1, round(H * s))), Image.LANCZOS)
    ov.save(out / "overview.png")
    downsampled = max(W, H) > DOWNSAMPLE_EDGE

    # --- tiles ---
    maxedge = min(args.maxedge, DOWNSAMPLE_EDGE)
    overlap = max(0.0, min(0.5, args.overlap))
    if not downsampled:
        rows, cols = 1, 1
        tiles = [{"row": 0, "col": 0, "box": [0, 0, W, H], "core": [0, 0, W, H]}]
    else:
        rows, cols, tiles = plan_tiles(W, H, maxedge, overlap)

    enh_dir = out / "tiles_enhanced"
    if args.enhance:
        enh_dir.mkdir(exist_ok=True)

    for t in tiles:
        x0, y0, x1, y1 = t["box"]
        crop = img.crop((x0, y0, x1, y1)) if downsampled else img
        fn = f"r{t['row']}c{t['col']}.png"
        crop.save(tiles_dir / fn)
        t["file"] = f"tiles/{fn}"
        if not args.no_metrics:
            q = quality_metrics(crop)
            t["sharpness_lapvar"] = q["sharpness_lapvar"]
            t["brightness_mean"] = q["brightness_mean"]
            t["flags"] = q["flags"]
        if args.enhance:
            enhance_for_legibility(crop, kind, do_deskew=args.deskew).save(enh_dir / fn)
            t["file_enhanced"] = f"tiles_enhanced/{fn}"

    meta = {
        "source": str(src),
        "size_px": [W, H],
        "megapixels": round(W * H / 1e6, 2),
        "kind": kind,
        "cv2_available": imgutil.has_cv2(),
        **raw,
        "downsampled_by_vision": downsampled,
        "quality": whole_quality,
        "overview": "overview.png",
        "tile_grid": [rows, cols],
        "tile_maxedge": maxedge,
        "tile_overlap": overlap,
        "tile_count": len(tiles),
        "tiles": tiles,
    }
    meta_path = out / "meta.json"
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")

    print(f"size={W}x{H} mp={meta['megapixels']} kind={kind} "
          f"downsampled={downsampled} tiles={len(tiles)} ({rows}x{cols})")
    if whole_quality and whole_quality["flags"]:
        print(f"QUALITY FLAGS: {', '.join(whole_quality['flags'])} "
              f"(sharpness={whole_quality['sharpness_lapvar']}, "
              f"brightness={whole_quality['brightness_mean']})")
    bad = [t["file"] for t in tiles if t.get("flags")]
    if bad:
        print(f"NOTE: {len(bad)} tile(s) flagged for quality -- re-verify with "
              f"zoom.py --clahe/--denoise before trusting fine detail.")
    if downsampled:
        print("NOTE: exceeds vision downsample limit -- read tiles/, not just "
              "overview.png.")
    print(str(meta_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
