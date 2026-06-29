import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import yaml


def _load_manifests(store_dir: Path) -> list[dict]:
    manifests = []
    for mf in sorted((store_dir / "projects").glob("*/context/manifest.yaml")):
        data = yaml.safe_load(mf.read_text()) or {}
        manifests.append(data)
    return manifests


def build_catalog(store_dir: Path) -> dict:
    """Build normalized registries from all projects/*/context/manifest.yaml.

    Returns a dict with keys: projects, apis, data-sources, services, schemas.
    """
    store_dir = Path(store_dir)
    manifests = _load_manifests(store_dir)

    projects = []
    apis = []
    data_sources = defaultdict(list)
    services = defaultdict(list)
    schemas = defaultdict(list)

    for m in manifests:
        repo = m.get("repo", "")
        projects.append({
            "project": m.get("project"),
            "repo": repo,
            "description": m.get("description"),
            "owners": m.get("owners", []),
            "deploy_target": m.get("deploy_target"),
            "systems_touched": m.get("systems_touched", []),
            "context_version": m.get("context_version"),
            "last_updated": m.get("last_updated"),
        })
        for api in m.get("apis_exposed") or []:
            apis.append({"repo": repo, **api})
        for sys_name in m.get("systems_touched") or []:
            data_sources[sys_name].append(repo)
        target = m.get("deploy_target")
        if target:
            services[target].append(repo)
        for schema in m.get("schemas") or []:
            schemas[schema].append(repo)

    return {
        "projects": projects,
        "apis": apis,
        "data-sources": dict(data_sources),
        "services": dict(services),
        "schemas": dict(schemas),
    }


def write_catalog(store_dir: Path) -> list[str]:
    """Build the catalog and write catalog/*.json into the store. Returns paths written."""
    store_dir = Path(store_dir)
    cat = build_catalog(store_dir)
    out_dir = store_dir / "catalog"
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for key, value in cat.items():
        path = out_dir / f"{key}.json"
        path.write_text(json.dumps(value, indent=2, sort_keys=True, default=str) + "\n")
        written.append(str(path.relative_to(store_dir)))
    return written


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Build catalog/*.json from the store.")
    parser.add_argument("store_dir", type=Path)
    args = parser.parse_args(argv)
    written = write_catalog(args.store_dir)
    print(f"Wrote {len(written)} catalog file(s): {', '.join(written)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
