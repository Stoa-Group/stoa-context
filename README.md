# stoa-context

## What this is

`stoa-context` is the **Stoa Context Layer**: the standard, validator, and scaffolding
tool for the `/context` library that every repo in the `Stoa-Group` org is expected to
carry. The idea is simple — coding agents (and new human developers) working in any Stoa
repo should be able to read a small, predictable set of files under `/context` and get an
accurate, current picture of that repo: what it does, how it's built, what it talks to,
and what to watch out for. This repo defines what those files must contain
(`STANDARD.md` + `schema/context.schema.json`), ships the tooling that installs and
enforces that shape (`tools/`), and provides the copy-paste templates (`templates/`) used
to scaffold a new `/context` library into a repo. It does not itself run a service — it's
a schema + a set of scripts that other repos' CI depends on directly.

## Tech stack

- **Python 3.11+** (CI runs 3.12), packaged with `setuptools` (see `pyproject.toml`)
- **PyYAML** — parsing `context/manifest.yaml`
- **jsonschema** (Draft 7, with format checking) — validating the manifest against
  `schema/context.schema.json`
- **pytest** — test suite (`tests/`), installed via the `dev` extra
- **gitleaks** — secret scanning of `/context` content (config in `.gitleaks.toml`)
- **GitHub CLI (`gh`)** — used by `tools/crawl_and_sync.py` to discover repos and by the
  scaffolded `Context Check` workflow to check out this repo
- **TruffleHog** — verified-secret scanning in this repo's own CI (`secret-scan.yml`)

## Architecture

| Path | What it is |
|---|---|
| `STANDARD.md` | The spec: which `/context` files are required, what goes in `manifest.yaml`, the read/admin tier split, and the "context must be current" hard rule |
| `schema/context.schema.json` | JSON Schema (draft-07) that `context/manifest.yaml` must satisfy |
| `templates/context/*` | The blank `/context` skeleton (`ARCHITECTURE.md`, `API.md`, `DECISIONS.md`, `GOTCHAS.md`, `admin/OPS.md`, `admin/INTERNAL.md`, `manifest.yaml`) copied into a target repo |
| `templates/workflows/context-check.yml` | The CI workflow copied into a target repo. On every PR it checks out **this repo at `main`** and runs `tools/validate_context.py` plus a gitleaks scan against that repo's `/context` |
| `templates/CLAUDE-context-rule.md` | The agent-instruction block appended to a target repo's `CLAUDE.md` |
| `tools/scaffold_context.py` | Installs the Kit into a target repo: copies the `/context` skeleton, the CI workflow, and the `CLAUDE.md` rule block — idempotent, never overwrites files that already exist. Also guards `.domoignore` on Domo-app repos so `/context` and `.github/` never ship inside a Domo publish bundle |
| `tools/validate_context.py` | The validator: checks all required `/context` files exist, validates `manifest.yaml` against the schema, and enforces "code changed but `/context` didn't" as a failure. This is the exact script every other Stoa repo's `Context Check` job runs |
| `tools/sync_context.py`, `tools/build_catalog.py`, `tools/crawl_and_sync.py` | A local crawler (not a running service) that discovers org repos with a `context/manifest.yaml` via `gh search code`, shallow-clones each one, copies its `/context` into the private `Stoa-Group/stoa-context-store` repo, and rebuilds JSON catalogs (`projects`, `apis`, `data-sources`, `services`, `schemas`) from all the manifests. Run on demand by whoever operates the store |
| `tests/` | pytest suite covering the validator, scaffolder, sync, and catalog builder, with fixtures under `tests/fixtures/` |

## Local development setup

```bash
git clone https://github.com/Stoa-Group/stoa-context.git
cd stoa-context
pip install -e ".[dev]"
python -m pytest tests/ -q
```

Try the two main tools against a repo on disk:

```bash
# Scaffold the /context skeleton + CI workflow + CLAUDE.md rule into another repo
python tools/scaffold_context.py /path/to/cloned/repo --templates templates

# Run the same gate CI runs, against that repo's changes
python tools/validate_context.py --repo-root /path/to/repo \
  --schema schema/context.schema.json \
  --changed-files "$(git -C /path/to/repo diff --name-only origin/main...HEAD)"
```

## Environment variables

None are required to install the package, run the tests, or run the validator/scaffolder
— there is no `.env` file and no code in this repo reads one. `tools/crawl_and_sync.py`
shells out to the `gh` and `git` CLIs, so it needs those already authenticated on your
machine; it does not read any secret from the environment itself.

## CI/CD

- **`.github/workflows/validate.yml`** — runs on every push and pull request. One job
  byte-compiles all Python and runs the full `pytest` suite (this is the job that keeps
  the validator every other repo's CI depends on actually working). A second job parses
  every `.json` and `.yml`/`.yaml` file in the repo, to catch a malformed schema or
  template before it can silently break another repo's `Context Check` gate.
- **`.github/workflows/secret-scan.yml`** — runs on every push and pull request, scanning
  the diff with TruffleHog (verified-secrets only) to block committing real credentials.

## Deployment

There is no build or deploy step — merging to `main` doesn't stand up a service. Instead,
`main` is live infrastructure for the rest of the org: the `Context Check` workflow that
`tools/scaffold_context.py` installs into every other Stoa repo checks out
`Stoa-Group/stoa-context` at `ref: main` on every one of that repo's pull requests, and
runs `tools/validate_context.py` and the gitleaks scan straight from that checkout. So a
change merged here takes effect org-wide the next time any repo's `Context Check` runs —
there is no separate release or version pin to update.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for branch policy and how to open a PR.

## Ownership / contact

Stoa Group Data & Technology — arovner@stoagroup.com
