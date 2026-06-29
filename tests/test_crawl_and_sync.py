from tools.crawl_and_sync import parse_repos_with_context


def test_parse_repos_with_context_filters_to_hits():
    raw = [
        {"repository": {"nameWithOwner": "Stoa-Group/stoagroupDB"}},
        {"repository": {"nameWithOwner": "Stoa-Group/stoagroupDB"}},
        {"repository": {"nameWithOwner": "Stoa-Group/banking-dashboard"}},
    ]
    repos = parse_repos_with_context(raw)
    assert repos == ["Stoa-Group/banking-dashboard", "Stoa-Group/stoagroupDB"]


def test_parse_repos_with_context_empty():
    assert parse_repos_with_context([]) == []


def test_parse_repos_with_context_skips_malformed_items():
    raw = [
        {"repository": {"nameWithOwner": "Stoa-Group/good"}},
        {"no_repository_key": True},
        {"repository": {}},  # missing nameWithOwner
    ]
    assert parse_repos_with_context(raw) == ["Stoa-Group/good"]
