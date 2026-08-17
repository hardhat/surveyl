from infra.ec2.ingestion.fallback import (
    check_ingestion_complete,
    late_success_override,
    publish_or_fallback,
    resolve_active_game_package,
)


class FakeDB:
    def __init__(self, tables):
        self.tables = tables
        self.updates = []

    def select(self, table, params=None):
        rows = self.tables.get(table, [])
        if params is None:
            return rows

        def matches(row):
            for key, value in params.items():
                if key == "limit":
                    continue
                if not value.startswith("eq."):
                    continue
                if str(row.get(key)) != value[len("eq."):]:
                    return False
            return True

        result = [r for r in rows if matches(r)]
        if "limit" in params:
            result = result[: params["limit"]]
        return result

    def update(self, table, params, patch):
        self.updates.append((table, params, patch))
        for row in self.tables.get(table, []):
            row.update(patch)
        return [patch]


def _complete_round1(game_day_id):
    return [{"game_day_id": game_day_id, "rank": r if r <= 5 else None} for r in range(1, 13)]


def _complete_round3(game_day_id):
    rows = []
    for story in range(5):
        for variant in range(3):
            rows.append({"game_day_id": game_day_id, "canonical_story_id": f"story-{story}"})
    return rows


def test_check_ingestion_complete_true_when_counts_match():
    db = FakeDB({"round1_candidates": _complete_round1("gd1"), "round3_candidates": _complete_round3("gd1")})

    assert check_ingestion_complete(db, "gd1") is True


def test_check_ingestion_complete_false_when_round1_incomplete():
    db = FakeDB({"round1_candidates": _complete_round1("gd1")[:10], "round3_candidates": _complete_round3("gd1")})

    assert check_ingestion_complete(db, "gd1") is False


def test_publish_or_fallback_publishes_when_ready():
    db = FakeDB({"round1_candidates": _complete_round1("gd1"), "round3_candidates": _complete_round3("gd1")})
    game_day = {"id": "gd1", "status": "draft"}

    result = publish_or_fallback(db, game_day)

    assert result["status"] == "published"


def test_publish_or_fallback_falls_back_when_not_ready():
    db = FakeDB({"round1_candidates": [], "round3_candidates": []})
    game_day = {"id": "gd1", "status": "draft"}

    result = publish_or_fallback(db, game_day)

    assert result["status"] == "fallback"


def test_late_success_override_flips_to_published_once_ready():
    db = FakeDB({"round1_candidates": _complete_round1("gd1"), "round3_candidates": _complete_round3("gd1")})
    game_day = {"id": "gd1", "status": "fallback"}

    result = late_success_override(db, game_day)

    assert result["status"] == "published"


def test_late_success_override_is_a_no_op_if_still_not_ready():
    db = FakeDB({"round1_candidates": [], "round3_candidates": []})
    game_day = {"id": "gd1", "status": "fallback"}

    result = late_success_override(db, game_day)

    assert result["status"] == "fallback"


def test_resolve_active_game_package_serves_today_when_published():
    db = FakeDB({})
    today = {"id": "gd-today", "status": "published", "game_date": "2026-08-20"}

    result = resolve_active_game_package(db, today)

    assert result == {"game_day_id": "gd-today", "is_fallback": False}


def test_resolve_active_game_package_serves_yesterday_on_fallback():
    db = FakeDB(
        {
            "game_days": [
                {"id": "gd-yesterday", "status": "published", "game_date": "2026-08-19"},
            ]
        }
    )
    today = {"id": "gd-today", "status": "fallback", "game_date": "2026-08-20"}

    result = resolve_active_game_package(db, today)

    assert result == {"game_day_id": "gd-yesterday", "is_fallback": True}
