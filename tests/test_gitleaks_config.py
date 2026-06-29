import shutil
import subprocess
from pathlib import Path

import pytest

GITLEAKS = shutil.which("gitleaks")
CONFIG = str(Path(__file__).resolve().parent.parent / ".gitleaks.toml")


@pytest.mark.skipif(GITLEAKS is None, reason="gitleaks not found on PATH")
def test_gitleaks_detects_planted_secret(tmp_path):
    # Synthesize an obviously-fake DDCI token at runtime so no secret-shaped
    # literal is committed to this (public) repo. It still matches the
    # stoa-domo-ddci-token rule: DDCI_ followed by >=20 alphanumerics.
    fake_token = "DDCI_" + ("A1" * 12)  # 24 chars after the prefix
    planted = tmp_path / "admin"
    planted.mkdir()
    (planted / "OPS.md").write_text(f"# Ops (planted for test)\n\ntoken: {fake_token}\n")

    result = subprocess.run(
        [GITLEAKS, "detect", "--no-git", "--source", str(tmp_path), "--config", CONFIG],
        capture_output=True, text=True,
    )
    # gitleaks exits 1 when it finds leaks.
    assert result.returncode == 1, result.stdout + result.stderr


@pytest.mark.skipif(GITLEAKS is None, reason="gitleaks not found on PATH")
def test_gitleaks_clean_on_good_context():
    good = str(Path(__file__).resolve().parent / "fixtures/good_context")
    result = subprocess.run(
        [GITLEAKS, "detect", "--no-git", "--source", good, "--config", CONFIG],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
