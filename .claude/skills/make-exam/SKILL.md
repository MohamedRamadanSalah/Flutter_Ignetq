---
name: make-exam
description: End-to-end pipeline — ingest lecture files, research, author professor-grade Networks questions with diagrams, and deliver a polished PDF. Use when the user provides lecture material and wants a complete quiz/exam/question-bank PDF.
---

# Make Exam — End-to-End Pipeline with Hard Gates

This orchestrates the four specialist skills **in order**. Each stage has a gate; a stage may
not start until the previous gate's artifacts exist. Skipping stages is what produces shallow
questions and wrong answer keys — do not skip, even under time pressure, even for "just a few
quick questions". If the user explicitly orders a stage skipped, comply but state plainly what
quality guarantee is lost.

## Stage 0 — Contract
Establish (from the user's message; only ask if genuinely undecidable): which lecture file(s);
number of questions and mix (MCQ / open / calculation); difficulty profile; language (English /
Arabic / bilingual); student-only PDF, instructor PDF with key, or both. Defaults: 10 questions
(5 MCQ, 3 calculation, 2 analysis), mixed difficulty, English, instructor PDF with key.
State your assumptions in one line and proceed — do not stall on questions the defaults cover.

## Stage 1 — Ingest (skill: read-material)
Run the full protocol on every provided file.
**Gate:** `coverage.md` (every page read) + `concepts.md` exist.

## Stage 2 — Research (skill: research)
Verify, deepen, build the misconception bank.
**Gate:** `research.md` exists; all answer-key-bound claims confirmed; misconception bank
covers every MCQ topic.

## Stage 3 — Author (skill: make-questions)
Write questions + full answer key; pass the 10-point quality gate; re-verify all arithmetic.
**Gate:** every question passes; arithmetic independently re-solved (Python for subnetting).

## Stage 4 — Diagrams (skill: draw-diagram)
For every question that references a figure: author SVG per conventions, render, visually
verify, check figure↔text consistency.
**Gate:** each diagram's PNG has been visually read and matches its question exactly.

## Stage 5 — Publish (skill: build-pdf)
Build from `templates/exam.html`, render, stamp page numbers, visual page-by-page review.
**Gate:** clean visual pass of the final PDF.

## Stage 6 — Deliver
Report to the user: the PDF path(s); the question mix and Bloom distribution actually achieved;
any lecture discrepancies found during research; anything assumed at Stage 0.
