<?php

declare(strict_types=1);

require __DIR__ . '/bootstrap.php';

header('Location: ' . (empty($_SESSION['admin_user_id']) ? 'login.php' : 'game_days.php'));
