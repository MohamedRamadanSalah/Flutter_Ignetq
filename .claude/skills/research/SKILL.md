---
name: research
description: Conduct rigorous online research on computer-networking topics before writing exam questions — authoritative-source-first (RFCs, standards, canonical textbooks), with claim verification and a written research log. Use after read-material and before make-questions, or whenever lecture content needs verification or enrichment.
---

# Networking Research — Strict Protocol

Purpose: deepen and verify understanding beyond the slides so that questions are technically
unimpeachable, distractors reflect *real* student misconceptions, and scenarios are realistic.
Research output feeds question writing — sloppy research becomes a wrong answer key.

## Hard Rules

1. **Every technical claim that will appear in a question or answer key must be verified
   against (a) the lecture material or (b) at least one authoritative source.** A claim you
   "remember" from training counts as UNVERIFIED until checked.
2. **When the lecture and an external source disagree, the LECTURE WINS for question scope and
   notation** (students are examined on what they were taught) — but record the discrepancy in
   the research log and flag it to the user. Never silently test students on material that
   contradicts their slides.
3. Prefer primary/authoritative sources, in this order:
   - **RFCs** (rfc-editor.org, datatracker.ietf.org) for protocol behavior — TCP (RFC 9293),
     IP (RFC 791), UDP (RFC 768), HTTP (RFC 9110-9114), DNS (RFC 1034/1035), DHCP (RFC 2131),
     ARP (RFC 826), ICMP (RFC 792), CIDR (RFC 4632)…
   - **IEEE standards** for 802.3 Ethernet, 802.11 Wi-Fi, 802.1Q VLANs
   - **Canonical textbooks**: Kurose & Ross *Computer Networking: A Top-Down Approach*;
     Tanenbaum & Wetherall *Computer Networks*; Peterson & Davie; Stevens *TCP/IP Illustrated*
   - University course pages (MIT, Stanford, CMU, UW) for how concepts are *taught and examined*
   - Reputable vendor docs (Cisco, Cloudflare Learning Center, RIPE/APNIC) for practice
   - Avoid as sole sources: SEO content farms, AI-generated articles, forum answers
4. **Numbers must be exact**: header sizes in bytes, field widths in bits, default timers, port
   numbers, address ranges. Verify each one — these are exactly where plausible-but-wrong
   answers come from.
5. Search at least two independent angles before concluding; if sources conflict, dig until
   resolved or report the conflict honestly.

## Procedure

1. **Plan**: from the Concept Inventory's concepts + ambiguities, write a numbered list of
   research questions. Three categories:
   - *Verify*: claims/numbers from the lecture to confirm
   - *Deepen*: the why/edge-cases behind each major concept (needed for analysis questions)
   - *Misconceptions*: search literally for "common misconceptions <topic>", "students confuse
     <X> with <Y>", instructor exam banks, and pedagogy papers — this is the raw material for
     high-quality distractors
2. **Search & fetch**: use WebSearch to locate, WebFetch to actually read. Never cite a page
   you only saw as a search-result snippet.
3. **Log**: write `_extracted/<stem>/research.md`:

```markdown
# Research Log — <lecture name>
## Verified claims
| # | Claim | Verdict (confirmed/corrected/unresolved) | Source (URL) |
## Deepened concepts
Per concept: what the lecture said → what fuller picture research adds → exam-relevant nuance.
## Misconception bank
| # | Misconception students hold | The correct understanding | Why students believe it | Source |
## Lecture discrepancies
Anything where slides conflict with authoritative sources — to be flagged to the user.
## Realistic scenario material
Concrete parameters found (typical RTTs, link speeds, MTU 1500, real CIDR blocks…) usable in
scenario questions.
```

## Done means
`research.md` exists; every claim destined for an answer key is marked confirmed; the
misconception bank has entries for every topic that will get multiple-choice questions; any
lecture discrepancies are listed for the user.
