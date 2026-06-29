import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from tools.build_catalog import write_catalog
from tools.sync_context import sync_repo_context


def parse_repos_with_context(raw: list[dict]) -> list[str]:
    """Dedupe + sort repo names from `gh search code` JSON results, skipping malformed items."""
    names = set()
    for item in raw:
        name = (item.get("repository") or {}).get("nameWithOwner")
        if name:
            names.add(name)
    return sorted(names)


def discover_repos_with_context(org: str = "Stoa-Group") -> list[str]:
    """Find repos that contain a context/manifest.yaml via gh code search."""
    out = subprocess.run(
        ["gh", "search", "code", "--owner", org, "filename:manifest.yaml", "path:context",
         "--json", "repository", "--limit", "200"],
        capture_output=True, text=True, check=True,
    ).stdout
    return parse_repos_with_context(json.loads(out or "[]"))


def sync_one(repo_name: str, store_dir: Path) -> bool:
    """Shallow-clone a repo and sync its /context into the store. Returns True on success."""
    with tempfile.TemporaryDirectory() as tmp:
        clone = Path(tmp) / "repo"
        r = subprocess.run(
            ["git", "clone", "--depth", "1", f"https://github.com/{repo_name}.git", str(clone)],
            capture_output=True, text=True,
        )
        if r.returncode != 0:
            print(f"  ! clone failed for {repo_name}: {r.stderr.strip()}")
            return False
        try:
            written = sync_repo_context(clone, store_dir, repo_name)
            print(f"  + {repo_name}: {len(written)} files")
            return True
        except FileNotFoundError:
            print(f"  - {repo_name}: no context/, skipped")
            return False


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Crawl org repos, sync /context, rebuild catalog.")
    parser.add_argument("store_dir", type=Path, help="local clone of stoa-context-store")
    parser.add_argument("--org", default="Stoa-Group")
    parser.add_argument("--repos", nargs="*", help="explicit repo list (skips discovery)")
    args = parser.parse_args(argv)

    repos = args.repos or discover_repos_with_context(args.org)
    print(f"Syncing {len(repos)} repo(s) into {args.store_dir}")
    for repo in repos:
        sync_one(repo, args.store_dir)

    written = write_catalog(args.store_dir)
    print(f"Catalog rebuilt: {', '.join(written)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
