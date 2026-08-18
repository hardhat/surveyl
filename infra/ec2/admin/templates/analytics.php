<?php include __DIR__ . '/header.php'; ?>
<h1>Analytics</h1>
<form method="get" action="analytics.php" class="filter">
  <label>Game day ID <input type="text" name="game_day_id" value="<?= h($gameDayId) ?>" size="40"></label>
  <button type="submit">Load</button>
</form>

<?php if ($gameDayId === null): ?>
  <p>Enter a game day ID above to load its analytics.</p>
<?php else: ?>
  <h2>Active players: <?= h((string) $activePlayers) ?></h2>

  <h2>Round completion rates</h2>
  <ul>
    <li>Round 1: <?= h(number_format($completionRates['round1'] * 100, 1)) ?>%</li>
    <li>Round 2: <?= h(number_format($completionRates['round2'] * 100, 1)) ?>%</li>
    <li>Round 3: <?= h(number_format($completionRates['round3'] * 100, 1)) ?>%</li>
    <li>Total attempts: <?= h((string) $completionRates['total_attempts']) ?></li>
  </ul>

  <h2>Skip rate per question</h2>
  <table>
    <thead><tr><th>Question</th><th>Type</th><th>Skip rate</th></tr></thead>
    <tbody>
    <?php foreach ($skipRates as $rate): ?>
      <tr>
        <td><?= h($rate['question_id']) ?></td>
        <td><?= h($rate['question_type']) ?></td>
        <td><?= h(number_format($rate['skip_rate'] * 100, 1)) ?>%</td>
      </tr>
    <?php endforeach; ?>
    <?php if ($skipRates === []): ?>
      <tr><td colspan="3">No Round 2 questions for that game day yet.</td></tr>
    <?php endif; ?>
    </tbody>
  </table>

  <h2>Format performance (lowest skip rate first)</h2>
  <ol>
    <?php foreach ($formatRanking as $format => $avgSkipRate): ?>
      <li><?= h($format) ?>: <?= h(number_format($avgSkipRate * 100, 1)) ?>% avg skip rate</li>
    <?php endforeach; ?>
  </ol>
<?php endif; ?>
<?php include __DIR__ . '/footer.php'; ?>
