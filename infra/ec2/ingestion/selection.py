"""Top-5 selection and Round 1 decoy generation (spec 8.2/8.3/8.7): 12 candidates total,
exactly 5 correct (rank 1-5 by the day's ranking), the rest plausible decoys with no
revealed rank.
"""
from .config import ROUND1_CORRECT_COUNT, ROUND1_DECOY_COUNT


def select_round1_candidates(
    ranked_stories, correct_count=ROUND1_CORRECT_COUNT, decoy_count=ROUND1_DECOY_COUNT, decoy_source=None
):
    """ranked_stories: output of ranking.rank_stories, highest score first.

    Decoys are drawn from the next-ranked real stories that didn't make the top 5 --
    genuinely plausible since they're real same-day news. If there aren't enough
    leftover ranked stories to fill the decoy quota, decoy_source(needed_count) is
    called to top up (e.g. an LLM-generated plausible-but-fake headline batch);
    raises if no decoy_source is supplied in that situation.

    Returns a list of dicts: {"canonical_story_id": ..., "rank": 1..5 or None}.
    """
    if len(ranked_stories) < correct_count:
        raise ValueError(
            f"need at least {correct_count} ranked stories to select the top {correct_count}, "
            f"got {len(ranked_stories)}"
        )

    top = ranked_stories[:correct_count]
    remainder = ranked_stories[correct_count:]
    decoys = list(remainder[:decoy_count])

    if len(decoys) < decoy_count:
        shortfall = decoy_count - len(decoys)
        if decoy_source is None:
            raise ValueError(
                f"only {len(decoys)} real candidate stories available for decoys, "
                f"need {decoy_count} and no decoy_source was provided"
            )
        decoys.extend(decoy_source(shortfall))

    candidates = [{"canonical_story_id": story["id"], "rank": rank} for rank, story in enumerate(top, start=1)]
    candidates += [{"canonical_story_id": story["id"], "rank": None} for story in decoys]
    return candidates


def write_round1_candidates(db, game_day_id, candidates):
    rows = [{"game_day_id": game_day_id, **candidate} for candidate in candidates]
    return db.insert("round1_candidates", rows)
