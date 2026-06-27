---
name: draw-diagram
description: Draw precise, student-readable network diagrams (topologies, packet headers, sequence/timing diagrams, encapsulation stacks, window protocols) as hand-authored SVG following strict layout conventions, then visually verify the render. Use whenever a question, exam, or document needs a figure.
---

# Network Diagrams — Precise SVG Protocol

Diagrams for exams must be unambiguous: a student loses marks because of a sloppy figure, not
because of their understanding. The diagram language here is **SVG, hand-authored** — every
coordinate is explicit and deterministic, it embeds directly into the HTML→PDF pipeline
(/build-pdf), and it renders identically everywhere. Do not use ASCII art in deliverables, and
do not use Mermaid (no renderer on this machine).

## Hard Rules

1. **Plan on paper first.** Before writing any SVG, write a short plan: list of nodes with
   their (x, y) centers on a grid, list of links/arrows with endpoints, list of labels with
   anchor positions. Compute coordinates — never eyeball-and-hope.
2. **Snap to a 20 px grid.** All node centers and connector endpoints on grid points.
   Align rows exactly (same y), space siblings evenly.
3. **No overlaps, ever**: no label may touch another label, a line, or a node outline. Links
   must attach to node *edges* (compute the boundary point), not node centers, so arrowheads
   are visible.
4. **Every element labeled**: every device has a name (R1, S1, Host A); every interface that
   matters has its address next to the correct link end; every link that matters has its rate/
   delay label parallel to it; every header field has name AND bit-width; every timing axis has
   units. A diagram with an unlabeled element the question depends on is broken.
5. **Mandatory visual verification**: after authoring, render to PNG and READ the PNG with the
   Read tool. Check: overlaps, truncated text, arrowheads, alignment, and that the diagram
   matches the question text (same names, same numbers). Fix and re-render until clean —
   minimum one render-and-look cycle, always.

```powershell
python .claude/skills/draw-diagram/scripts/svg_to_png.py "<file.svg>"   # writes <file.svg>.png
```

## Visual conventions (use consistently in every figure)

- Canvas: `viewBox="0 0 W H"`; white background; default 12 px sans-serif
  (`font-family="Segoe UI, Arial, sans-serif"`); black text; ≥20 px margin all around.
- **Devices** (Networks 1 set):
  - Host/PC: rect 80×50, rx=6, fill `#dbeafe`, stroke `#1d4ed8` 2px; name centered inside.
  - Router: circle r=28, fill `#fee2e2`, stroke `#b91c1c` 2px.
  - Switch: rect 90×40, fill `#dcfce7`, stroke `#15803d` 2px.
  - Server: rect 70×80, rx=4, fill `#f3e8ff`, stroke `#7e22ce` 2px, two thin lines inside.
  - Cloud/Internet: ellipse, fill `#f1f5f9`, stroke `#475569`, dashed.
- **Links**: solid 2px black for wired; dashed for wireless/logical. Link properties
  (`10 Mbps, 5 ms`) in a small label offset 6–10 px from the line midpoint, never on the line.
- **Packet flow arrows** (distinct from links!): use `marker-end` arrowheads, stroke `#dc2626`,
  drawn offset from the link so both stay visible; number multi-step flows ①②③.
- **Interface addresses**: 11 px, gray `#374151`, placed near the device end of the link,
  on the outside of the topology.
- **Header layouts**: a row of rects on a common baseline; widths proportional to bit-width
  where feasible; field name inside the rect (shrink font or abbreviate + footnote if narrow);
  bit-width below each field; a bit ruler (0 … 31) above the first row for 32-bit-word formats.
- **Sequence/timing diagrams**: vertical lifelines per host, time flows DOWN with an explicit
  time axis and units; messages are slanted arrows when propagation delay matters (annotate
  RTT/timeout spans with dimension lines); label every arrow (`SYN, seq=42`); show segment
  loss as an arrow ending in a red ×.
- **Color is reinforcement, never the only carrier of meaning** (printers may be grayscale):
  also differentiate by shape, dash pattern, and label.
- Language of labels: match the language of the question text (default English, concise
  technical terms — `R1`, `eth0`, `10.0.1.0/24`); if the user requests Arabic or bilingual
  output, keep device IDs and addresses in Latin script and translate prose labels.

## Templates

`reference/templates.svg.md` contains ready-to-adapt SVG skeletons: two-subnet routed topology,
IPv4 header, TCP 3-way handshake sequence diagram, and a Stop-and-Wait timing diagram with
delay annotation. Start from the closest template; adapt coordinates by computing, not nudging.

## Reusing lecture figures and components

When authoring diagrams for exam questions on specific lecture material, first check
`_extracted/<stem>/figures/` for figures extracted during `/read-material`, and the
Concept Inventory's `Components available for diagram reuse` section. These lecture
figures provide the **exact device styling** students learned from — reuse it.

### Component extraction workflow

1. Read the Concept Inventory's component table to identify available device shapes.
2. For each device type, inspect the source figure via OCR:
   ```powershell
   python .claude/skills/analyze-image/scripts/ocr.py "_extracted/<stem>/figures/<figure.png>" [--json]
   ```
3. Recreate each device as a reusable SVG `<defs>` component matching the lecture's
   exact styling (colors, stroke widths, corner radii, font sizes). For example:

   ```svg
   <!-- After inspecting a lecture figure that uses a blue rounded-rect host -->
   <defs>
     <g id="host-lecture">
       <rect x="0" y="0" width="80" height="50" rx="6" fill="#dbeafe" stroke="#1d4ed8" stroke-width="2"/>
       <text x="40" y="30" text-anchor="middle" font-weight="bold" font-size="12">Host</text>
     </g>
     <g id="switch-lecture">
       <rect x="0" y="0" width="90" height="40" fill="#dcfce7" stroke="#15803d" stroke-width="2"/>
       <text x="45" y="25" text-anchor="middle" font-weight="bold" font-size="12">Switch</text>
     </g>
     <g id="router-lecture">
       <circle cx="28" cy="28" r="28" fill="#fee2e2" stroke="#b91c1c" stroke-width="2"/>
       <text x="28" y="33" text-anchor="middle" font-weight="bold" font-size="12">R</text>
     </g>
   </defs>
   ```

4. Compose new topologies by instantiating these `<use href="#host-lecture" x="..." y="..."/>`
   components — this guarantees every device in every question diagram matches the lecture
   style exactly.

### Full topology reuse

Where the lecture figure's topology or layout directly matches the question concept, adapt
the SVG from the figure rather than drawing from scratch — this ensures students see the
same notation they learned from. If the figure is purely photographic or decorative,
note that and do not attempt to replicate it in SVG.

## Consistency gate

Before a diagram ships inside a question set: every device name, address, rate, and delay in
the figure appears identically in the question text (and vice versa for everything the student
needs). One mismatch = unfair question = rejected.
