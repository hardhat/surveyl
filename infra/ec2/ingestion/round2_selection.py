"""Round 2 canonical question selection (spec 9.5): for each story, pick the winning
Round 3 candidate from lowest skip rate, then highest total answers, then random
tiebreak. Always selects from whatever data exists -- no minimum sample-size fallback.
"""
import random


def _skip_rate(candidate_stats):
    total = candidate_stats["total_answers"] + candidate_stats["total_skips"]
    return candidate_stats["total_skips"] / total if total else 0.0


def select_canonical_candidate(candidates_with_stats, rng=None):
    """candidates_with_stats: list of dicts with at least id, total_answers, total_skips.
    Returns the winning candidate dict.
    """
    if not candidates_with_stats:
        raise ValueError("no candidates to select from")
    rng = rng or random.Random()

    min_rate = min(_skip_rate(c) for c in candidates_with_stats)
    lowest_skip_rate = [c for c in candidates_with_stats if _skip_rate(c) == min_rate]

    max_answers = max(c["total_answers"] for c in lowest_skip_rate)
    tied_on_answers = [c for c in lowest_skip_rate if c["total_answers"] == max_answers]

    return rng.choice(tied_on_answers)


def fetch_candidate_stats(db, round3_candidate_ids):
    """Joins round3_candidates to their question_stats row (0/0 if no responses yet)."""
    stats_by_id = {
        row["round3_candidate_id"]: row
        for row in db.select(
            "question_stats",
            params={"round3_candidate_id": f"in.({','.join(round3_candidate_ids)})"},
        )
    }
    results = []
    for candidate_id in round3_candidate_ids:
        stats = stats_by_id.get(candidate_id, {"total_answers": 0, "total_skips": 0})
        results.append({"id": candidate_id, **stats})
    return results
