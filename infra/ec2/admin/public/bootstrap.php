<?php

declare(strict_types=1);

require __DIR__ . '/../autoload.php';

use Surveyle\Admin\Analytics;
use Surveyle\Admin\Auth;
use Surveyle\Admin\CliCandidateRegenerator;
use Surveyle\Admin\Editors;
use Surveyle\Admin\Env;
use Surveyle\Admin\GameDays;
use Surveyle\Admin\Review;
use Surveyle\Admin\SupabaseAuthClient;
use Surveyle\Admin\SupabaseClient;
use Surveyle\Admin\Winners;

session_start();

$env = Env::load();
$db = SupabaseClient::fromEnv($env);
$auth = new Auth(SupabaseAuthClient::fromEnv($env), $db);
$regenerator = new CliCandidateRegenerator($env['SURVEYLE_HOME'] ?? '/opt/surveyle');
$review = new Review($db, $regenerator);
$editors = new Editors($db);
$winners = new Winners($db);
$analytics = new Analytics($db);
$gameDays = new GameDays($db);

function require_admin(): void
{
    if (empty($_SESSION['admin_user_id'])) {
        header('Location: login.php');
        exit;
    }
}

/** The game_day_id filter, read from either a GET link or a same-page POST form. */
function current_game_day_id(): ?string
{
    $value = (string) ($_GET['game_day_id'] ?? $_POST['game_day_id'] ?? '');
    return $value !== '' ? $value : null;
}

function h(?string $value): string
{
    return htmlspecialchars($value ?? '', ENT_QUOTES, 'UTF-8');
}
