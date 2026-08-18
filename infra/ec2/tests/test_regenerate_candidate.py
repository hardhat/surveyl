from infra.ec2.ingestion.regenerate_candidate import regenerate


class FakeDB:
    def __init__(self, candidates, stories):
        self._candidates = candidates
        self._stories = stories
        self.updates = []

    def select(self, table, params=None):
        if table == "round3_candidates":
            candidate_id = params["id"].removeprefix("eq.")
            return [c for c in self._candidates if c["id"] == candidate_id]
        if table == "canonical_stories":
            story_id = params["id"].removeprefix("eq.")
            return [s for s in self._stories if s["id"] == story_id]
        raise AssertionError(f"unexpected table {table}")

    def update(self, table, params, patch):
        self.updates.append((table, params, patch))
        candidate_id = params["id"].removeprefix("eq.")
        for c in self._candidates:
            if c["id"] == candidate_id:
                c.update(patch)
        return [c for c in self._candidates if c["id"] == candidate_id]


class FakeLLM:
    def generate_round3_questions(self, headline, summary, count=3):
        assert count == 1
        return [{"question_type": "percentage", "prompt": f"new question about {headline}", "options": None}]


def test_regenerate_updates_only_the_rejected_candidate():
    candidates = [
        {
            "id": "c1", "canonical_story_id": "story-1", "game_day_id": "day-1",
            "variant_order": 1, "status": "rejected",
        },
        {
            "id": "c2", "canonical_story_id": "story-1", "game_day_id": "day-1",
            "variant_order": 2, "status": "approved",
        },
    ]
    stories = [{"id": "story-1", "headline": "Headline", "summary": "Summary"}]
    db = FakeDB(candidates, stories)
    llm = FakeLLM()

    result = regenerate(db, llm, "c1")

    assert result["prompt"] == "new question about Headline"
    assert result["status"] == "pending"
    assert candidates[1]["status"] == "approved"  # untouched
