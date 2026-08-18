<?php include __DIR__ . '/header.php'; ?>
<h1 class="text-2xl font-bold mb-4">Content editors</h1>
<form method="get" action="editors.php" class="flex items-end gap-3 mb-6">
  <label class="block">
    <span class="block text-sm font-medium text-slate-700 mb-1">Game day ID</span>
    <input type="text" name="game_day_id" value="<?= h($gameDayId) ?>" size="40" class="border border-slate-300 rounded px-2 py-1.5 text-sm w-96">
  </label>
  <button type="submit" class="bg-slate-900 text-white px-3 py-1.5 rounded text-sm font-medium hover:bg-slate-700">Load</button>
</form>

<?php if ($gameDayId === null): ?>
  <p class="text-slate-500">Enter a game day ID above to load its content.</p>
<?php else: ?>
  <h2 class="text-lg font-semibold mt-8 mb-3">Story summaries</h2>
  <?php foreach ($storiesById as $story): ?>
    <form method="post" action="editors.php" class="bg-white border border-slate-200 rounded-lg shadow-sm p-4 mb-3">
      <input type="hidden" name="action" value="update_summary">
      <input type="hidden" name="game_day_id" value="<?= h($gameDayId) ?>">
      <input type="hidden" name="story_id" value="<?= h($story['id']) ?>">
      <p class="font-semibold mb-2"><?= h($story['headline']) ?></p>
      <textarea name="summary" class="w-full border border-slate-300 rounded px-2 py-1.5 text-sm mb-2"><?= h($story['summary'] ?? '') ?></textarea>
      <button type="submit" class="bg-slate-900 text-white px-3 py-1.5 rounded text-sm font-medium hover:bg-slate-700">Save summary</button>
    </form>
  <?php endforeach; ?>

  <h2 class="text-lg font-semibold mt-8 mb-3">Round 1 clues</h2>
  <?php foreach ($clues as $clue): ?>
    <form method="post" action="editors.php" class="bg-white border border-slate-200 rounded-lg shadow-sm p-4 mb-3">
      <input type="hidden" name="action" value="update_clue">
      <input type="hidden" name="game_day_id" value="<?= h($gameDayId) ?>">
      <input type="hidden" name="clue_id" value="<?= h($clue['id']) ?>">
      <p class="text-sm text-slate-500 mb-2"><?= h($clue['clue_type']) ?> (clue <?= h((string) $clue['clue_order']) ?>)</p>
      <textarea name="content" class="w-full border border-slate-300 rounded px-2 py-1.5 text-sm mb-2"><?= h($clue['content']) ?></textarea>
      <button type="submit" class="bg-slate-900 text-white px-3 py-1.5 rounded text-sm font-medium hover:bg-slate-700">Save clue</button>
    </form>
  <?php endforeach; ?>

  <h2 class="text-lg font-semibold mt-8 mb-3">Round 3 candidate questions</h2>
  <?php foreach ($round3Candidates as $candidate): ?>
    <form method="post" action="editors.php" class="bg-white border border-slate-200 rounded-lg shadow-sm p-4 mb-3">
      <input type="hidden" name="action" value="update_candidate">
      <input type="hidden" name="game_day_id" value="<?= h($gameDayId) ?>">
      <input type="hidden" name="candidate_id" value="<?= h($candidate['id']) ?>">
      <p class="text-sm text-slate-500 mb-2">Variant <?= h((string) $candidate['variant_order']) ?> (<?= h($candidate['question_type']) ?>), status: <?= h($candidate['status']) ?></p>
      <textarea name="prompt" class="w-full border border-slate-300 rounded px-2 py-1.5 text-sm mb-2"><?= h($candidate['prompt']) ?></textarea>
      <button type="submit" class="bg-slate-900 text-white px-3 py-1.5 rounded text-sm font-medium hover:bg-slate-700">Save question</button>
    </form>
  <?php endforeach; ?>

  <h2 class="text-lg font-semibold mt-8 mb-3">Round 2 explanations</h2>
  <?php foreach ($round2Questions as $question): ?>
    <form method="post" action="editors.php" class="bg-white border border-slate-200 rounded-lg shadow-sm p-4 mb-3">
      <input type="hidden" name="action" value="update_explanation">
      <input type="hidden" name="game_day_id" value="<?= h($gameDayId) ?>">
      <input type="hidden" name="question_id" value="<?= h($question['id']) ?>">
      <p class="text-sm text-slate-500 mb-2"><?= h($question['prompt']) ?></p>
      <textarea name="explanation" class="w-full border border-slate-300 rounded px-2 py-1.5 text-sm mb-2"><?= h($question['explanation'] ?? '') ?></textarea>
      <button type="submit" class="bg-slate-900 text-white px-3 py-1.5 rounded text-sm font-medium hover:bg-slate-700">Save explanation</button>
    </form>
  <?php endforeach; ?>
<?php endif; ?>
<?php include __DIR__ . '/footer.php'; ?>
