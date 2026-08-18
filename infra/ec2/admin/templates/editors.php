<?php include __DIR__ . '/header.php'; ?>
<h1>Content editors</h1>
<form method="get" action="editors.php" class="filter">
  <label>Game day ID <input type="text" name="game_day_id" value="<?= h($gameDayId) ?>" size="40"></label>
  <button type="submit">Load</button>
</form>

<?php if ($gameDayId === null): ?>
  <p>Enter a game day ID above to load its content.</p>
<?php else: ?>
  <h2>Story summaries</h2>
  <?php foreach ($storiesById as $story): ?>
    <form method="post" action="editors.php">
      <input type="hidden" name="action" value="update_summary">
      <input type="hidden" name="game_day_id" value="<?= h($gameDayId) ?>">
      <input type="hidden" name="story_id" value="<?= h($story['id']) ?>">
      <p><strong><?= h($story['headline']) ?></strong></p>
      <textarea name="summary"><?= h($story['summary'] ?? '') ?></textarea>
      <button type="submit">Save summary</button>
    </form>
  <?php endforeach; ?>

  <h2>Round 1 clues</h2>
  <?php foreach ($clues as $clue): ?>
    <form method="post" action="editors.php">
      <input type="hidden" name="action" value="update_clue">
      <input type="hidden" name="game_day_id" value="<?= h($gameDayId) ?>">
      <input type="hidden" name="clue_id" value="<?= h($clue['id']) ?>">
      <p><?= h($clue['clue_type']) ?> (clue <?= h((string) $clue['clue_order']) ?>)</p>
      <textarea name="content"><?= h($clue['content']) ?></textarea>
      <button type="submit">Save clue</button>
    </form>
  <?php endforeach; ?>

  <h2>Round 3 candidate questions</h2>
  <?php foreach ($round3Candidates as $candidate): ?>
    <form method="post" action="editors.php">
      <input type="hidden" name="action" value="update_candidate">
      <input type="hidden" name="game_day_id" value="<?= h($gameDayId) ?>">
      <input type="hidden" name="candidate_id" value="<?= h($candidate['id']) ?>">
      <p>Variant <?= h((string) $candidate['variant_order']) ?> (<?= h($candidate['question_type']) ?>), status: <?= h($candidate['status']) ?></p>
      <textarea name="prompt"><?= h($candidate['prompt']) ?></textarea>
      <button type="submit">Save question</button>
    </form>
  <?php endforeach; ?>

  <h2>Round 2 explanations</h2>
  <?php foreach ($round2Questions as $question): ?>
    <form method="post" action="editors.php">
      <input type="hidden" name="action" value="update_explanation">
      <input type="hidden" name="game_day_id" value="<?= h($gameDayId) ?>">
      <input type="hidden" name="question_id" value="<?= h($question['id']) ?>">
      <p><?= h($question['prompt']) ?></p>
      <textarea name="explanation"><?= h($question['explanation'] ?? '') ?></textarea>
      <button type="submit">Save explanation</button>
    </form>
  <?php endforeach; ?>
<?php endif; ?>
<?php include __DIR__ . '/footer.php'; ?>
