<?php

declare(strict_types=1);

require __DIR__ . '/bootstrap.php';
require_admin();

$days = $gameDays->listAll();

include __DIR__ . '/../templates/game_days.php';
