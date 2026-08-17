"""Ingestion failure fallback and late-success override (spec 5.4/5.5).

NOTE: `resolve_active_game_package` is the logic the "fetch today's game package" API
must apply (spec section 21 assigns that read path to a Supabase Edge Function, not
this EC2 job). It's implemented here in Python now as the reference behaviour and
covered by unit tests; it will need porting to the Edge Function's TypeScript runtime
before players can actually hit it -- that porting is not yet done.
"""
from .config import ROUND1_CANDIDATE_COUNT, ROUND1_CORRECT_COUNT, ROUND3_CANDIDATES_PER_STORY, ROUND3_STORY_COUNT


def check_ingestion_complete(db, game_day_id):
    """A day's ingestion is complete once it has its 12 Round 1 candidates (5 with a
    rank) and, for its role as a *future* story set, 3 Round 3 candidates for each of
    its 5 stories. (Round 2 questions may legitimately be absent/admin-authored on
    early launch days, so they're not part of this readiness check.)
    """
    round1 = db.select("round1_candidates", params={"game_day_id": f"eq.{game_day_id}"})
    if len(round1) != ROUND1_CANDIDATE_COUNT:
        return False
    if sum(1 for r in round1 if r.get("rank") is not None) != ROUND1_CORRECT_COUNT:
        return False

    round3 = db.select("round3_candidates", params={"game_day_id": f"eq.{game_day_id}"})
    by_story = {}
    for row in round3:
        by_story.setdefault(row["canonical_story_id"], 0)
        by_story[row["canonical_story_id"]] += 1
    if len(by_story) != ROUND3_STORY_COUNT:
        return False
    return all(count == ROUND3_CANDIDATES_PER_STORY for count in by_story.values())


def publish_or_fallback(db, game_day):
    """Called at the 6:00am publish cutoff. Marks `game_day` published if ingestion
    completed in time, otherwise fallback (spec 5.3/5.4: auto-publish happens either
    way, using whatever content is ready -- fallback just means "not ready" here).
    """
    status = "published" if check_ingestion_complete(db, game_day["id"]) else "fallback"
    return db.update("game_days", {"id": f"eq.{game_day['id']}"}, {"status": status})[0]


def late_success_override(db, game_day):
    """Spec 5.5: once late ingestion succeeds after 6am, replace the fallback with the
    real game immediately. Only flips status -- existing player_attempts rows (from
    players who started the fallback session) are left untouched so they can finish.
    """
    if game_day["status"] != "fallback":
        return game_day
    if not check_ingestion_complete(db, game_day["id"]):
        return game_day
    return db.update("game_days", {"id": f"eq.{game_day['id']}"}, {"status": "published"})[0]


def resolve_active_game_package(db, today_game_day):
    """Returns {"game_day_id": ..., "is_fallback": bool} identifying which game_day's
    content a *new* session fetching "today's game" should actually receive.

    - published today -> serve today, is_fallback=False
    - fallback today -> serve yesterday's game_day (must exist/be published), with a
      warning flag; players who already completed yesterday's game are blocked from
      a fresh attempt by the existing one-attempt-per-day unique constraint, since the
      attempt gets recorded against yesterday's game_day_id in this case.
    """
    if today_game_day["status"] == "published":
        return {"game_day_id": today_game_day["id"], "is_fallback": False}

    if today_game_day["status"] != "fallback":
        raise ValueError(f"game_day {today_game_day['id']} is not published or fallback yet")

    [yesterday] = db.select(
        "game_days",
        params={
            "game_date": f"eq.{_previous_date(today_game_day['game_date'])}",
            "status": "eq.published",
            "limit": 1,
        },
    ) or [None]
    if yesterday is None:
        raise RuntimeError("ingestion failed today and no published game exists for yesterday either")
    return {"game_day_id": yesterday["id"], "is_fallback": True}


def _previous_date(iso_date_str):
    from datetime import date, timedelta

    return (date.fromisoformat(iso_date_str) - timedelta(days=1)).isoformat()
