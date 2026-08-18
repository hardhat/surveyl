<?php include __DIR__ . '/header.php'; ?>
<h1 class="text-2xl font-bold mb-4">Round 3 review queue</h1>
<form method="get" action="review.php" class="flex items-end gap-3 mb-6">
  <label class="block">
    <span class="block text-sm font-medium text-slate-700 mb-1">Game day ID</span>
    <input type="text" name="game_day_id" value="<?= h($gameDayId) ?>" size="40" class="border border-slate-300 rounded px-2 py-1.5 text-sm w-96">
  </label>
  <button type="submit" class="bg-slate-900 text-white px-3 py-1.5 rounded text-sm font-medium hover:bg-slate-700">Filter</button>
</form>
<table class="w-full border-collapse text-sm bg-white shadow-sm rounded overflow-hidden mb-6">
  <thead>
  <tr class="bg-slate-100 text-left">
    <th class="p-2 font-semibold border-b border-slate-200">Story</th>
    <th class="p-2 font-semibold border-b border-slate-200">Variant</th>
    <th class="p-2 font-semibold border-b border-slate-200">Type</th>
    <th class="p-2 font-semibold border-b border-slate-200">Prompt</th>
    <th class="p-2 font-semibold border-b border-slate-200">Options</th>
    <th class="p-2 font-semibold border-b border-slate-200">Winner?</th>
    <th class="p-2 font-semibold border-b border-slate-200">Actions</th>
  </tr>
  </thead>
  <tbody>
  <?php foreach ($candidates as $candidate): ?>
    <tr class="border-b border-slate-100 align-top">
      <td class="p-2"><?= h($storyHeadlines[$candidate['canonical_story_id']] ?? $candidate['canonical_story_id']) ?></td>
      <td class="p-2"><?= h((string) $candidate['variant_order']) ?></td>
      <td class="p-2"><?= h($candidate['question_type']) ?></td>
      <td class="p-2"><?= h($candidate['prompt']) ?></td>
      <td class="p-2">
        <?php if ($candidate['question_type'] === 'multiple_choice' && !empty($candidate['options'])): ?>
          <ol class="list-decimal list-inside space-y-0.5">
            <?php foreach ($candidate['options'] as $option): ?>
              <li><?= h($option) ?></li>
            <?php endforeach; ?>
          </ol>
        <?php else: ?>
          <span class="text-slate-400">&mdash; (0-100 slider)</span>
        <?php endif; ?>
      </td>
      <td class="p-2">
        <?php if (($winnerIdsByStory[$candidate['canonical_story_id']] ?? null) === $candidate['id']): ?>
          <span class="inline-block bg-emerald-100 text-emerald-800 text-xs font-semibold px-2 py-0.5 rounded">Winner</span>
        <?php endif; ?>
      </td>
      <td class="p-2">
        <form method="post" action="review.php" class="flex gap-2">
          <input type="hidden" name="game_day_id" value="<?= h($gameDayId) ?>">
          <input type="hidden" name="candidate_id" value="<?= h($candidate['id']) ?>">
          <button type="submit" name="action" value="approve" class="bg-emerald-600 text-white px-2 py-1 rounded text-xs font-medium hover:bg-emerald-700">Approve</button>
          <button type="submit" name="action" value="reject" class="bg-red-600 text-white px-2 py-1 rounded text-xs font-medium hover:bg-red-700">Reject &amp; regenerate</button>
        </form>
      </td>
    </tr>
  <?php endforeach; ?>
  <?php if ($candidates === []): ?>
    <tr><td colspan="7" class="p-4 text-center text-slate-500">No pending candidates<?= $gameDayId !== null ? ' for that game day' : ' (enter a game day ID above)' ?>.</td></tr>
  <?php endif; ?>
  </tbody>
</table>
<?php include __DIR__ . '/footer.php'; ?>
