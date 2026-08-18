<?php

declare(strict_types=1);

namespace Surveyle\Admin;

/**
 * Lists game_days for admin navigation (spec 13.2) -- lets admins discover which
 * game_day_id to filter review/editors/analytics by, instead of needing raw SQL access.
 */
class GameDays
{
    public function __construct(private SupabaseClientInterface $db)
    {
    }

    public function listAll(): array
    {
        return $this->db->select('game_days', ['order' => 'game_date.desc']);
    }
}
