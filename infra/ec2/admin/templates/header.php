<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Surveyle Admin</title>
  <link rel="stylesheet" href="assets/style.css">
</head>
<body>
<header class="topbar">
  <strong>Surveyle Admin</strong>
  <?php if (!empty($_SESSION['admin_user_id'])): ?>
    <nav>
      <a href="game_days.php">Game Days</a>
      <a href="review.php">Review Queue</a>
      <a href="editors.php">Editors</a>
      <a href="analytics.php">Analytics</a>
      <a href="logout.php">Log out (<?= h($_SESSION['admin_email'] ?? '') ?>)</a>
    </nav>
  <?php endif; ?>
</header>
<main>
