---
name: build-pdf
description: Produce a polished, print-quality PDF (exam, question set, handout) from structured content via HTML + print CSS rendered with headless Edge, with page numbering and a mandatory visual self-review of every page. Use whenever the user wants a PDF deliverable.
---

# PDF Production — Design & Verification Protocol

A PDF that *looks* unprofessional undermines trust in its content, and a PDF you never looked
at after generating WILL contain layout bugs (split questions, overflowing SVGs, orphan
headings). Both problems are solved here: a proven template + a mandatory visual review loop.

## Pipeline

1. **Author HTML** starting from `templates/exam.html` (already styled: A4 `@page`, cover
   header, instructions band, question cards that never split across pages, figure/choice/
   table styles, answer key forced onto a fresh page). Replace the `{{PLACEHOLDERS}}` and the
   sample question blocks; keep the CSS unless the user requests a different look.
   - Embed diagrams as **inline SVG** (from /draw-diagram) inside `<figure class="diagram">` —
     never as ASCII art, and avoid external image links (headless rendering may miss them;
     if you must use images, use absolute `file:///` URIs and increase the virtual-time budget).
2. **Render**:
   ```powershell
   python .claude/skills/build-pdf/scripts/html_to_pdf.py "<file.html>" -o "<file.pdf>"
   ```
3. **Stamp page numbers** (Chromium cannot render CSS margin-box page numbers — do not try;
   this post-process is the supported way):
   ```powershell
   python .claude/skills/build-pdf/scripts/stamp_pagenum.py "<file.pdf>" --footer "Networks 1 — <title>"
   ```
4. **Visual review — mandatory, never skip.** Read the generated PDF with the Read tool
   (it renders pages visually; use `pages` for long documents). Inspect EVERY page for:
   - questions or figures split across a page break (fix: the element is missing
     `break-inside: avoid`, or is genuinely taller than a page → shrink the figure)
   - SVG overflow/clipping, labels unreadable at print size (text inside figures must be
     ≥ 9 pt effective — scale the figure, don't let text shrink below that)
   - orphan section headings at a page bottom; widowed single lines
   - the answer key starting on its own page; page numbers present and correct
   - typography: no double spaces, consistent marks formatting, no `{{PLACEHOLDER}}` left over
5. **Fix and re-render** until a full pass is clean. Report to the user only after the visual
   pass succeeds — "the script ran" is not "the PDF is good".

## Design rules

- One typeface family (Segoe UI), two accent colors max; restraint reads as professional.
- 11 pt body, 1.45 line height, generous margins — never cram to save pages.
- Every question shows its marks; every figure has a number and caption; questions reference
  figures by number ("Figure 2"), never by position ("the diagram below" breaks under reflow).
- Question metadata pills (Bloom level, difficulty) are for instructor copies; strip them from
  the student copy if the user asks for one (and then also strip the answer-key section into a
  separate PDF: student version and instructor version are two renders of the same HTML with
  sections removed, not two documents maintained by hand).
- For Arabic/bilingual output: add `dir="rtl"` on the relevant elements and a suitable font
  (`"Segoe UI", "Traditional Arabic", "Arial"`); keep addresses, device IDs, and math LTR
  inside `<bdi>`/`<span dir="ltr">`.
