"""CLI entrypoint for admin-triggered single Round 3 candidate regeneration (spec
11.4), invoked by the PHP admin dashboard (infra/ec2/admin) as a subprocess so the LLM
prompt/safety-rule logic (llm.py's LLMClient) stays defined in one place instead of
being duplicated in PHP.
"""
import argparse
import json

from .db import SupabaseClient
from .llm import LLMClient
from .round3_questions import regenerate_single_candidate


def regenerate(db, llm, candidate_id):
    [candidate] = db.select("round3_candidates", params={"id": f"eq.{candidate_id}"})
    [story] = db.select("canonical_stories", params={"id": f"eq.{candidate['canonical_story_id']}"})
    new_row = regenerate_single_candidate(llm, candidate["game_day_id"], story, candidate["variant_order"])
    return db.update("round3_candidates", {"id": f"eq.{candidate_id}"}, new_row)[0]


def main():
    parser = argparse.ArgumentParser(description="Regenerate a single rejected Round 3 candidate")
    parser.add_argument("--candidate-id", required=True)
    args = parser.parse_args()

    db = SupabaseClient.from_env()
    llm = LLMClient()
    result = regenerate(db, llm, args.candidate_id)
    print(json.dumps(result))


if __name__ == "__main__":
    main()
