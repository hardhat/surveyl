<?php include __DIR__ . '/header.php'; ?>
<h1>Round 3 review queue</h1>
<form method="get" action="review.php" class="filter">
  <label>Game day ID <input type="text" name="game_day_id" value="<?= h($gameDayId) ?>" size="40"></label>
  <button type="submit">Filter</button>
</form>
<table>
  <thead>
  <tr><th>Story</th><th>Variant</th><th>Type</th><th>Prompt</th><th>Options</th><th>Winner?</th><th>Actions</th></tr>
  </thead>
  <tbody>
  <?php foreach ($candidates as $candidate): ?>
    <tr>
      <td><?= h($storyHeadlines[$candidate['canonical_story_id']] ?? $candidate['canonical_story_id']) ?></td>
      <td><?= h((string) $candidate['variant_order']) ?></td>
      <td><?= h($candidate['question_type']) ?></td>
      <td><?= h($candidate['prompt']) ?></td>
      <td>
        <?php if ($candidate['question_type'] === 'multiple_choice' && !empty($candidate['options'])): ?>
          <ol>
            <?php foreach ($candidate['options'] as $option): ?>
              <li><?= h($option) ?></li>
            <?php endforeach; ?>
          </ol>
        <?php else: ?>
          &mdash; (0-100 slider)
        <?php endif; ?>
      </td>
      <td><?= ($winnerIdsByStory[$candidate['canonical_story_id']] ?? null) === $candidate['id'] ? 'Winner' : '' ?></td>
      <td>
        <form method="post" action="review.php">
          <input type="hidden" name="game_day_id" value="<?= h($gameDayId) ?>">
          <input type="hidden" name="candidate_id" value="<?= h($candidate['id']) ?>">
          <button type="submit" name="action" value="approve">Approve</button>
          <button type="submit" name="action" value="reject">Reject &amp; regenerate</button>
        </form>
      </td>
    </tr>
  <?php endforeach; ?>
  <?php if ($candidates === []): ?>
    <tr><td colspan="7">No pending candidates<?= $gameDayId !== null ? ' for that game day' : ' (enter a game day ID above)' ?>.</td></tr>
  <?php endif; ?>
  </tbody>
</table>
<?php include __DIR__ . '/footer.php'; ?>
