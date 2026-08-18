<?php include __DIR__ . '/header.php'; ?>
<h1>Admin log in</h1>
<?php if ($error !== null): ?>
  <p class="error"><?= h($error) ?></p>
<?php endif; ?>
<form method="post" action="login.php">
  <p><label>Email <input type="email" name="email" required autofocus></label></p>
  <p><label>Password <input type="password" name="password" required></label></p>
  <button type="submit">Log in</button>
</form>
<?php include __DIR__ . '/footer.php'; ?>
