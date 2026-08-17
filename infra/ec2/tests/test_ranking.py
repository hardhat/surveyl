from infra.ec2.ingestion.ranking import rank_stories


def test_higher_coverage_volume_wins_when_other_signals_are_equal():
    stories = [
        {"id": "a", "coverage_volume": 20, "search_spike": 10, "social_engagement": 5},
        {"id": "b", "coverage_volume": 5, "search_spike": 10, "social_engagement": 5},
    ]

    ranked = rank_stories(stories)

    assert [s["id"] for s in ranked] == ["a", "b"]


def test_search_spike_breaks_a_coverage_volume_tie():
    stories = [
        {"id": "a", "coverage_volume": 10, "search_spike": 90, "social_engagement": 0},
        {"id": "b", "coverage_volume": 10, "search_spike": 10, "social_engagement": 0},
    ]

    ranked = rank_stories(stories)

    assert [s["id"] for s in ranked] == ["a", "b"]


def test_coverage_volume_priority_beats_a_social_engagement_advantage():
    # Weighting: coverage_volume=0.6, search_spike=0.3, social_engagement=0.1.
    # "a" wins on coverage+spike even though "b" dominates the lowest-priority signal.
    stories = [
        {"id": "a", "coverage_volume": 100, "search_spike": 100, "social_engagement": 0},
        {"id": "b", "coverage_volume": 0, "search_spike": 0, "social_engagement": 100},
    ]

    ranked = rank_stories(stories)

    assert [s["id"] for s in ranked] == ["a", "b"]


def test_identical_stories_produce_a_deterministic_tie_break_by_id():
    stories = [
        {"id": "story-b", "coverage_volume": 10, "search_spike": 10, "social_engagement": 10},
        {"id": "story-a", "coverage_volume": 10, "search_spike": 10, "social_engagement": 10},
    ]

    ranked = rank_stories(stories)

    assert [s["id"] for s in ranked] == ["story-a", "story-b"]


def test_empty_input_returns_empty_list():
    assert rank_stories([]) == []
