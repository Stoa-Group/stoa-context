import argparse
import shutil
import sys
from pathlib import Path


def _slug(repo_name: str) -> str:
    """Stoa-Group/myrepo -> Stoa-Group__myrepo (filesystem-safe project dir)."""
    return repo_name.replace("/", "__")


def sync_repo_context(repo_dir: Path, store_dir: Path, repo_name: str) -> list[str]:
    """Copy repo_dir/context into store_dir/projects/<slug>/context, replacing any
    previous copy so deletions propagate. Returns the list of files written.
    Raises FileNotFoundError if the repo has no context/ directory.
    """
    repo_dir = Path(repo_dir)
    store_dir = Path(store_dir)
    src = repo_dir / "context"
    if not src.is_dir():
        raise FileNotFoundError(f"{repo_name}: no context/ directory at {src}")

    dst = store_dir / "projects" / _slug(repo_name) / "context"
    if dst.exists():
        shutil.rmtree(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, dst)

    return [str(p.relative_to(store_dir)) for p in dst.rglob("*") if p.is_file()]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Sync one repo's /context into the store.")
    parser.add_argument("repo_dir", type=Path)
    parser.add_argument("store_dir", type=Path)
    parser.add_argument("repo_name", help="e.g. Stoa-Group/myrepo")
    args = parser.parse_args(argv)
    written = sync_repo_context(args.repo_dir, args.store_dir, args.repo_name)
    print(f"Synced {len(written)} file(s) for {args.repo_name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
