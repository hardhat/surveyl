<?php

declare(strict_types=1);

namespace Surveyle\Admin;

/**
 * Surfaces the auto-selected Round 2 winner (spec 9.5/13.2): read-only, no manual
 * override -- the admin UI only needs to highlight which Round 3 candidate was
 * promoted for each story.
 */
class Winners
{
    public function __construct(private SupabaseClientInterface $db)
    {
    }

    /** @return array<string, string> canonical_story_id => winning round3_candidate_id */
    public function winningCandidateIdsByStory(string $gameDayId): array
    {
        $round1 = $this->db->select('round1_candidates', ['game_day_id' => "eq.{$gameDayId}"]);
        $round1ById = [];
        foreach ($round1 as $row) {
            $round1ById[$row['id']] = $row;
        }
        if ($round1ById === []) {
            return [];
        }

        $ids = implode(',', array_keys($round1ById));
        $questions = $this->db->select('round2_questions', ['round1_candidate_id' => "in.({$ids})"]);

        $result = [];
        foreach ($questions as $question) {
            if (empty($question['source_round3_candidate_id'])) {
                continue;
            }
            $storyId = $round1ById[$question['round1_candidate_id']]['canonical_story_id'];
            $result[$storyId] = $question['source_round3_candidate_id'];
        }
        return $result;
    }
}
