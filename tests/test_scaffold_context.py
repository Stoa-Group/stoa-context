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
