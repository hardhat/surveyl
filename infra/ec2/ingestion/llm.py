"""OpenAI wrapper for the two LLM-generated content types (spec 11.2): Round 1 clue
text and Round 3 candidate questions. All prompts bake in the editorial safety rules
from specification.md section 3.3 so generated copy doesn't need a separate safety pass
before admin review.
"""
import json
import os

from openai import OpenAI

DEFAULT_MODEL = "gpt-4o-mini"

_SAFETY_RULES = """You write mildly cheeky copy for a daily UK news game called Surveyle.
Avoid: making light of active mass-casualty events, sexual crimes, child harm, personal
tragedies involving private individuals, defamatory or unverifiable claims, targeting
protected characteristics, or implying facts the poll itself can't prove. Political jokes
should target absurdity, systems, media framing, or institutions -- never vulnerable
individuals."""


class LLMClient:
    def __init__(self, api_key=None, model=DEFAULT_MODEL):
        self.client = OpenAI(api_key=api_key or os.environ["OPENAI_API_KEY"])
        self.model = model

    def _json_completion(self, system, user):
        response = self.client.chat.completions.create(
            model=self.model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        return json.loads(response.choices[0].message.content)

    def generate_clue(self, headline, summary, clue_type):
        """Returns the clue content string for the given clue_type (one of
        'satirical_summary', 'redacted_headline', 'keyword_cluster').
        """
        prompts = {
            "satirical_summary": (
                "Write a one-sentence satirical summary of this story that hints at what "
                "happened without naming the specific people/places/organisation involved."
            ),
            "redacted_headline": (
                "Rewrite this headline with the key identifying names/places/organisations "
                "replaced by blanks (e.g. '____'), keeping the rest of the wording intact."
            ),
            "keyword_cluster": (
                "Produce 4-6 short keywords or phrases (comma separated) that hint at this "
                "story's topic without naming the specific people/places/organisation involved."
            ),
        }
        system = f"{_SAFETY_RULES}\nRespond as JSON: {{\"content\": \"...\"}}"
        user = f"{prompts[clue_type]}\n\nHeadline: {headline}\nSummary: {summary or ''}"
        return self._json_completion(system, user)["content"]

    def generate_round3_questions(self, headline, summary, count=3):
        """Returns `count` candidate questions, each a dict:
        {"question_type": "multiple_choice"|"percentage", "prompt": str,
         "options": [str, str, str, str] | None}
        Formats may be mixed across the batch (spec 10.4).
        """
        system = (
            f"{_SAFETY_RULES}\n"
            "Write crowd-testing poll questions about the story below, in the style of a "
            "cheeky British panel-show poll. Each question is either 'multiple_choice' "
            "(exactly 4 options, single correct-feeling answer left ambiguous since this "
            "is opinion polling, not trivia) or 'percentage' (asks what % of people think/"
            "did/would do something related to the story).\n"
            f'Respond as JSON: {{"questions": [{{"question_type": "...", "prompt": "...", '
            '"options": [..] or null}}, ...]}}'
        )
        user = f"Headline: {headline}\nSummary: {summary or ''}\nGenerate exactly {count} questions."
        result = self._json_completion(system, user)
        return result["questions"][:count]
