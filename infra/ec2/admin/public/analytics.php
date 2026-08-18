<?php

declare(strict_types=1);

require __DIR__ . '/bootstrap.php';
require_admin();

$gameDayId = current_game_day_id();

$activePlayers = null;
$completionRates = null;
$skipRates = [];
$formatRanking = [];

if ($gameDayId !== null) {
    $activePlayers = $analytics->dailyActivePlayers($gameDayId);
    $completionRates = $analytics->roundCompletionRates($gameDayId);
    $skipRates = $analytics->skipRatesByQuestion($gameDayId);
    $formatRanking = $analytics->topPerformingFormats($skipRates);
}

include __DIR__ . '/../templates/analytics.php';
