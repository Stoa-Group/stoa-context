from pathlib import Path

from tools.sync_context import sync_repo_context


def _make_repo(tmp_path):
    repo = tmp_path / "myrepo"
    ctx = repo / "context" / "admin"
    ctx.mkdir(parents=True)
    (repo / "context" / "manifest.yaml").write_text("project: myrepo\n")
    (repo / "context" / "ARCHITECTURE.md").write_text("# arch\n")
    (repo / "context" / "admin" / "OPS.md").write_text("# ops\n")
    return repo


def test_sync_copies_context_tree_into_store(tmp_path):
    repo = _make_repo(tmp_path)
    store = tmp_path / "store"
    store.mkdir()
    written = sync_repo_context(repo, store, "Stoa-Group/myrepo")

    dst = store / "projects" / "Stoa-Group__myrepo" / "context"
    assert (dst / "manifest.yaml").read_text() == "project: myrepo\n"
    assert (dst / "admin" / "OPS.md").read_text() == "# ops\n"
    assert any("manifest.yaml" in w for w in written)


def test_sync_replaces_stale_files(tmp_path):
    repo = _make_repo(tmp_path)
    store = tmp_path / "store"
    store.mkdir()
    sync_repo_context(repo, store, "Stoa-Group/myrepo")
    (repo / "context" / "ARCHITECTURE.md").unlink()
    sync_repo_context(repo, store, "Stoa-Group/myrepo")
    dst = store / "projects" / "Stoa-Group__myrepo" / "context"
    assert not (dst / "ARCHITECTURE.md").exists()


def test_sync_raises_when_no_context(tmp_path):
    repo = tmp_path / "norepo"
    repo.mkdir()
    store = tmp_path / "store"
    store.mkdir()
    try:
        sync_repo_context(repo, store, "Stoa-Group/norepo")
        assert False, "expected FileNotFoundError"
    except FileNotFoundError:
        pass
