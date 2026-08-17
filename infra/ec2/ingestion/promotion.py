"""Promotion/expiry logic (spec 10.10): the winning Round 3 candidate for a story is
promoted into tomorrow's Round 2 question only if that story makes tomorrow's final
top 5; otherwise its candidates are discarded (marked rejected, not deleted, so the
admin review trail is preserved).
"""
from .round2_selection import fetch_candidate_stats, select_canonical_candidate


def compute_correct_answer(stats, question_type):
    """Derives the Round 2 'correct' answer from the winning candidate's crowd
    responses: the most-picked option for multiple choice, or the mean percentage
    (rounded to the nearest 5, matching the slider step) for percentage questions.
    """
    if question_type == "multiple_choice":
        option_counts = stats.get("option_counts") or {}
        if not option_counts:
            return {"correct_option_index": 0}
        winning_index = int(max(option_counts, key=lambda k: option_counts[k]))
        return {"correct_option_index": winning_index}

    total = stats["total_answers"]
    average = (stats["percentage_sum"] / total) if total else 50
    rounded = round(average / 5) * 5
    return {"correct_percentage": max(0, min(100, int(rounded)))}


def promote_or_discard_story(db, round3_candidates_for_story, tomorrow_round1_candidate, rng=None):
    """round3_candidates_for_story: the 3 round3_candidates rows for one canonical story.
    tomorrow_round1_candidate: tomorrow's round1_candidates row for that story if it made
    the top 5, else None (meaning: discard).

    Returns the inserted round2_questions row, or None if the story was discarded.
    """
    candidate_ids = [c["id"] for c in round3_candidates_for_story]

    if tomorrow_round1_candidate is None:
        db.update("round3_candidates", {"id": f"in.({','.join(candidate_ids)})"}, {"status": "rejected"})
        return None

    stats = fetch_candidate_stats(db, candidate_ids)
    winner_stats = select_canonical_candidate(stats, rng=rng)
    winner_candidate = next(c for c in round3_candidates_for_story if c["id"] == winner_stats["id"])

    answer = compute_correct_answer(winner_stats, winner_candidate["question_type"])
    row = {
        "round1_candidate_id": tomorrow_round1_candidate["id"],
        "source_round3_candidate_id": winner_candidate["id"],
        "question_type": winner_candidate["question_type"],
        "prompt": winner_candidate["prompt"],
        "options": winner_candidate.get("options"),
        **answer,
    }
    return db.insert("round2_questions", [row])[0]
