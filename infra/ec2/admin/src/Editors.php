<?php

declare(strict_types=1);

namespace Surveyle\Admin;

/**
 * Persists admin edits to generated copy (spec 11.3): clues, story summaries, Round 3
 * candidate question text, and Round 2 explanations. Clue edit history is captured by
 * the round1_clues_before_update DB trigger, not here.
 */
class Editors
{
    public function __construct(private SupabaseClientInterface $db)
    {
    }

    public function updateClue(string $clueId, string $content): array
    {
        $rows = $this->db->update('round1_clues', ['id' => "eq.{$clueId}"], ['content' => $content]);
        return $rows[0];
    }

    public function updateStorySummary(string $storyId, string $summary): array
    {
        $rows = $this->db->update('canonical_stories', ['id' => "eq.{$storyId}"], ['summary' => $summary]);
        return $rows[0];
    }

    public function updateCandidatePrompt(string $candidateId, string $prompt, ?array $options = null): array
    {
        $patch = ['prompt' => $prompt];
        if ($options !== null) {
            $patch['options'] = $options;
        }
        $rows = $this->db->update('round3_candidates', ['id' => "eq.{$candidateId}"], $patch);
        return $rows[0];
    }

    public function updateExplanation(string $round2QuestionId, string $explanation): array
    {
        $rows = $this->db->update(
            'round2_questions',
            ['id' => "eq.{$round2QuestionId}"],
            ['explanation' => $explanation]
        );
        return $rows[0];
    }
}
