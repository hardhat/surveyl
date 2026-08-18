<?php

declare(strict_types=1);

namespace Surveyle\Admin;

interface SupabaseClientInterface
{
    /** @return array<int, array<string, mixed>> */
    public function select(string $table, array $params = []): array;

    /** @return array<int, array<string, mixed>> */
    public function insert(string $table, array $rows): array;

    /** @return array<int, array<string, mixed>> */
    public function update(string $table, array $params, array $patch): array;
}
