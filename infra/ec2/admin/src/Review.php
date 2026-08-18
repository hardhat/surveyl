<?php

declare(strict_types=1);

namespace Surveyle\Admin;

/**
 * Review queue for Round 3 candidate questions (spec 13.2/11.4): admins approve or
 * reject each generated candidate; rejecting one immediately regenerates only that
 * single variant, leaving the other two for that story untouched.
 */
class Review
{
    public function __construct(
        private SupabaseClientInterface $db,
        private CandidateRegeneratorInterface $regenerator
    ) {
    }

    public function pendingCandidates(?string $gameDayId = null): array
    {
        $params = ['status' => 'eq.pending', 'order' => 'canonical_story_id,variant_order'];
        if ($gameDayId !== null) {
            $params['game_day_id'] = "eq.{$gameDayId}";
        }
        return $this->db->select('round3_candidates', $params);
    }

    public function approve(string $candidateId): array
    {
        $rows = $this->db->update('round3_candidates', ['id' => "eq.{$candidateId}"], ['status' => 'approved']);
        return $rows[0];
    }

    public function reject(string $candidateId): array
    {
        $this->db->update('round3_candidates', ['id' => "eq.{$candidateId}"], ['status' => 'rejected']);
        return $this->regenerator->regenerate($candidateId);
    }
}
