"""Shared imaging utilities for the analyze-image skill.

Goal: deliver the cleanest possible pixels to the vision model and quantify how
trustworthy those pixels are, so reported findings can be confidence-tagged
against measured image quality rather than guesswork.

Design:
- One canonical loader that applies EXIF orientation, flattens alpha onto white,
  and normalizes exotic modes (CMYK, P, 16-bit, LA) to 8-bit RGB. What we tile is
  exactly what a human would see.
- Quality metrics computed with OpenCV when present, with a NumPy fallback so the
  module never hard-fails if cv2 is missing. Every metric is documented with the
  direction that means "good".
- A document-vs-photo classifier that lets callers pick sane processing defaults.

Run standalone as a quick quality probe:
    python imgutil.py <image>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps

try:
    import cv2  # type: ignore
    _HAS_CV2 = True
except Exception:  # pragma: no cover - cv2 expected on this machine
    cv2 = None
    _HAS_CV2 = False

# Claude's vision pipeline downscales so the long edge is ~1568 px. A tile at or
# under this is delivered to the model at (near) full fidelity.
DOWNSAMPLE_EDGE = 1568


# --------------------------------------------------------------------------- #
# Loading / normalization
# --------------------------------------------------------------------------- #
def load_normalized(path: str | Path) -> Image.Image:
    """Open an image and return an 8-bit RGB PIL image as a human would see it.

    - Applies EXIF orientation.
    - Uses the first frame of animated/multi-page formats.
    - Flattens transparency onto a white background (so dark UI text stays dark).
    - Converts CMYK / palette / 16-bit / grayscale-with-alpha to RGB.
    """
    img = Image.open(path)
    try:
        img.seek(0)
    except Exception:
        pass
    img = ImageOps.exif_transpose(img)

    if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
        rgba = img.convert("RGBA")
        bg = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
        img = Image.alpha_composite(bg, rgba).convert("RGB")
    elif img.mode == "I;16" or img.mode == "I":
        arr = np.asarray(img).astype(np.float64)
        lo, hi = float(arr.min()), float(arr.max())
        norm = (arr - lo) / (hi - lo) * 255.0 if hi > lo else np.zeros_like(arr)
        img = Image.fromarray(norm.astype(np.uint8), mode="L").convert("RGB")
    elif img.mode != "RGB":
        img = img.convert("RGB")
    return img


def _gray(img: Image.Image) -> np.ndarray:
    """Luma array (uint8, HxW) from an RGB PIL image."""
    arr = np.asarray(img.convert("L"))
    return arr


# --------------------------------------------------------------------------- #
# Quality metrics
# --------------------------------------------------------------------------- #
def _laplacian_var(gray: np.ndarray) -> float:
    """Variance of the Laplacian -- the standard focus/sharpness measure.

    Higher = sharper. Low values flag blur or heavy downscaling. The threshold
    is scale-dependent, so callers should treat it comparatively, not absolutely.
    """
    if _HAS_CV2:
        return float(cv2.Laplacian(gray, cv2.CV_64F).var())
    # NumPy fallback: 4-neighbour discrete Laplacian.
    g = gray.astype(np.float64)
    lap = (
        -4 * g
        + np.roll(g, 1, 0) + np.roll(g, -1, 0)
        + np.roll(g, 1, 1) + np.roll(g, -1, 1)
    )[1:-1, 1:-1]
    return float(lap.var())


def _noise_sigma(gray: np.ndarray) -> float:
    """Robust noise estimate: MAD of a high-pass (image minus 3x3 box blur)."""
    g = gray.astype(np.float64)
    if _HAS_CV2:
        blur = cv2.blur(gray, (3, 3)).astype(np.float64)
    else:
        k = np.ones((3, 3)) / 9.0
        # cheap separable box blur via cumulative trick omitted; use simple conv
        from numpy.lib.stride_tricks import sliding_window_view as swv
        pad = np.pad(g, 1, mode="edge")
        blur = swv(pad, (3, 3)).mean(axis=(-1, -2))
    hp = g - blur
    mad = np.median(np.abs(hp - np.median(hp)))
    return float(1.4826 * mad)  # MAD -> sigma for ~Gaussian


def quality_metrics(img: Image.Image) -> dict:
    """Return measured quality indicators with interpretation flags.

    Keys:
      sharpness_lapvar  higher=sharper (blurry if very low, e.g. <60 at full res)
      brightness_mean   0..255 mean luma (too dark <50, too bright >205)
      contrast_std      0..~128 luma spread (flat/low-contrast if <25)
      noise_sigma       estimated noise std in luma units (noisy if >8)
      clip_black_frac   fraction of near-black pixels (crushed shadows if high)
      clip_white_frac   fraction of near-white pixels (blown highlights if high)
      entropy_bits      0..8 histogram entropy (near-blank if <2)
      flags             human-readable quality warnings (empty list == clean)
    """
    g = _gray(img)
    total = g.size
    hist = np.bincount(g.ravel(), minlength=256).astype(np.float64)
    p = hist / max(1, total)
    nz = p[p > 0]
    entropy = float(-(nz * np.log2(nz)).sum())

    m = {
        "sharpness_lapvar": round(_laplacian_var(g), 1),
        "brightness_mean": round(float(g.mean()), 1),
        "contrast_std": round(float(g.std()), 1),
        "noise_sigma": round(_noise_sigma(g), 2),
        "clip_black_frac": round(float((g < 4).mean()), 4),
        "clip_white_frac": round(float((g > 251).mean()), 4),
        "entropy_bits": round(entropy, 2),
    }
    # Flags are intentionally conservative: they must fire only on genuinely
    # hard-to-read regions, never on a normal white-background document (which
    # is bright and high-white-fraction yet perfectly legible). A flag that
    # cries wolf trains the reader to ignore it.
    flags = []
    if m["sharpness_lapvar"] < 40:
        flags.append("LOW_SHARPNESS")          # genuine blur, not just smooth fill
    if m["brightness_mean"] < 50:
        flags.append("DARK")
    elif m["brightness_mean"] > 235 and m["contrast_std"] < 20:
        flags.append("WASHED_OUT")             # bright AND flat == detail lost
    if m["contrast_std"] < 18 and m["entropy_bits"] >= 2.0:
        flags.append("LOW_CONTRAST")           # flat but not blank
    if m["noise_sigma"] > 8:
        flags.append("NOISY")
    if m["contrast_std"] < 12 and m["entropy_bits"] < 2.0:
        flags.append("MOSTLY_BLANK")           # near-empty region, little to read
    m["flags"] = flags
    return m


def classify_kind(img: Image.Image) -> str:
    """Heuristically label the image so callers can choose defaults.

    Returns one of: 'document', 'screenshot', 'photo', 'graphic'.
    Uses colour count, saturation, and white-background fraction on a downscaled
    copy (fast and resolution-stable).
    """
    small = img.copy()
    small.thumbnail((512, 512), Image.LANCZOS)
    rgb = np.asarray(small).reshape(-1, 3)
    # quantize to 4 bits/channel to estimate distinct-colour richness
    q = (rgb >> 4).astype(np.uint32)
    codes = (q[:, 0] << 8) | (q[:, 1] << 4) | q[:, 2]
    n_colors = int(np.unique(codes).size)
    hsv = np.asarray(small.convert("HSV")).reshape(-1, 3)
    sat_mean = float(hsv[:, 1].mean())
    g = np.asarray(small.convert("L"))
    white_frac = float((g > 235).mean())

    if white_frac > 0.45 and n_colors < 400 and sat_mean < 40:
        return "document"
    if n_colors < 1200 and sat_mean < 70:
        return "screenshot"
    if n_colors > 2500 and sat_mean > 50:
        return "photo"
    return "graphic"


def has_cv2() -> bool:
    return _HAS_CV2


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: python imgutil.py <image>", file=sys.stderr)
        return 2
    p = Path(sys.argv[1])
    if not p.exists():
        print(f"ERROR: not found: {p}", file=sys.stderr)
        return 2
    img = load_normalized(p)
    out = {
        "size_px": list(img.size),
        "kind": classify_kind(img),
        "cv2": _HAS_CV2,
        "quality": quality_metrics(img),
    }
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
