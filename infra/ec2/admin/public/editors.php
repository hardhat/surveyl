<?php

declare(strict_types=1);

require __DIR__ . '/bootstrap.php';
require_admin();

$gameDayId = current_game_day_id();

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $action = (string) ($_POST['action'] ?? '');
    if ($action === 'update_clue') {
        $editors->updateClue((string) $_POST['clue_id'], (string) $_POST['content']);
    } elseif ($action === 'update_summary') {
        $editors->updateStorySummary((string) $_POST['story_id'], (string) $_POST['summary']);
    } elseif ($action === 'update_candidate') {
        $editors->updateCandidatePrompt((string) $_POST['candidate_id'], (string) $_POST['prompt']);
    } elseif ($action === 'update_explanation') {
        $editors->updateExplanation((string) $_POST['question_id'], (string) $_POST['explanation']);
    }
    header('Location: editors.php' . ($gameDayId !== null ? '?game_day_id=' . urlencode($gameDayId) : ''));
    exit;
}

$round1Candidates = $gameDayId !== null ? $db->select('round1_candidates', ['game_day_id' => "eq.{$gameDayId}"]) : [];

$storiesById = [];
foreach (array_column($round1Candidates, 'canonical_story_id') as $storyId) {
    $rows = $db->select('canonical_stories', ['id' => "eq.{$storyId}"]);
    if ($rows !== []) {
        $storiesById[$storyId] = $rows[0];
    }
}

$clues = [];
foreach (array_keys($storiesById) as $storyId) {
    foreach ($db->select('round1_clues', ['canonical_story_id' => "eq.{$storyId}"]) as $clue) {
        $clues[] = $clue;
    }
}

$round3Candidates = $gameDayId !== null ? $db->select('round3_candidates', ['game_day_id' => "eq.{$gameDayId}"]) : [];

$round2Questions = [];
foreach ($round1Candidates as $round1Candidate) {
    $rows = $db->select('round2_questions', ['round1_candidate_id' => "eq.{$round1Candidate['id']}"]);
    if ($rows !== []) {
        $round2Questions[] = $rows[0];
    }
}

include __DIR__ . '/../templates/editors.php';
