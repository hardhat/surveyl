<?php

declare(strict_types=1);

namespace Surveyle\Admin\Tests;

use PHPUnit\Framework\TestCase;
use Surveyle\Admin\Review;
use Surveyle\Admin\Tests\Fakes\FakeCandidateRegenerator;
use Surveyle\Admin\Tests\Fakes\FakeSupabaseClient;

class ReviewTest extends TestCase
{
    public function testPendingCandidatesFiltersByStatusAndGameDay(): void
    {
        $db = new FakeSupabaseClient(['round3_candidates' => [
            ['id' => 'c1', 'game_day_id' => 'day-1', 'status' => 'pending'],
            ['id' => 'c2', 'game_day_id' => 'day-1', 'status' => 'approved'],
            ['id' => 'c3', 'game_day_id' => 'day-2', 'status' => 'pending'],
        ]]);
        $review = new Review($db, new FakeCandidateRegenerator());

        $pending = $review->pendingCandidates('day-1');

        self::assertCount(1, $pending);
        self::assertSame('c1', $pending[0]['id']);
    }

    public function testApproveSetsStatusApproved(): void
    {
        $db = new FakeSupabaseClient(['round3_candidates' => [
            ['id' => 'c1', 'status' => 'pending'],
        ]]);
        $review = new Review($db, new FakeCandidateRegenerator());

        $result = $review->approve('c1');

        self::assertSame('approved', $result['status']);
    }

    public function testRejectMarksRejectedAndRegeneratesOnlyThatCandidate(): void
    {
        $db = new FakeSupabaseClient(['round3_candidates' => [
            ['id' => 'c1', 'status' => 'pending'],
            ['id' => 'c2', 'status' => 'pending'],
        ]]);
        $regenerator = new FakeCandidateRegenerator(['id' => 'c1', 'prompt' => 'new prompt']);
        $review = new Review($db, $regenerator);

        $result = $review->reject('c1');

        self::assertSame(['c1'], $regenerator->regeneratedIds);
        self::assertSame('new prompt', $result['prompt']);
        self::assertSame([['round3_candidates', ['id' => 'eq.c1'], ['status' => 'rejected']]], $db->updates);
        self::assertSame('pending', $db->select('round3_candidates', ['id' => 'eq.c2'])[0]['status']);
    }
}
