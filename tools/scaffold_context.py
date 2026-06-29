import argparse
import shutil
import sys
from pathlib import Path

RULE_MARKER = "HARD RULE — Context library"


def scaffold(target_repo: Path, templates_dir: Path) -> list[str]:
    """Install the Context Kit into target_repo. Idempotent; never clobbers existing files.

    Returns the list of repo-relative paths that were created or modified.
    """
    target_repo = Path(target_repo)
    templates_dir = Path(templates_dir)
    touched: list[str] = []

    # 1. Copy the /context skeleton (skip files that already exist).
    src_ctx = templates_dir / "context"
    for src in src_ctx.rglob("*"):
        if src.is_dir():
            continue
        rel = src.relative_to(src_ctx)
        dst = target_repo / "context" / rel
        if dst.exists():
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
        touched.append(f"context/{rel.as_posix()}")

    # 2. Copy the CI workflow (skip if present).
    wf_dst = target_repo / ".github" / "workflows" / "context-check.yml"
    if not wf_dst.exists():
        wf_dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(templates_dir / "workflows" / "context-check.yml", wf_dst)
        touched.append(".github/workflows/context-check.yml")

    # 3. Append the CLAUDE rule block exactly once.
    rule = (templates_dir / "CLAUDE-context-rule.md").read_text()
    claude = target_repo / "CLAUDE.md"
    existing = claude.read_text() if claude.exists() else ""
    if RULE_MARKER not in existing:
        # ensure a blank line separates existing CLAUDE.md content from the appended rule block
        sep = "" if existing.endswith("\n") or existing == "" else "\n"
        claude.write_text(existing + sep + ("\n" if existing else "") + rule)
        touched.append("CLAUDE.md")

    return touched


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Install the Stoa Context Kit into a repo.")
    parser.add_argument("target_repo", type=Path)
    parser.add_argument("--templates", default=Path("templates"), type=Path)
    args = parser.parse_args(argv)
    touched = scaffold(args.target_repo, args.templates)
    print(f"Scaffolded {len(touched)} file(s):")
    for t in touched:
        print(f"  + {t}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
