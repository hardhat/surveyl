from infra.ec2.ingestion.promotion import compute_correct_answer, promote_or_discard_story


class FakeDB:
    def __init__(self, question_stats):
        self._question_stats = question_stats
        self.updates = []
        self.inserts = []

    def select(self, table, params=None):
        assert table == "question_stats"
        return self._question_stats

    def update(self, table, params, patch):
        self.updates.append((table, params, patch))
        return [patch]

    def insert(self, table, rows):
        self.inserts.append((table, rows))
        return rows


def _round3_candidates(story_id):
    return [
        {"id": "c1", "canonical_story_id": story_id, "question_type": "percentage", "prompt": "p1", "options": None},
        {"id": "c2", "canonical_story_id": story_id, "question_type": "percentage", "prompt": "p2", "options": None},
        {"id": "c3", "canonical_story_id": story_id, "question_type": "percentage", "prompt": "p3", "options": None},
    ]


def test_story_not_in_tomorrows_top5_is_discarded():
    db = FakeDB(question_stats=[])
    candidates = _round3_candidates("story-1")

    result = promote_or_discard_story(db, candidates, tomorrow_round1_candidate=None)

    assert result is None
    assert db.updates == [("round3_candidates", {"id": "in.(c1,c2,c3)"}, {"status": "rejected"})]
    assert db.inserts == []


def test_story_in_tomorrows_top5_is_promoted_to_round2_questions():
    db = FakeDB(
        question_stats=[
            {"round3_candidate_id": "c1", "total_answers": 10, "total_skips": 5, "percentage_sum": 400},
            {"round3_candidate_id": "c2", "total_answers": 10, "total_skips": 1, "percentage_sum": 250},
            {"round3_candidate_id": "c3", "total_answers": 10, "total_skips": 8, "percentage_sum": 300},
        ]
    )
    candidates = _round3_candidates("story-1")
    tomorrow_round1_candidate = {"id": "r1-tomorrow"}

    result = promote_or_discard_story(db, candidates, tomorrow_round1_candidate)

    assert result["round1_candidate_id"] == "r1-tomorrow"
    assert result["source_round3_candidate_id"] == "c2"  # lowest skip rate
    assert result["correct_percentage"] == 25  # 250/10 = 25, already a multiple of 5
    assert db.updates == []


def test_compute_correct_answer_multiple_choice_uses_most_picked_option():
    stats = {"option_counts": {"0": 2, "1": 7, "2": 1, "3": 0}}

    answer = compute_correct_answer(stats, "multiple_choice")

    assert answer == {"correct_option_index": 1}


def test_compute_correct_answer_percentage_rounds_to_nearest_5():
    stats = {"total_answers": 4, "percentage_sum": 91}  # mean = 22.75 -> rounds to 25

    answer = compute_correct_answer(stats, "percentage")

    assert answer == {"correct_percentage": 25}
