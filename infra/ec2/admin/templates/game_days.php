<?php include __DIR__ . '/header.php'; ?>
<h1>Game days</h1>
<p>Pick a day to jump into its review queue, editors, or analytics.</p>
<table>
  <thead>
  <tr><th>Date</th><th>Status</th><th>Game day ID</th><th>Links</th></tr>
  </thead>
  <tbody>
  <?php foreach ($days as $day): ?>
    <tr>
      <td><?= h($day['game_date']) ?></td>
      <td><?= h($day['status']) ?></td>
      <td><code><?= h($day['id']) ?></code></td>
      <td>
        <a href="review.php?game_day_id=<?= urlencode($day['id']) ?>">Review</a>
        &middot; <a href="editors.php?game_day_id=<?= urlencode($day['id']) ?>">Editors</a>
        &middot; <a href="analytics.php?game_day_id=<?= urlencode($day['id']) ?>">Analytics</a>
      </td>
    </tr>
  <?php endforeach; ?>
  <?php if ($days === []): ?>
    <tr><td colspan="4">No game days yet.</td></tr>
  <?php endif; ?>
  </tbody>
</table>
<?php include __DIR__ . '/footer.php'; ?>
