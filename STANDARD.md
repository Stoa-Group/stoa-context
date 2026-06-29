# Stoa Context Standard

Every repo in `Stoa-Group` carries a `/context` library. This is the single source of
truth for its shape. The validator (`tools/validate_context.py`) and CI gate enforce it.

## Files

| Path | Tier | Purpose |
|---|---|---|
| `context/manifest.yaml` | read | machine-readable metadata (powers the global catalog) |
| `context/ARCHITECTURE.md` | read | layout, modules, data flow, run/deploy |
| `context/API.md` | read | endpoints, schemas, data sources, locked formulas |
| `context/DECISIONS.md` | read | dated decision log + changelog |
| `context/GOTCHAS.md` | read | landmines, open bugs |
| `context/admin/OPS.md` | admin | env layout, infra, secret *references* (never values) |
| `context/admin/INTERNAL.md` | admin | internal-only decisions |

## manifest.yaml fields

See `schema/context.schema.json` for the authoritative schema. Required:
`project`, `repo`, `description`, `owners`, `deploy_target`, `systems_touched`,
`context_version`, `last_updated`. Optional: `apis_exposed`, `apis_consumed`, `schemas`.

- `deploy_target`: one of `render | domo | github-actions-cron | none`.
- `systems_touched`: subset of `azure-sql | domo | procore | render-services | onedrive | realpage`.
- `last_updated`: ISO date; set to today on every context change.
- `context_version`: integer; bump on every context change.

## The hard rule

Context must be current at the end of every session and before every push. The
`Context Check` CI gate fails a PR into `main` when code changed without a `/context`
update, when `manifest.yaml` is invalid, or when gitleaks detects a secret in `/context`.

## Tiers

Everything outside `context/admin/` is read-tier (org-wide read MCP). Everything inside
`context/admin/` is admin-tier (separate authorized MCP install). Admin content is
references only — a real secret value will be blocked by the gate.

## Aggregator & sync

Per-repo `/context` is aggregated into the PRIVATE `Stoa-Group/stoa-context-store` repo:

- `projects/<owner>__<repo>/context/…` — synced copies (read + admin tiers).
- `catalog/*.json` — generated registries: `projects`, `apis`, `data-sources`, `services`, `schemas`.

Sync is driven by a local crawler (`tools/crawl_and_sync.py`) that uses existing `gh`/`git`
credentials — it discovers repos with a `context/manifest.yaml`, shallow-clones each, copies
`/context` into the store, rebuilds the catalog, and commits/pushes the store. It runs on
demand and from the autonomous loop. (A future GitHub-App push-trigger can replace the crawl
for near-real-time sync without per-repo PATs.)

The store is PRIVATE because it contains the admin tier. Plan 3's MCP serves the read tier
org-wide and the admin tier to authorized installs.
