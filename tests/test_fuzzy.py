from light_cli_tui.fuzzy import fuzzy_filter, fuzzy_score


def test_empty_query_never_matches():
    assert fuzzy_score("", "Anything") is None
    assert fuzzy_score("   ", "Anything") is None


def test_substring_match_scores_100_case_insensitive():
    assert fuzzy_score("play", "Playing God") == 100.0
    assert fuzzy_score("PLAY", "playing god") == 100.0


def test_no_match_below_threshold_returns_none():
    assert fuzzy_score("xyzzy", "Playing God", threshold=80) is None


def test_fuzzy_match_above_threshold_scores_below_100():
    score = fuzzy_score("Playin God", "Playing God")
    assert score is not None
    assert score < 100.0


def test_fuzzy_filter_sorts_best_first_and_drops_non_matches():
    items = ["Playing God", "Playin God", "Totally Unrelated"]
    scored = fuzzy_filter("Playing God", items, key=lambda s: (s,))

    assert [item for _, item in scored] == ["Playing God", "Playin God"]
    assert scored[0][0] >= scored[1][0]


def test_fuzzy_filter_empty_query_matches_nothing():
    items = ["Anything", "Something Else"]
    assert fuzzy_filter("", items, key=lambda s: (s,)) == []
