import random

from infra.ec2.ingestion.round2_selection import select_canonical_candidate


def test_lowest_skip_rate_wins():
    candidates = [
        {"id": "a", "total_answers": 10, "total_skips": 10},  # 50% skip rate
        {"id": "b", "total_answers": 10, "total_skips": 2},  # ~17% skip rate
        {"id": "c", "total_answers": 10, "total_skips": 5},  # ~33% skip rate
    ]

    winner = select_canonical_candidate(candidates)

    assert winner["id"] == "b"


def test_highest_total_answers_breaks_a_skip_rate_tie():
    candidates = [
        {"id": "a", "total_answers": 10, "total_skips": 10},  # 50% skip rate
        {"id": "b", "total_answers": 20, "total_skips": 20},  # 50% skip rate, more volume
    ]

    winner = select_canonical_candidate(candidates)

    assert winner["id"] == "b"


def test_full_tie_resolves_via_random_with_a_fixed_seed():
    candidates = [
        {"id": "a", "total_answers": 10, "total_skips": 5},
        {"id": "b", "total_answers": 10, "total_skips": 5},
        {"id": "c", "total_answers": 10, "total_skips": 5},
    ]

    winner = select_canonical_candidate(candidates, rng=random.Random(42))

    # Deterministic given the fixed seed; pinned so a regression would be caught.
    assert winner["id"] == random.Random(42).choice(candidates)["id"]


def test_zero_data_candidates_still_select_without_a_sample_size_minimum():
    candidates = [
        {"id": "a", "total_answers": 0, "total_skips": 0},
        {"id": "b", "total_answers": 0, "total_skips": 0},
    ]

    winner = select_canonical_candidate(candidates, rng=random.Random(1))

    assert winner["id"] in {"a", "b"}
