# CLAUDE.md — stoa-context

> Stoa Group repo. Org context: `Stoa-Group/stoa-skills` (CLAUDE.md + wiki/).

---
## ⛔ HARD RULE — org wiki: consult BEFORE, update AFTER (locked 2026-07-06, Alec directive)

The org wiki in `Stoa-Group/stoa-skills` → `wiki/` is the shared brain for every agent
(Cowork, claude.ai/code repo sessions, GitHub Actions, the DGX fleet). Working in this
repo:

1. **CONSULT FIRST.** Before touching any Stoa system, read the relevant
   `stoa-skills/wiki/` page — `wiki/agents.md` is the router; the limitations registry
   (`wiki/operations/cloud-session-limitations.md`) probably already documents your
   blocker and its workaround. Never claim missing context, re-derive architecture, or
   re-discover a runbook before checking the wiki. Cite the page you used.
2. **UPDATE AFTER.** If this session learned anything durable — a new service/cron/env
   var/tool, a changed data flow, a new gotcha, an incident diagnosis, a hit
   limitation — update the matching wiki page in stoa-skills IN THE SAME SESSION,
   before declaring the work complete. Rewrite in place with a date tag; land via PR.
   **A discovery that isn't written back to the wiki is an incomplete task.**

This is IN ADDITION to this repo's fix-memoir rule (memoirs = training data; the wiki =
current-state truth). Canonical rule text + enforcement: stoa-skills `CLAUDE.md`
§"⛔ HARD RULE: the org wiki is consulted BEFORE and updated AFTER every workflow".
