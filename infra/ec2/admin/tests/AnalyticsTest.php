<?php

declare(strict_types=1);

namespace Surveyle\Admin\Tests;

use PHPUnit\Framework\TestCase;
use Surveyle\Admin\Analytics;
use Surveyle\Admin\Tests\Fakes\FakeSupabaseClient;

class AnalyticsTest extends TestCase
{
    public function testDailyActivePlayersCountsAttemptRows(): void
    {
        $db = new FakeSupabaseClient(['player_attempts' => [
            ['id' => 'a1', 'game_day_id' => 'day-1'],
            ['id' => 'a2', 'game_day_id' => 'day-1'],
            ['id' => 'a3', 'game_day_id' => 'day-2'],
        ]]);
        $analytics = new Analytics($db);

        self::assertSame(2, $analytics->dailyActivePlayers('day-1'));
    }

    public function testRoundCompletionRates(): void
    {
        $db = new FakeSupabaseClient(['player_attempts' => [
            [
                'id' => 'a1', 'game_day_id' => 'day-1',
                'round1_submitted_at' => '2026-01-01', 'round2_submitted_at' => '2026-01-01',
                'round3_submitted_at' => null,
            ],
            [
                'id' => 'a2', 'game_day_id' => 'day-1',
                'round1_submitted_at' => '2026-01-01', 'round2_submitted_at' => null,
                'round3_submitted_at' => null,
            ],
        ]]);
        $analytics = new Analytics($db);

        $rates = $analytics->roundCompletionRates('day-1');

        self::assertSame(1.0, $rates['round1']);
        self::assertSame(0.5, $rates['round2']);
        self::assertSame(0.0, $rates['round3']);
        self::assertSame(2, $rates['total_attempts']);
    }

    public function testRoundCompletionRatesWithNoAttemptsReturnsZeroes(): void
    {
        $analytics = new Analytics(new FakeSupabaseClient([]));

        $rates = $analytics->roundCompletionRates('day-1');

        self::assertSame(0, $rates['total_attempts']);
        self::assertSame(0.0, $rates['round1']);
    }

    public function testSkipRatesByQuestionComputesFromQuestionStats(): void
    {
        $db = new FakeSupabaseClient([
            'round1_candidates' => [['id' => 'r1', 'game_day_id' => 'day-1', 'canonical_story_id' => 's1']],
            'round2_questions' => [['id' => 'q1', 'round1_candidate_id' => 'r1', 'question_type' => 'percentage']],
            'question_stats' => [['round2_question_id' => 'q1', 'total_answers' => 8, 'total_skips' => 2]],
        ]);
        $analytics = new Analytics($db);

        $rates = $analytics->skipRatesByQuestion('day-1');

        self::assertSame('q1', $rates[0]['question_id']);
        self::assertSame(0.2, $rates[0]['skip_rate']);
    }

    public function testTopPerformingFormatsRanksByLowestAverageSkipRate(): void
    {
        $analytics = new Analytics(new FakeSupabaseClient([]));
        $rates = [
            ['question_id' => 'q1', 'question_type' => 'percentage', 'skip_rate' => 0.4],
            ['question_id' => 'q2', 'question_type' => 'multiple_choice', 'skip_rate' => 0.1],
            ['question_id' => 'q3', 'question_type' => 'multiple_choice', 'skip_rate' => 0.3],
        ];

        $ranking = $analytics->topPerformingFormats($rates);

        self::assertSame(['multiple_choice', 'percentage'], array_keys($ranking));
        self::assertEqualsWithDelta(0.2, $ranking['multiple_choice'], 0.0001);
    }
}
