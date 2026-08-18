<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Surveyle Admin</title>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-50 text-slate-900 font-sans min-h-screen">
<header class="bg-slate-900 text-white px-6 py-3 flex items-center gap-6 flex-wrap">
  <strong class="text-lg tracking-tight">Surveyle Admin</strong>
  <?php if (!empty($_SESSION['admin_user_id'])): ?>
    <nav class="flex items-center gap-4 text-sm">
      <a href="game_days.php" class="text-slate-200 hover:text-white hover:underline">Game Days</a>
      <a href="review.php" class="text-slate-200 hover:text-white hover:underline">Review Queue</a>
      <a href="editors.php" class="text-slate-200 hover:text-white hover:underline">Editors</a>
      <a href="analytics.php" class="text-slate-200 hover:text-white hover:underline">Analytics</a>
      <a href="logout.php" class="ml-auto text-slate-300 hover:text-white hover:underline">Log out (<?= h($_SESSION['admin_email'] ?? '') ?>)</a>
    </nav>
  <?php endif; ?>
</header>
<main class="max-w-5xl mx-auto p-6">
