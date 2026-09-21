# Contributing to stoa-context

## Branch policy

- This repo has a single long-lived branch: **`main`**. (Several other Stoa repos use a
  `dev` integration branch that PRs land on before a separate `dev → main` promotion PR;
  this repo does not have a `dev` branch, so `main` is both the integration and the
  production branch here.)
- **All changes land via pull request into `main`.** This is enforced by an org-wide
  GitHub ruleset: a PR must exist before a change can merge. It currently requires 0
  approvals, but every `.github/CODEOWNERS`-matched path (which is everything in this
  repo) requests review from `@arovner`.
- **Direct push to `main` is emergency-only.** Repo admins can bypass the PR requirement,
  but this should be the exception, not the workflow — open a PR for normal changes.
- Before opening a PR, run the checks CI will run:
  ```bash
  pip install -e ".[dev]"
  python -m pytest tests/ -q
  ```

## Opening a PR

1. Branch off `main`.
2. Make your change. If you touch `schema/context.schema.json`, `tools/`, or the
   `templates/` skeleton, remember other Stoa repos' `Context Check` CI checks out this
   repo live at `main` — a breaking change here can break that gate org-wide the moment
   it merges.
3. Open the PR against `main`. `@arovner` is requested as reviewer automatically via
   CODEOWNERS.
4. Both CI workflows (`Validate` and `Secret Scan`) must be green before merging.
