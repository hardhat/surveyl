<?php include __DIR__ . '/header.php'; ?>
<h1 class="text-2xl font-bold mb-2">Game days</h1>
<p class="text-slate-500 mb-6">Pick a day to jump into its review queue, editors, or analytics.</p>
<table class="w-full border-collapse text-sm bg-white shadow-sm rounded overflow-hidden">
  <thead>
  <tr class="bg-slate-100 text-left">
    <th class="p-2 font-semibold border-b border-slate-200">Date</th>
    <th class="p-2 font-semibold border-b border-slate-200">Status</th>
    <th class="p-2 font-semibold border-b border-slate-200">Game day ID</th>
    <th class="p-2 font-semibold border-b border-slate-200">Links</th>
  </tr>
  </thead>
  <tbody>
  <?php foreach ($days as $day): ?>
    <tr class="border-b border-slate-100">
      <td class="p-2 font-medium"><?= h($day['game_date']) ?></td>
      <td class="p-2">
        <span class="inline-block bg-slate-100 text-slate-700 text-xs font-semibold px-2 py-0.5 rounded"><?= h($day['status']) ?></span>
      </td>
      <td class="p-2"><code class="text-xs text-slate-500"><?= h($day['id']) ?></code></td>
      <td class="p-2 space-x-2">
        <a href="review.php?game_day_id=<?= urlencode($day['id']) ?>" class="text-slate-900 font-medium hover:underline">Review</a>
        <a href="editors.php?game_day_id=<?= urlencode($day['id']) ?>" class="text-slate-900 font-medium hover:underline">Editors</a>
        <a href="analytics.php?game_day_id=<?= urlencode($day['id']) ?>" class="text-slate-900 font-medium hover:underline">Analytics</a>
      </td>
    </tr>
  <?php endforeach; ?>
  <?php if ($days === []): ?>
    <tr><td colspan="4" class="p-4 text-center text-slate-500">No game days yet.</td></tr>
  <?php endif; ?>
  </tbody>
</table>
<?php include __DIR__ . '/footer.php'; ?>
