---
name: analyze-image
description: Read and analyze ANY image (PNG, JPG, WebP, BMP, TIFF, GIF, screenshots, diagrams, charts, scans, photos) at the highest achievable accuracy. Counters vision downsampling with native-resolution tiling and targeted zoom, then re-reads and tests every claim against the pixels before reporting. Use whenever the user gives you an image to read, describe, transcribe, measure, or extract data from — especially when detail and correctness matter.
---

# Analyze Image — High-Accuracy Reading & Verification Protocol

A weak reader glances at a downsized thumbnail, narrates a plausible-sounding
description, and calls it done. You will not. The single biggest cause of image
misreads is **silent downsampling**: the vision pipeline shrinks any image whose
long edge exceeds ~1568 px, so small text, thin lines, fine gradients, and dense
tables are destroyed before you ever see them. The second biggest cause is
**reporting from memory of the glance** instead of from the pixels. This protocol
defeats both: it reads at native resolution by tiling, then independently
re-verifies and tests every factual claim before it ships.

## Hard Rules (non-negotiable)

1. **Never describe an image you have only seen at overview/thumbnail size when
   `prep.py` reports `downsampled=True`.** You MUST read the native-resolution
   tiles. The overview is for orientation only.
2. **Never report a number, a word, a color value, a count, or a coordinate you
   have not confirmed by looking at the specific region** (a tile, or a `zoom.py`
   crop of it). "It looks like about…" is a hypothesis, not a finding — confirm
   or label it.
3. **Every factual claim gets a second, independent look** (the Revision pass).
   Read the claim, find the exact pixels it rests on, and try to *falsify* it.
   A claim that survives a genuine falsification attempt is reported; one that
   does not is corrected or dropped.
4. **Transcribe verbatim, then verify character-by-character** for any text, code,
   serial number, equation, axis label, or address. Ambiguous glyphs
   (`0/O`, `1/l/I`, `5/S`, `rn/m`, `,/.`) are resolved by zooming, never guessed.
5. **State uncertainty explicitly.** Tag every claim High / Medium / Low
   confidence. If a region is illegible even after zoom+enhance, say "illegible"
   — never invent plausible content to fill the gap.
6. **Distinguish observation from inference.** What is literally drawn/written
   vs. what you conclude from it are reported in separate registers.
7. **Report honestly.** If a tile failed to render, a region is blurred, EXIF was
   stripped, or a measurement is approximate, say so. Skipped steps are disclosed.

## Procedure

### Step 1 — Prep (metadata + overview + native tiles + quality)
```powershell
python .claude/skills/analyze-image/scripts/prep.py "<image>" --outdir _extracted
# add --enhance to also write CLAHE/denoise/sharpen tile variants;
# add --deskew (with --enhance) only for genuinely skewed SCANS.
```
Writes under `_extracted/<stem>/`: `meta.json`, `overview.png` (whole image), and
`tiles/rRcC.png` (native-res tiles). **Read `meta.json` first** and act on it:
- `downsampled_by_vision: true` → reading tiles is **mandatory**; `false` → the
  whole image fits and the single tile equals the image.
- `kind` (document / screenshot / photo / graphic) sets your reading strategy.
- `quality` and each tile's `flags` are **measured** signals — they drive your
  confidence tags. A tile flagged `LOW_SHARPNESS` / `DARK` / `NOISY` /
  `LOW_CONTRAST` / `WASHED_OUT` is one whose reads you must re-verify with
  `zoom.py` (and may at best support a Medium/Low-confidence claim). No flags ==
  pixels are trustworthy. (`imgutil.py <image>` prints these metrics standalone.)
- Each tile carries a `box` (the padded, overlapping region shown) **and** a
  `core` (the unique non-overlapping region it owns) — used for counting in Step 3.

Also run OCR text extraction in parallel (works on any PNG/JPG without a vision model):
```powershell
python .claude/skills/analyze-image/scripts/ocr.py "<image>" [--json]
```
This uses Windows built-in OCR (Windows.Media.Ocr, Windows 10+). The extracted
text provides an independent data stream — useful when the model lacks vision
capability, and as a cross-check when vision is available. Pipe with `--json` for
structured consumption (line-level + word-level breakdown).

### Step 2 — Orientation pass (overview)
Read `overview.png` with the Read tool. Establish, in one short note: what kind
of image this is (photo / screenshot / UI / chart / diagram / scanned document /
map / table / mixed), its overall layout, the reading order, and a list of every
distinct **region** worth a close look. This is your plan — it tells you which
tiles and crops matter. Do not extract details here; resolution is too low.

### Step 3 — Systematic detail pass (tiles)
Read **every** tile in `meta.json` with the Read tool, in row-major order — not
just the ones you think are interesting; the boring corner is where the footnote
hides. For each tile, record what it contains: text (verbatim), objects, numbers,
labels, colors, spatial relationships. Tiles overlap by design — use the overlap
to stitch content that straddles a seam, and use the pixel `box` in `meta.json`
to map any finding back to original-image coordinates.

**When the model cannot read image files** (returns "Cannot read image"): skip
Step 2–3 tile reading and rely on `ocr.py` text extraction from Step 1 as your
primary text source. Cross-reference the OCR output against any available source
file (e.g., SVG, PPTX text layer, DOCX) for verification. SVG sources for
diagrams drawn by `/draw-diagram` always contain the exact intended text —
prefer them over OCR when both exist.

