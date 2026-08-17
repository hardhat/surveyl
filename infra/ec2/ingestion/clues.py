"""Round 1 clue generation (spec 8.4/8.5): each of the day's top-5 stories gets a
primary clue (clue_order 1) and an optional second clue (clue_order 2), generated via
LLMClient and written to round1_clues.
"""
PRIMARY_CLUE_TYPE = "redacted_headline"
SECONDARY_CLUE_TYPE = "satirical_summary"


def generate_clues_for_story(llm, story):
    """story: dict with id, headline, summary. Returns rows ready for round1_clues.insert."""
    return [
        {
            "canonical_story_id": story["id"],
            "clue_order": 1,
            "clue_type": PRIMARY_CLUE_TYPE,
            "content": llm.generate_clue(story["headline"], story.get("summary"), PRIMARY_CLUE_TYPE),
        },
        {
            "canonical_story_id": story["id"],
            "clue_order": 2,
            "clue_type": SECONDARY_CLUE_TYPE,
            "content": llm.generate_clue(story["headline"], story.get("summary"), SECONDARY_CLUE_TYPE),
        },
    ]


def generate_and_write_clues(db, llm, top_stories):
    """top_stories: the day's 5 real top stories (dicts with id/headline/summary)."""
    rows = []
    for story in top_stories:
        rows.extend(generate_clues_for_story(llm, story))
    return db.insert("round1_clues", rows)
