# CouncilBot – Compliance Notes (Victoria Local Government Act 2020)

This document summarizes how CouncilBot aligns with key transparency and governance expectations under the Local Government Act 2020 (Vic) and typical council Governance Rules. It is guidance only and not legal advice.

## Principles Mapped to Behaviour

- Public transparency: Posts link to official agendas and minutes (not mirrors). Distinguishes proposed (agenda) vs decided (minutes). Threads contain short summaries only.
- Meeting types: Base posts label Ordinary Council, Delegated Committee, and Special Meetings. Minutes reflect decisions; agendas reflect proposals.
- Confidential information: Bot does not attempt to publish confidential or in‑camera items. Heuristics filter potentially sensitive content from thread bullets (e.g., “confidential”, “in camera”, “legal advice”, “CEO employment”).
- Personal information: Redaction applied to emails and phone numbers in extracted bullet text; avoids posting personal identifiers from community submissions.
- Procurement & contracts: Summaries avoid attaching detailed commercial terms; focus on decision headlines and high-level budget figures present in official documents.
- Copyright/terms: Links to the council’s official website; content is a short, transformative summary.
- Accuracy and clarity: Agenda wording uses “to consider/proposed”, minutes use “adopted/approved/resolved” where applicable.

## Technical Safeguards

- Summary extraction filters and redactions in `src/processors/summarize.py`:
  - Redacts emails and phone numbers in bullets.
  - Skips bullets containing likely confidential/sensitive markers (e.g., “confidential”, “in camera”, “legal advice”, “CEO employment”).
  - Includes all high‑value items (score threshold) except filtered sensitive items.
- Scheduler (planned):
  - Posts one base item per hour with reply thread; rotates councils and enforces per‑council cooldown.
  - If any council has no fresh items, rotation skips cleanly.
  - Optional alerts when a council appears inactive beyond a reasonable window.

## Operator Guidance

- Treat council documents as authoritative. If an agenda and minutes differ, the minutes govern.
- Never imply adoption before minutes confirm the decision.
- If a bullet appears sensitive (e.g., employment matters), prefer general language or omit it.
- Keep posts concise and factual; avoid verbatim copying of large excerpts.

---

This project aims to support transparency while respecting statutory constraints and council processes. If you identify a gap, please open an issue with details and the relevant Governance Rule or Act section.

