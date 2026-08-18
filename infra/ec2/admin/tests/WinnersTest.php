<?php

declare(strict_types=1);

namespace Surveyle\Admin\Tests;

use PHPUnit\Framework\TestCase;
use Surveyle\Admin\Tests\Fakes\FakeSupabaseClient;
use Surveyle\Admin\Winners;

class WinnersTest extends TestCase
{
    public function testHighlightsTheWinningCandidatePerStory(): void
    {
        $db = new FakeSupabaseClient([
            'round1_candidates' => [
                ['id' => 'r1', 'game_day_id' => 'day-1', 'canonical_story_id' => 'story-1'],
                ['id' => 'r2', 'game_day_id' => 'day-1', 'canonical_story_id' => 'story-2'],
            ],
            'round2_questions' => [
                ['id' => 'q1', 'round1_candidate_id' => 'r1', 'source_round3_candidate_id' => 'c2'],
                ['id' => 'q2', 'round1_candidate_id' => 'r2', 'source_round3_candidate_id' => null],
            ],
        ]);
        $winners = new Winners($db);

        $result = $winners->winningCandidateIdsByStory('day-1');

        self::assertSame(['story-1' => 'c2'], $result);
    }

    public function testReturnsEmptyWhenNoRound1CandidatesForDay(): void
    {
        $db = new FakeSupabaseClient([]);
        $winners = new Winners($db);

        self::assertSame([], $winners->winningCandidateIdsByStory('day-1'));
    }
}
