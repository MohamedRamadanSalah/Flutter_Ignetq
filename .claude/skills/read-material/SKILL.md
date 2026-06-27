---
name: read-material
description: Rigorously ingest lecture material (PDF, PPTX, DOCX) before any question writing. Extracts text, renders every page/slide as an image, forces a visual read of all graphics, and produces a Concept Inventory. Use whenever the user provides lecture files or asks to read/study course material.
---

# Read Lecture Material — Strict Ingestion Protocol

You are reading material that students will be examined on. A misread slide becomes a wrong
question, which is a serious failure. Text extraction ALONE IS NEVER SUFFICIENT for networking
material — the meaning usually lives in the diagrams (topologies, packet headers, handshakes,
timing diagrams) that extraction cannot capture.

## Hard Rules (non-negotiable)

1. **NEVER answer questions about, summarize, or write exam questions from a file you have not
   fully ingested with this protocol.** "I skimmed the text" is not ingestion.
2. **NEVER skip a page flagged `LOW_TEXT` or `HAS_GRAPHICS`** — those pages must be read
   visually with the Read tool on the rendered PNG. When the model cannot read image files
   (returns "Cannot read image"), run `ocr.py` from the `analyze-image` skill instead and
   cross-reference with the extracted text and any available source files (PPTX/DOCX/SVG).
3. **NEVER guess at a figure's content from its caption or surrounding text.** Look at it or
   OCR it. If OCR produces garbled text (common for diagram labels), note the uncertainty
   and tag claims as [M] or [L] confidence.
4. If extraction fails or a page renders unreadably, say so explicitly. Never fill gaps with
   plausible-sounding networking knowledge and present it as "from the lecture".
5. Keep lecture content and your own background knowledge separated at all times. The Concept
   Inventory records only what the material actually says — including its specific notation,
   variable names, and simplifications, even if a textbook would phrase it differently.

## Procedure

### Step 1 — Extract
```powershell
python .claude/skills/read-material/scripts/extract.py "<file>" --outdir _extracted --extract-figures
```
This produces, under `_extracted/<stem>/`:
- `manifest.json` — per-page stats and flags
- `text.md` — extracted text with page markers (including PPTX speaker notes)
- `pages/pNNN.png` — raster image of every page/slide
- `figures/` — every embedded image extracted as a standalone PNG/JPG file
- `figures.json` — index of extracted figures with page/slide references

Always use `--extract-figures` so diagrams and images from the lecture are available
as reusable components when drawing diagrams for questions.

If the script errors on a PDF, the file may be scanned/image-only: the PNGs are still produced —
read them all visually. (Note: the Read tool can also read PDFs directly with the `pages`
parameter; use that as a cross-check, not a substitute for this protocol.)

### Step 2 — Full text pass
Read `text.md` in full (in chunks if large). While reading, build a running list of: every term
defined, every protocol named, every formula, every numeric example, every claim that sounds
testable.

### Step 3 — Visual pass (the part weak readers skip — you will not)
Read the manifest's `pages_requiring_visual_read` list. **Read every listed PNG with the Read
tool.** For lecture decks, also visually read the first slide, the last slide, and any slide
whose extracted text mentions a figure ("as shown", "diagram", "topology", "header format",
"see figure"). For each figure, record in your notes:
- What the figure depicts (topology? header layout? sequence/timing diagram? graph?)
- Every label, field name, numeric value, and axis in it
- What concept the figure is teaching that the text alone does not state

**When the model cannot read image files**, replace Step 3 with this fallback:

```powershell
python .claude/skills/analyze-image/scripts/ocr.py "_extracted/<stem>/pages/pNNN.png" [--json]
```

Run this on **every** page flagged `LOW_TEXT` or `HAS_GRAPHICS`, plus any page whose
extracted text references a figure. For diagrams rendered from SVG (under `output/`), read
the `.svg` source directly instead — it is always more accurate than OCR.

After OCR extraction, cross-reference the OCR text against the extracted `text.md`:

### Step 3b — Figure extraction & component inventory (critical for question diagram reuse)
Read `figures.json` from the extraction output. For each figure entry, note its page and
filename. Run OCR to understand its content:

```powershell
python .claude/skills/analyze-image/scripts/ocr.py "_extracted/<stem>/figures/<figure.png>" [--json]
```

For each figure that contains reusable network devices (router, switch, host, server,
cloud, link styles), extract a **component inventory** in the Concept Inventory:

```
## Components available for diagram reuse
| Component | Style (lecture) | Found in figure | SVG template status |
|---|---|---|---|
| Router | Circle, red outline, bold label | p032_fig2 | needs authoring |
| Switch | Rect, green outline, labeled ports | p033_fig2 | needs authoring |
| Host/PC | Rounded rect, blue outline | p032_fig2 | needs authoring |
| Link style | Solid 2px black, interface label gray | p032_fig2 | needs authoring |
```

When you later author questions with `/draw-diagram`, use this component inventory to
recreate each device shape as an SVG element matching the lecture's exact styling —
students should see the same router shape and switch icon they learned from. The
extracted PNG figures serve as visual reference for colors, sizes, and layout patterns;
the SVG components you author implement them.

Link each extracted figure to the concepts it illustrates in the Concept Inventory
(Step 5). Add a `figures_referenced` section listing which figures map to which
testable concepts, and which device components can be reused from each figure.
- Text that appears in both sources is **[H]** confidence.
- Text unique to OCR (diagram labels, figure annotations not in text.md) is **[M]** — it
  came from the image but may be garbled by OCR.
- Text that OCR splits or mangles (e.g., "Appli ation" for "Application", "protcx:ol" for
  "protocol") is reconstructed from context and tagged **[M]**.
- Any value that cannot be resolved (illegible numbers, truncated edges) is marked **[L]**
  or "illegible" — never invented.

### Step 4 — Coverage log (mandatory output)
Write `_extracted/<stem>/coverage.md` containing a table: one row per page/slide with columns
`page | read-text? | read-visually? | ocr-fallback? | content summary (≤15 words)`. Every row
must have at least one "yes" in `read-text?`, `read-visually?`, or `ocr-fallback?`. If any row
would be "no/no/no", go back and read it. Mark the method used: "visual" for Read tool reads,
"ocr" for `ocr.py` fallback, "svg" for SVG source reads. This log is your proof of coverage —
produce it before claiming the material is ingested.

### Step 5 — Concept Inventory (mandatory output)
Write `_extracted/<stem>/concepts.md`:

```markdown
# Concept Inventory — <lecture name>
## Scope
What the lecture covers and explicitly does NOT cover (so questions never exceed scope).
## Concepts
For each concept: name | page(s) | depth taught (mentioned / explained / derived / worked-example)
## Definitions & notation (verbatim)
Exact definitions and symbols AS THE LECTURE WRITES THEM (e.g., if it uses L/R for
transmission delay, keep L/R).
## Formulas & worked examples
Each formula with its variables; each numeric example with its numbers and result.
## Figures
Each figure: page, what it shows, every label/value on it.
## Testable claims
Cause-effect statements, comparisons, trade-offs, "note that…" remarks — prime question material.
## Ambiguities / gaps
Anything unclear, possibly erroneous in the slides, or needing research to firm up.
```

The `depth taught` column is what keeps later questions fair: a concept merely *mentioned* may
only support a recall question; *explained* supports comprehension; *derived / worked-example*
supports calculation and analysis questions.

## Done means
Both `coverage.md` and `concepts.md` exist, every page row shows coverage, and you can state
the lecture's scope boundary in one sentence.
