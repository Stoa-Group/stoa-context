import argparse
import datetime
import json
import sys
from pathlib import Path

import yaml
from jsonschema import Draft7Validator, FormatChecker


def _coerce_dates(obj):
    """Recursively convert datetime.date/datetime values to ISO strings so
    jsonschema sees strings rather than Python date objects (PyYAML parses
    bare YYYY-MM-DD values as datetime.date automatically)."""
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    if isinstance(obj, datetime.date):
        return obj.isoformat()
    if isinstance(obj, dict):
        return {k: _coerce_dates(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_coerce_dates(v) for v in obj]
    return obj


def validate_manifest(manifest: dict, schema_path: Path) -> list[str]:
    """Return a list of human-readable schema errors (empty == valid)."""
    schema = json.loads(Path(schema_path).read_text())
    manifest = _coerce_dates(manifest)
    validator = Draft7Validator(schema, format_checker=FormatChecker())
    errors = []
    for err in sorted(validator.iter_errors(manifest), key=lambda e: list(e.path)):
        loc = ".".join(str(p) for p in err.path) or "(root)"
        errors.append(f"{loc}: {err.message}")
    return errors


REQUIRED_FILES = [
    "manifest.yaml",
    "ARCHITECTURE.md",
    "API.md",
    "DECISIONS.md",
    "GOTCHAS.md",
    "admin/OPS.md",
    "admin/INTERNAL.md",
]


def check_required_files(context_dir: Path) -> list[str]:
    """Return errors for any required /context file that is missing."""
    context_dir = Path(context_dir)
    errors = []
    for rel in REQUIRED_FILES:
        if not (context_dir / rel).is_file():
            errors.append(f"missing required file: context/{rel}")
    return errors


# Non-source files whose change alone does NOT require a /context update. Tunable; broaden as new repo conventions appear.
# Stored lowercased; membership is compared case-insensitively (CI runs on Linux,
# where README.MD / readme.md must be treated the same as README.md).
IGNORED_FILES = {
    "readme.md",
    "license",
    "license.md",
    ".gitignore",
    ".gitleaks.toml",
    "changelog.md",
    "makefile",
    "package.json",
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "pyproject.toml",
    "poetry.lock",
    "requirements.txt",
    ".domoignore",
    ".editorconfig",
    ".prettierrc",
}
IGNORED_PREFIXES = ("context/", ".github/", "docs/")


def check_freshness(changed_files: list[str]) -> list[str]:
    """Fail if code changed in this PR but /context was not touched.

    `changed_files` is the list of repo-relative paths changed vs the PR base.
    """
    context_changed = any(f.startswith("context/") for f in changed_files)
    code_changed = any(
        f.lower() not in IGNORED_FILES and not f.startswith(IGNORED_PREFIXES)
        for f in changed_files
    )
    if code_changed and not context_changed:
        return ["code changed but /context was not updated (hard rule violation)"]
    return []


def run_checks(repo_root: Path, changed_files: list[str], schema_path: Path):
    """Run all gate checks. Returns (exit_code, messages)."""
    repo_root = Path(repo_root)
    context_dir = repo_root / "context"
    messages: list[str] = []

    file_errors = check_required_files(context_dir)
    messages += file_errors

    manifest_path = context_dir / "manifest.yaml"
    if manifest_path.is_file():
        manifest = yaml.safe_load(manifest_path.read_text()) or {}
        if not manifest:
            messages.append("manifest: context/manifest.yaml is empty or unparseable")
        messages += [f"manifest: {e}" for e in validate_manifest(manifest, schema_path)]
    else:
        messages.append("manifest: context/manifest.yaml not found")

    messages += check_freshness(changed_files)

    return (1 if messages else 0), messages


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Validate a repo's /context library.")
    parser.add_argument("--repo-root", default=".", type=Path)
    parser.add_argument("--schema", default=Path("schema/context.schema.json"), type=Path)
    parser.add_argument(
        "--changed-files",
        default="",
        help="newline- or comma-separated list of changed paths vs PR base",
    )
    args = parser.parse_args(argv)

    raw = args.changed_files.replace(",", "\n")
    changed = [line.strip() for line in raw.splitlines() if line.strip()]

    code, messages = run_checks(args.repo_root, changed, args.schema)
    if messages:
        print("Context gate FAILED:")
        for m in messages:
            print(f"  - {m}")
    else:
        print("Context gate PASSED.")
    return code


if __name__ == "__main__":
    sys.exit(main())
