# stoa-context

The Stoa Context Layer: the standard, validator, and scaffolding for per-repo `/context`
libraries, plus (later) the global catalog and MCP feed.

## Install the Kit into a repo

    python tools/scaffold_context.py /path/to/cloned/repo --templates templates

## Run the gate locally

    python tools/validate_context.py --repo-root /path/to/repo \
      --schema schema/context.schema.json \
      --changed-files "$(git -C /path/to/repo diff --name-only origin/main...HEAD)"

See `STANDARD.md` for the full specification.
