<?php

declare(strict_types=1);

namespace Surveyle\Admin;

/**
 * Basic analytics/observability (spec 13.2/19): active players, round completion
 * rates, skip rates per question, and question-format performance for one game day.
 */
class Analytics
{
    public function __construct(private SupabaseClientInterface $db)
    {
    }

    public function dailyActivePlayers(string $gameDayId): int
    {
        return count($this->db->select('player_attempts', ['game_day_id' => "eq.{$gameDayId}"]));
    }

    /** @return array{round1: float, round2: float, round3: float, total_attempts: int} */
    public function roundCompletionRates(string $gameDayId): array
    {
        $attempts = $this->db->select('player_attempts', ['game_day_id' => "eq.{$gameDayId}"]);
        $total = count($attempts);
        if ($total === 0) {
            return ['round1' => 0.0, 'round2' => 0.0, 'round3' => 0.0, 'total_attempts' => 0];
        }

        $rate = function (string $field) use ($attempts, $total): float {
            $completed = count(array_filter($attempts, fn($a) => !empty($a[$field])));
            return $completed / $total;
        };
        return [
            'round1' => $rate('round1_submitted_at'),
            'round2' => $rate('round2_submitted_at'),
            'round3' => $rate('round3_submitted_at'),
            'total_attempts' => $total,
        ];
    }

    /** @return list<array{question_id: string, question_type: string, skip_rate: float}> */
    public function skipRatesByQuestion(string $gameDayId): array
    {
        $round1 = $this->db->select('round1_candidates', ['game_day_id' => "eq.{$gameDayId}"]);
        $round1Ids = array_column($round1, 'id');
        $questions = $round1Ids !== []
            ? $this->db->select('round2_questions', ['round1_candidate_id' => 'in.(' . implode(',', $round1Ids) . ')'])
            : [];

        $rates = [];
        foreach ($questions as $question) {
            $statsRows = $this->db->select('question_stats', ['round2_question_id' => "eq.{$question['id']}"]);
            $rates[] = [
                'question_id' => $question['id'],
                'question_type' => $question['question_type'],
                'skip_rate' => $this->skipRate($statsRows[0] ?? null),
            ];
        }
        return $rates;
    }

    private function skipRate(?array $stats): float
    {
        if ($stats === null) {
            return 0.0;
        }
        $total = $stats['total_answers'] + $stats['total_skips'];
        return $total > 0 ? $stats['total_skips'] / $total : 0.0;
    }

    /**
     * Ranks question formats best-to-worst by average skip rate across $rates (from
     * skipRatesByQuestion), per spec 19's "top-performing question format" metric.
     *
     * @return array<string, float> question_type => average skip rate, ascending
     */
    public function topPerformingFormats(array $rates): array
    {
        $byFormat = [];
        foreach ($rates as $rate) {
            $byFormat[$rate['question_type']][] = $rate['skip_rate'];
        }

        $averages = [];
        foreach ($byFormat as $format => $skipRates) {
            $averages[$format] = array_sum($skipRates) / count($skipRates);
        }
        asort($averages);
        return $averages;
    }
}