### Step 4 — Targeted zoom (the part weak readers skip)
For anything still dense, tiny, faint, or decision-critical, crop and magnify:
```powershell
python .claude/skills/analyze-image/scripts/zoom.py "<image>" --box X Y W H --scale 3
python .claude/skills/analyze-image/scripts/zoom.py "<image>" --frac 0 0.9 1 1 --scale 2 --clahe
python .claude/skills/analyze-image/scripts/zoom.py "<image>" --box X Y W H --grid 50
```
`--box` uses original-image pixels (take them from a tile's `box`/`core`);
`--frac` uses 0..1 fractions. Enhancement flags compose: `--clahe` (adaptive
local contrast — best for faint scans/screenshots), `--denoise` (heavy JPG /
sensor noise), `--sharpen`, `--grayscale`, `--enhance` (= clahe+sharpen). Match
the flag to the tile's quality flag from Step 1 (NOISY→`--denoise`,
LOW_CONTRAST/WASHED_OUT→`--clahe`). `--grid N` overlays a labeled coordinate grid
every N original px — use it to localize, measure, or point precisely. The crop's
own measured sharpness/flags are printed so you can tell if enhancement helped.
Zoom is mandatory for: small/dense text, tabular data, chart tick values and data
points, handwriting, logos/seals, and any glyph you could not resolve in Step 3.

### Step 5 — Task-specific reading
Apply the lens the user asked for. Common modes (use what fits):
- **Transcription / OCR**: reproduce text exactly, preserving layout, line breaks,
  and structure. Use `ocr.py` for automated text extraction when vision is
  unavailable or as a first pass. Then re-read each line (Step 6 covers this).
  For diagrams rendered from SVG, read the `.svg` source directly — it is
  always more accurate than OCR for synthetic text.
- **Data extraction (charts/tables)**: read axes, units, scales, and legend first;
  estimate each value by reading against gridlines; reconstruct the table/series;
  note interpolation where a value falls between gridlines.
- **Diagrams / UI / screenshots**: enumerate every node/control/label and the
  connections or hierarchy between them; transcribe button/menu text verbatim.
- **Photos / scenes**: inventory subjects, then attributes, spatial relations,
  text, and context; separate what is visible from what you infer.
- **Counting**: count each object in the tile whose **`core`** box (from
  `meta.json`) contains the object's centre — the cores partition the image with
  no overlap, so nothing is counted twice or missed at a seam. State the count
  and your confidence; use `zoom.py --grid` if positions are ambiguous.

### Step 6 — Revision pass (independent re-read — MANDATORY)
List every factual claim you intend to report. For each one, **go back to the
exact pixels** (the relevant tile or a fresh `zoom.py` crop) and actively try to
disprove it: Is that digit a 3 or an 8? Is that line solid or dashed? Are there
really four items or five? Is that arrow pointing in or out? Treat your first read
as a suspect, not a witness. Correct everything that fails. This pass is not
optional and is not a re-skim of the overview — it is pixel-level falsification.

### Step 7 — Cross-checks / tests (verify by a second method)
Where the image admits an independent check, run it — agreement between two
methods is your accuracy evidence:
- **Internal consistency**: do parts sum to the stated total? do percentages reach
  100%? do labeled coordinates match the visual position? does a chart's described
  trend match its plotted points?
- **Cross-modal**: compare your visual text read against `meta.json`/EXIF where
  relevant; if the image was rendered from a known source file, diff against it.
  Use `ocr.py` output as a second-opinion text read — flag any discrepancy
  between visual reading and OCR for re-inspection.
- **Redundancy**: re-read one critical value from a *different* crop (different
  scale or `--enhance`) and confirm the two reads agree.
- **Plausibility / units**: do magnitudes and units make physical sense? flag any
  value that violates an obvious constraint as suspect, and re-examine it.
Record each check and its outcome (pass / mismatch-resolved / unresolved).

### Step 8 — Report
Deliver, in this order:
1. **One-line summary** — what the image is.
2. **Findings** — structured to the task (transcript, table, inventory, answer),
   each item tagged **[H] / [M] / [L]** confidence.
3. **Observations vs. inferences** — kept separate.
4. **Verification notes** — what you tiled/zoomed, which cross-checks you ran and
   their results, and what (if anything) remains uncertain or illegible.
Never present an inference as an observation, and never let a Low-confidence read
sit unmarked next to High-confidence ones.

## Tips for hostile images
- **Faint / low-contrast scans**: `zoom.py --enhance`; read light-on-light and
  dark-on-dark regions separately.
- **Rotated / skewed**: prep applies EXIF orientation, but content skew remains —
  note it and read along the actual text baseline.
- **Huge images (10+ MP)**: tiles will be many; read them all, but prioritize the
  region map from Step 2 for zoom budget.
- **Repeating patterns / grids**: use the tile boxes as a coordinate frame so you
  don't lose your place or double-count.
- **Compression artifacts (heavy JPG)**: distinguish true edges from blocky
  artifacts; don't over-read JPEG noise as content.
- **OCR on synthetic diagrams**: Windows built-in OCR struggles with small
  diagram labels (MAC addresses, port numbers, directional arrows). Always
  prefer the SVG source when one exists. For pure raster images, combine OCR
  output with positional context from the tile `box` coordinates to reconstruct
  label–object relationships.

## Done means
`meta.json` exists and was read; every tile was read (when `downsampled=True`)
OR `ocr.py` was run and its output was cross-checked against available source
files when vision is unavailable; every decision-critical region was zoomed (or
flagged as inaccessible); every reported claim survived the Step 6 falsification
pass and is confidence-tagged; cross-checks are recorded; and anything illegible
is labeled as such rather than invented.
