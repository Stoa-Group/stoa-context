from pathlib import Path

import yaml

from tools.validate_context import (
    check_freshness,
    check_required_files,
    run_checks,
    validate_manifest,
)

SCHEMA = Path("schema/context.schema.json")
FIX = Path("tests/fixtures")


def _load(p):
    return yaml.safe_load(Path(p).read_text())


def test_good_manifest_has_no_schema_errors():
    manifest = _load(FIX / "good_context/context/manifest.yaml")
    assert validate_manifest(manifest, SCHEMA) == []


def test_bad_manifest_reports_missing_and_invalid_fields():
    manifest = _load(FIX / "bad_manifest/context/manifest.yaml")
    errors = validate_manifest(manifest, SCHEMA)
    joined = " ".join(errors)
    assert "repo" in joined
    assert "owners" in joined
    assert "deploy_target" in joined


def test_invalid_last_updated_date_is_rejected():
    manifest = _load(FIX / "good_context/context/manifest.yaml")
    manifest["last_updated"] = "not-a-date"
    errors = validate_manifest(manifest, SCHEMA)
    assert any("last_updated" in e or "date" in e.lower() for e in errors)


def test_required_files_pass_for_good_context():
    ctx = FIX / "good_context/context"
    assert check_required_files(ctx) == []


def test_required_files_report_missing(tmp_path):
    ctx = tmp_path / "context"
    ctx.mkdir()
    (ctx / "manifest.yaml").write_text("project: x\n")
    errors = check_required_files(ctx)
    joined = " ".join(errors)
    assert "ARCHITECTURE.md" in joined
    assert "admin/OPS.md" in joined


def test_freshness_ok_when_context_updated_with_code():
    changed = ["src/server.ts", "context/API.md", "context/manifest.yaml"]
    assert check_freshness(changed) == []


def test_freshness_ok_when_only_context_changed():
    changed = ["context/DECISIONS.md"]
    assert check_freshness(changed) == []


def test_freshness_ok_when_nothing_relevant_changed():
    changed = ["README.md", ".gitignore"]
    assert check_freshness(changed) == []


def test_freshness_fails_when_code_changed_but_context_did_not():
    changed = ["src/server.ts", "package.json"]
    errors = check_freshness(changed)
    assert len(errors) == 1
    assert "context" in errors[0].lower()


def test_freshness_ignores_lockfiles_and_changelog():
    assert check_freshness(["package-lock.json", "CHANGELOG.md", "poetry.lock"]) == []


def test_run_checks_passes_on_good_context():
    code, messages = run_checks(
        repo_root=FIX / "good_context",
        changed_files=["context/API.md"],
        schema_path=SCHEMA,
    )
    assert code == 0, messages


def test_run_checks_fails_on_bad_manifest():
    code, messages = run_checks(
        repo_root=FIX / "bad_manifest",
        changed_files=["context/manifest.yaml"],
        schema_path=SCHEMA,
    )
    assert code == 1
    assert any("repo" in m for m in messages)


def test_run_checks_reports_empty_manifest(tmp_path):
    ctx = tmp_path / "context"; ctx.mkdir(); (ctx / "manifest.yaml").write_text("\n")
    # create the other required files so only the manifest-empty path is exercised
    for n in ["ARCHITECTURE.md","API.md","DECISIONS.md","GOTCHAS.md"]:
        (ctx / n).write_text("# x\n")
    (ctx / "admin").mkdir(); (ctx / "admin/OPS.md").write_text("# x\n"); (ctx / "admin/INTERNAL.md").write_text("# x\n")
    code, messages = run_checks(repo_root=tmp_path, changed_files=["context/manifest.yaml"], schema_path=SCHEMA)
    assert code == 1
    assert any("empty" in m.lower() for m in messages)


def test_template_context_has_all_required_files():
    assert check_required_files(Path("templates/context")) == []


def test_template_manifest_matches_schema_shape():
    manifest = _load("templates/context/manifest.yaml")
    errors = validate_manifest(manifest, SCHEMA)
    # The template uses REPLACE_ME placeholders but must be schema-valid in shape.
    assert errors == [], errors
