<?php

declare(strict_types=1);

require __DIR__ . '/bootstrap.php';
require_admin();

$gameDayId = current_game_day_id();

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $action = (string) ($_POST['action'] ?? '');
    $candidateId = (string) ($_POST['candidate_id'] ?? '');
    if ($action === 'approve') {
        $review->approve($candidateId);
    } elseif ($action === 'reject') {
        $review->reject($candidateId);
    }
    header('Location: review.php' . ($gameDayId !== null ? '?game_day_id=' . urlencode($gameDayId) : ''));
    exit;
}

$candidates = $review->pendingCandidates($gameDayId);
$winnerIdsByStory = $gameDayId !== null ? $winners->winningCandidateIdsByStory($gameDayId) : [];

include __DIR__ . '/../templates/review.php';
