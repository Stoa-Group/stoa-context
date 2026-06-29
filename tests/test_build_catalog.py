from pathlib import Path

from tools.build_catalog import build_catalog

STORE = Path("tests/fixtures/store_sample")


def test_projects_registry_lists_every_project():
    cat = build_catalog(STORE)
    names = {p["project"] for p in cat["projects"]}
    assert names == {"example-service", "other-app"}


def test_services_registry_groups_by_deploy_target():
    cat = build_catalog(STORE)
    services = cat["services"]
    assert set(services["render"]) == {"Stoa-Group/example-service"}
    assert set(services["domo"]) == {"Stoa-Group/other-app"}


def test_data_sources_maps_system_to_repos():
    cat = build_catalog(STORE)
    ds = cat["data-sources"]
    assert set(ds["azure-sql"]) == {"Stoa-Group/example-service", "Stoa-Group/other-app"}
    assert set(ds["domo"]) == {"Stoa-Group/other-app"}


def test_apis_registry_collects_exposed_endpoints():
    cat = build_catalog(STORE)
    apis = cat["apis"]
    paths = {(a["repo"], a["method"], a["path"]) for a in apis}
    assert ("Stoa-Group/example-service", "GET", "/api/v1/example") in paths


def test_schemas_registry_maps_schema_to_repos():
    cat = build_catalog(STORE)
    schemas = cat["schemas"]
    assert set(schemas["example.Widget"]) == {"Stoa-Group/example-service", "Stoa-Group/other-app"}


import json as _json
from tools.build_catalog import write_catalog


def test_write_catalog_emits_json_files(tmp_path):
    import shutil
    store = tmp_path / "store"
    shutil.copytree(STORE, store)
    written = write_catalog(store)
    assert (store / "catalog" / "projects.json").is_file()
    data = _json.loads((store / "catalog" / "projects.json").read_text())
    assert {p["project"] for p in data} == {"example-service", "other-app"}
    assert any("catalog/services.json" in w for w in written)
