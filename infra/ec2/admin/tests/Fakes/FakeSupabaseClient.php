<?php

declare(strict_types=1);

namespace Surveyle\Admin\Tests\Fakes;

use Surveyle\Admin\SupabaseClientInterface;

/**
 * In-memory stand-in for SupabaseClient, mirroring the Python ingestion tests' FakeDB
 * pattern (see infra/ec2/tests/test_promotion.py) so both sides of the stack test the
 * same way. Supports the `eq.` and `in.(...)` PostgREST filter forms used by src/.
 */
class FakeSupabaseClient implements SupabaseClientInterface
{
    /** @var array<string, array<int, array<string, mixed>>> */
    private array $tables;

    /** @var list<array{0: string, 1: array, 2: array}> */
    public array $updates = [];

    /** @var list<array{0: string, 1: array}> */
    public array $inserts = [];

    public function __construct(array $tables = [])
    {
        $this->tables = $tables;
    }

    public function select(string $table, array $params = []): array
    {
        $rows = $this->tables[$table] ?? [];
        foreach ($params as $column => $filter) {
            if (!is_string($filter)) {
                continue;
            }
            if (str_starts_with($filter, 'eq.')) {
                $value = substr($filter, 3);
                $rows = array_values(array_filter($rows, fn($row) => (string) ($row[$column] ?? '') === $value));
            } elseif (str_starts_with($filter, 'in.(') && str_ends_with($filter, ')')) {
                $values = explode(',', substr($filter, 4, -1));
                $rows = array_values(array_filter(
                    $rows,
                    fn($row) => in_array((string) ($row[$column] ?? ''), $values, true)
                ));
            }
        }
        return array_values($rows);
    }

    public function insert(string $table, array $rows): array
    {
        $this->inserts[] = [$table, $rows];
        foreach ($rows as $row) {
            $this->tables[$table][] = $row;
        }
        return $rows;
    }

    public function update(string $table, array $params, array $patch): array
    {
        $this->updates[] = [$table, $params, $patch];
        $matchedIds = array_column($this->select($table, $params), 'id');

        $updated = [];
        foreach ($this->tables[$table] ?? [] as $index => $row) {
            if (in_array($row['id'] ?? null, $matchedIds, true)) {
                $this->tables[$table][$index] = array_merge($row, $patch);
                $updated[] = $this->tables[$table][$index];
            }
        }
        return $updated;
    }
}
