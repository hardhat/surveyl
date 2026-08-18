"""Daily orchestration entrypoint, invoked by cron at the freeze/publish/late-check
times (see infra/ec2/crontab). Wires together the pure-logic modules in this package
against the live Supabase project via db.SupabaseClient.

Design note on Round 3's "next day story set" (spec 10.2): at day D's 3:30am freeze,
the same ranking run that finalizes D's own top 5 (from D-1's news) also treats the
next 5 runner-up stories (ranks 6-10) as *provisional* candidates for D+1's top 5. Those
provisional stories get their Round 3 candidate questions generated now and tested
throughout day D; day D+1's freeze then promotes or discards each one once D+1's real
top 5 is known (spec 10.10). This reuses the existing ranking output rather than trying
to predict genuinely future news, and the promotion/discard step is exactly the
mechanism the spec describes for handling an imperfect provisional guess.
"""
import argparse
import logging
from datetime import date, timedelta

from . import clues, fallback, promotion, round3_questions, selection
from .clustering import cluster_by_embeddings
from .config import ROUND1_DECOY_COUNT, ROUND3_STORY_COUNT
from .db import SupabaseClient
from .llm import LLMClient
from .ranking import rank_stories
from .signals import search_spike_score, social_engagement_score
from .sources import fetch_raw_articles, news_window_for_game_date, write_raw_articles

logger = logging.getLogger(__name__)


def get_or_create_game_day(db, game_date):
    existing = db.select("game_days", params={"game_date": f"eq.{game_date.isoformat()}"})
    if existing:
        return existing[0]
    return db.insert("game_days", [{"game_date": game_date.isoformat(), "status": "draft"}])[0]


def _materialize_clusters(db, llm, game_date, raw_articles):
    """Clusters raw articles, writes one canonical_stories row per cluster, links each
    raw_stories row back to it, and returns the canonical stories annotated with
    coverage_volume (cluster size) for ranking.
    """
    embedding_texts = [f"{a['headline']}. {a.get('article_text') or ''}".strip() for a in raw_articles]
    embeddings = llm.generate_embeddings(embedding_texts)
    clusters = cluster_by_embeddings(raw_articles, embeddings)
    stories = []
    for cluster in clusters:
        representative = cluster[0]
        canonical = db.insert(
            "canonical_stories", [{"game_date": game_date.isoformat(), "headline": representative["headline"]}]
        )[0]
        raw_rows = write_raw_articles(
            db, [{**article, "canonical_story_id": canonical["id"]} for article in cluster]
        )
        stories.append({**canonical, "coverage_volume": len(raw_rows)})
    return stories


def _attach_signals(stories):
    for story in stories:
        story["search_spike"] = search_spike_score(story["headline"])
        story["social_engagement"] = social_engagement_score(story)
    return stories


def assemble(db, llm, game_date):
    """Runs the 3:30am freeze pipeline for `game_date` (uses game_date - 1 day's news)."""
    today_game_day = get_or_create_game_day(db, game_date)
    tomorrow_game_day = get_or_create_game_day(db, game_date + timedelta(days=1))

    window_start, window_end = news_window_for_game_date(game_date)
    raw_articles = fetch_raw_articles(window_start, window_end)
    if not raw_articles:
        logger.warning("no raw articles fetched for %s; leaving game_day in draft for fallback", game_date)
        return today_game_day

    stories = _materialize_clusters(db, llm, game_date, raw_articles)
    stories = _attach_signals(stories)
    ranked = rank_stories(stories)

    candidates = selection.select_round1_candidates(ranked, decoy_count=ROUND1_DECOY_COUNT)
    selection.write_round1_candidates(db, today_game_day["id"], candidates)

    top5_ids = [c["canonical_story_id"] for c in candidates if c["rank"] is not None]
    top5_stories = [s for s in ranked if s["id"] in top5_ids]
    clues.generate_and_write_clues(db, llm, top5_stories)

    remainder = ranked[len(top5_stories):]
    future_stories = remainder[:ROUND3_STORY_COUNT]
    if future_stories:
        round3_questions.generate_and_write_round3_candidates(db, llm, tomorrow_game_day["id"], future_stories)

    _promote_yesterdays_round3(db, today_game_day, candidates)
    return today_game_day


def _promote_yesterdays_round3(db, today_game_day, todays_round1_candidates):
    """Resolves the Round 3 candidates that were generated *for* today (game_day_id =
    today) during yesterday's freeze, now that today's real top 5 is known.
    """
    round3_rows = db.select("round3_candidates", params={"game_day_id": f"eq.{today_game_day['id']}"})
    by_story = {}
    for row in round3_rows:
        by_story.setdefault(row["canonical_story_id"], []).append(row)

    rank1_by_story = {c["canonical_story_id"]: c for c in todays_round1_candidates if c.get("rank") is not None}
    # todays_round1_candidates from selection.py don't carry DB ids; re-fetch to get them.
    if by_story:
        db_round1 = db.select("round1_candidates", params={"game_day_id": f"eq.{today_game_day['id']}"})
        rank1_by_story = {r["canonical_story_id"]: r for r in db_round1 if r.get("rank") is not None}

    for story_id, story_candidates in by_story.items():
        promotion.promote_or_discard_story(db, story_candidates, rank1_by_story.get(story_id))


def publish(db, game_date):
    game_day = get_or_create_game_day(db, game_date)
    return fallback.publish_or_fallback(db, game_day)


def late_check(db, game_date):
    game_day = get_or_create_game_day(db, game_date)
    return fallback.late_success_override(db, game_day)


def main():
    parser = argparse.ArgumentParser(description="Surveyle daily ingestion pipeline")
    parser.add_argument("action", choices=["assemble", "publish", "late-check"])
    parser.add_argument("--date", help="ISO game_date override, defaults to today (UK time)")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    from .config import UK_TZ
    from datetime import datetime

    game_date = date.fromisoformat(args.date) if args.date else datetime.now(UK_TZ).date()

    db = SupabaseClient.from_env()
    if args.action == "assemble":
        llm = LLMClient()
        assemble(db, llm, game_date)
    elif args.action == "publish":
        publish(db, game_date)
    elif args.action == "late-check":
        late_check(db, game_date)


if __name__ == "__main__":
    main()
