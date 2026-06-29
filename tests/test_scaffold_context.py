from pathlib import Path

from tools.scaffold_context import scaffold

TEMPLATES = Path("templates")


def test_scaffold_creates_context_workflow_and_claude(tmp_path):
    repo = tmp_path / "somerepo"
    repo.mkdir()
    created = scaffold(repo, TEMPLATES)

    assert (repo / "context" / "manifest.yaml").is_file()
    assert (repo / "context" / "admin" / "OPS.md").is_file()
    assert (repo / ".github" / "workflows" / "context-check.yml").is_file()
    assert (repo / "CLAUDE.md").is_file()
    assert "HARD RULE" in (repo / "CLAUDE.md").read_text()
    assert any("context/manifest.yaml" in c for c in created)


def test_scaffold_is_idempotent_and_does_not_clobber(tmp_path):
    repo = tmp_path / "somerepo"
    repo.mkdir()
    scaffold(repo, TEMPLATES)
    arch = repo / "context" / "ARCHITECTURE.md"
    arch.write_text("# Custom architecture notes\n")
    scaffold(repo, TEMPLATES)
    assert arch.read_text() == "# Custom architecture notes\n"


def test_scaffold_appends_rule_once(tmp_path):
    repo = tmp_path / "somerepo"
    repo.mkdir()
    (repo / "CLAUDE.md").write_text("# Existing CLAUDE\n")
    scaffold(repo, TEMPLATES)
    scaffold(repo, TEMPLATES)
    assert (repo / "CLAUDE.md").read_text().count("HARD RULE — Context library") == 1


def test_scaffold_guards_domoignore_for_domo_repo(tmp_path):
    repo = tmp_path / "domorepo"
    repo.mkdir()
    (repo / "manifest.json").write_text('{"name":"x"}')  # Domo app indicator
    scaffold(repo, TEMPLATES)
    di = (repo / ".domoignore").read_text()
    assert "context/" in di
    assert ".github/" in di


def test_scaffold_appends_to_existing_domoignore_without_dupes(tmp_path):
    repo = tmp_path / "domorepo"
    repo.mkdir()
    (repo / ".domoignore").write_text("node_modules/\ncontext/\n")  # already has context/
    scaffold(repo, TEMPLATES)
    di = (repo / ".domoignore").read_text()
    assert di.count("context/") == 1          # not duplicated
    assert ".github/" in di                    # added
    assert "node_modules/" in di               # preserved


def test_scaffold_skips_domoignore_for_non_domo_repo(tmp_path):
    repo = tmp_path / "plainrepo"
    repo.mkdir()
    scaffold(repo, TEMPLATES)
    assert not (repo / ".domoignore").exists()
