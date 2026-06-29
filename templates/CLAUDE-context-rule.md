## HARD RULE — Context library must stay current (Stoa Context Layer)

At the end of EVERY session, and before EVERY push, the `/context` library MUST reflect
the current state of this repo:

- `context/manifest.yaml` — bump `context_version` and set `last_updated` to today.
- `context/{ARCHITECTURE,API,DECISIONS,GOTCHAS}.md` — update whatever the change touched.
- `context/admin/*` — references only; NEVER commit a real secret value (the CI gate blocks it).

A PR into `main` will FAIL the `Context Check` workflow if code changed without a
corresponding `/context` update, if `manifest.yaml` is invalid, or if a secret is detected.
See `Stoa-Group/stoa-context` → `STANDARD.md`.
