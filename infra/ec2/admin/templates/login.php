<?php include __DIR__ . '/header.php'; ?>
<div class="max-w-sm mx-auto mt-12 bg-white border border-slate-200 rounded-lg shadow-sm p-6">
  <h1 class="text-xl font-bold mb-4">Admin log in</h1>
  <?php if ($error !== null): ?>
    <p class="bg-red-50 text-red-700 border border-red-200 rounded px-3 py-2 text-sm mb-4"><?= h($error) ?></p>
  <?php endif; ?>
  <form method="post" action="login.php" class="space-y-4">
    <label class="block">
      <span class="block text-sm font-medium text-slate-700 mb-1">Email</span>
      <input type="email" name="email" required autofocus class="w-full border border-slate-300 rounded px-2 py-1.5 text-sm">
    </label>
    <label class="block">
      <span class="block text-sm font-medium text-slate-700 mb-1">Password</span>
      <input type="password" name="password" required class="w-full border border-slate-300 rounded px-2 py-1.5 text-sm">
    </label>
    <button type="submit" class="bg-slate-900 text-white px-4 py-1.5 rounded text-sm font-medium hover:bg-slate-700">Log in</button>
  </form>
</div>
<?php include __DIR__ . '/footer.php'; ?>
