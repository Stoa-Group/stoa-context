from tools.crawl_and_sync import parse_repos_with_context


def test_parse_repos_with_context_filters_to_hits():
    raw = [
        {"repository": {"nameWithOwner": "Stoa-Group/stoagroupDB"}},
        {"repository": {"nameWithOwner": "Stoa-Group/stoagroupDB"}},
        {"repository": {"nameWithOwner": "Stoa-Group/banking-dashboard"}},
    ]
    repos = parse_repos_with_context(raw)
    assert repos == ["Stoa-Group/banking-dashboard", "Stoa-Group/stoagroupDB"]
