"""Round 3 candidate question generation (spec 10.2): 3 candidates per next-day story,
generated via LLMClient and written to round3_candidates.
"""
from .config import ROUND3_CANDIDATES_PER_STORY


def generate_candidates_for_story(llm, game_day_id, story, count=ROUND3_CANDIDATES_PER_STORY):
    """story: dict with id, headline, summary. Returns rows ready for
    round3_candidates.insert, with variant_order 1..count.
    """
    questions = llm.generate_round3_questions(story["headline"], story.get("summary"), count=count)
    rows = []
    for variant_order, question in enumerate(questions, start=1):
        rows.append(
            {
                "game_day_id": game_day_id,
                "canonical_story_id": story["id"],
                "variant_order": variant_order,
                "question_type": question["question_type"],
                "prompt": question["prompt"],
                "options": question.get("options"),
            }
        )
    return rows


def generate_and_write_round3_candidates(db, llm, game_day_id, future_stories):
    """future_stories: the next day's 5 candidate stories (dicts with id/headline/summary)."""
    rows = []
    for story in future_stories:
        rows.extend(generate_candidates_for_story(llm, game_day_id, story))
    return db.insert("round3_candidates", rows)


def regenerate_single_candidate(llm, game_day_id, story, variant_order):
    """Admin rejected one candidate (spec 11.4): regenerate only that single variant,
    leaving the other two untouched. Returns one row ready for an update/insert.
    """
    [question] = llm.generate_round3_questions(story["headline"], story.get("summary"), count=1)
    return {
        "game_day_id": game_day_id,
        "canonical_story_id": story["id"],
        "variant_order": variant_order,
        "question_type": question["question_type"],
        "prompt": question["prompt"],
        "options": question.get("options"),
        "status": "pending",
    }
