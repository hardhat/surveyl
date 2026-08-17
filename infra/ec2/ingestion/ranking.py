"""Weighted composite story ranking (spec 12.3): coverage volume > search spikes >
social engagement. Each signal is min-max normalized across the day's candidate stories
before weighting, so relative priority holds regardless of each signal's raw scale.
"""
from .config import RANKING_WEIGHTS


def _normalize(values):
    lo, hi = min(values), max(values)
    if hi == lo:
        return [0.5 for _ in values]
    return [(v - lo) / (hi - lo) for v in values]


def rank_stories(stories, weights=None):
    """stories: list of dicts with at least id, coverage_volume, search_spike,
    social_engagement. Returns a new list, sorted highest score first, each with a
    'score' key added. Ties break deterministically on story id (ascending).
    """
    weights = weights or RANKING_WEIGHTS
    if not stories:
        return []

    coverage = _normalize([s["coverage_volume"] for s in stories])
    spike = _normalize([s["search_spike"] for s in stories])
    social = _normalize([s["social_engagement"] for s in stories])

    scored = []
    for story, c, sp, so in zip(stories, coverage, spike, social):
        score = (
            weights["coverage_volume"] * c
            + weights["search_spike"] * sp
            + weights["social_engagement"] * so
        )
        scored.append({**story, "score": score})

    scored.sort(key=lambda s: (-s["score"], str(s["id"])))
    return scored
