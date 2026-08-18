<?php include __DIR__ . '/header.php'; ?>
<h1 class="text-2xl font-bold mb-4">Analytics</h1>
<form method="get" action="analytics.php" class="flex items-end gap-3 mb-6">
  <label class="block">
    <span class="block text-sm font-medium text-slate-700 mb-1">Game day ID</span>
    <input type="text" name="game_day_id" value="<?= h($gameDayId) ?>" size="40" class="border border-slate-300 rounded px-2 py-1.5 text-sm w-96">
  </label>
  <button type="submit" class="bg-slate-900 text-white px-3 py-1.5 rounded text-sm font-medium hover:bg-slate-700">Load</button>
</form>

<?php if ($gameDayId === null): ?>
  <p class="text-slate-500">Enter a game day ID above to load its analytics.</p>
<?php else: ?>
  <h2 class="text-lg font-semibold mt-8 mb-3">Active players: <?= h((string) $activePlayers) ?></h2>

  <h2 class="text-lg font-semibold mt-8 mb-3">Round completion rates</h2>
  <ul class="bg-white border border-slate-200 rounded-lg shadow-sm p-4 mb-6 space-y-1 text-sm">
    <li>Round 1: <?= h(number_format($completionRates['round1'] * 100, 1)) ?>%</li>
    <li>Round 2: <?= h(number_format($completionRates['round2'] * 100, 1)) ?>%</li>
    <li>Round 3: <?= h(number_format($completionRates['round3'] * 100, 1)) ?>%</li>
    <li>Total attempts: <?= h((string) $completionRates['total_attempts']) ?></li>
  </ul>

  <h2 class="text-lg font-semibold mt-8 mb-3">Skip rate per question</h2>
  <table class="w-full border-collapse text-sm bg-white shadow-sm rounded overflow-hidden mb-6">
    <thead>
    <tr class="bg-slate-100 text-left">
      <th class="p-2 font-semibold border-b border-slate-200">Question</th>
      <th class="p-2 font-semibold border-b border-slate-200">Type</th>
      <th class="p-2 font-semibold border-b border-slate-200">Skip rate</th>
    </tr>
    </thead>
    <tbody>
    <?php foreach ($skipRates as $rate): ?>
      <tr class="border-b border-slate-100">
        <td class="p-2"><?= h($rate['question_id']) ?></td>
        <td class="p-2"><?= h($rate['question_type']) ?></td>
        <td class="p-2"><?= h(number_format($rate['skip_rate'] * 100, 1)) ?>%</td>
      </tr>
    <?php endforeach; ?>
    <?php if ($skipRates === []): ?>
      <tr><td colspan="3" class="p-4 text-center text-slate-500">No Round 2 questions for that game day yet.</td></tr>
    <?php endif; ?>
    </tbody>
  </table>

  <h2 class="text-lg font-semibold mt-8 mb-3">Format performance (lowest skip rate first)</h2>
  <ol class="list-decimal list-inside bg-white border border-slate-200 rounded-lg shadow-sm p-4 space-y-1 text-sm">
    <?php foreach ($formatRanking as $format => $avgSkipRate): ?>
      <li><?= h($format) ?>: <?= h(number_format($avgSkipRate * 100, 1)) ?>% avg skip rate</li>
    <?php endforeach; ?>
  </ol>
<?php endif; ?>
<?php include __DIR__ . '/footer.php'; ?>
