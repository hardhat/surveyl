<?php

declare(strict_types=1);

namespace Surveyle\Admin\Tests;

use PHPUnit\Framework\TestCase;
use Surveyle\Admin\GameDays;
use Surveyle\Admin\Tests\Fakes\FakeSupabaseClient;

class GameDaysTest extends TestCase
{
    public function testListAllReturnsGameDaysRows(): void
    {
        $db = new FakeSupabaseClient(['game_days' => [
            ['id' => 'd1', 'game_date' => '2026-08-18', 'status' => 'draft'],
            ['id' => 'd2', 'game_date' => '2026-08-19', 'status' => 'draft'],
        ]]);
        $gameDays = new GameDays($db);

        $result = $gameDays->listAll();

        self::assertCount(2, $result);
        self::assertSame(['d1', 'd2'], array_column($result, 'id'));
    }
}
