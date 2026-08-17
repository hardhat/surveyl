import pytest

from infra.ec2.ingestion.selection import select_round1_candidates


def _ranked_stories(n):
    return [{"id": f"story-{i}"} for i in range(n)]


def test_produces_12_candidates_with_exactly_5_flagged_correct():
    ranked = _ranked_stories(12)

    candidates = select_round1_candidates(ranked)

    assert len(candidates) == 12
    assert sum(1 for c in candidates if c["rank"] is not None) == 5


def test_top_5_ranks_are_1_through_5_in_ranked_order():
    ranked = _ranked_stories(12)

    candidates = select_round1_candidates(ranked)

    correct = sorted((c for c in candidates if c["rank"] is not None), key=lambda c: c["rank"])
    assert [c["rank"] for c in correct] == [1, 2, 3, 4, 5]
    assert [c["canonical_story_id"] for c in correct] == [f"story-{i}" for i in range(5)]


def test_decoys_have_no_rank():
    ranked = _ranked_stories(12)

    candidates = select_round1_candidates(ranked)

    decoys = [c for c in candidates if c["rank"] is None]
    assert len(decoys) == 7


def test_insufficient_decoys_falls_back_to_decoy_source():
    ranked = _ranked_stories(7)  # only 2 leftover after top 5, need 5 more decoys (decoy_count=7)

    candidates = select_round1_candidates(
        ranked, decoy_source=lambda n: [{"id": f"generated-{i}"} for i in range(n)]
    )

    assert len(candidates) == 12
    decoy_ids = {c["canonical_story_id"] for c in candidates if c["rank"] is None}
    assert decoy_ids == {
        "story-5",
        "story-6",
        "generated-0",
        "generated-1",
        "generated-2",
        "generated-3",
        "generated-4",
    }


def test_insufficient_decoys_without_a_source_raises():
    ranked = _ranked_stories(6)

    with pytest.raises(ValueError):
        select_round1_candidates(ranked)


def test_too_few_ranked_stories_for_top_5_raises():
    with pytest.raises(ValueError):
        select_round1_candidates(_ranked_stories(3))
