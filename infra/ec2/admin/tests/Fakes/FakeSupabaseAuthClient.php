<?php

declare(strict_types=1);

namespace Surveyle\Admin\Tests\Fakes;

use Surveyle\Admin\SupabaseAuthClientInterface;

class FakeSupabaseAuthClient implements SupabaseAuthClientInterface
{
    public function __construct(private array $validCredentials, private string $userId)
    {
    }

    public function signInWithPassword(string $email, string $password): array
    {
        if (($this->validCredentials['email'] ?? null) !== $email
            || ($this->validCredentials['password'] ?? null) !== $password) {
            throw new \RuntimeException('invalid credentials');
        }
        return ['access_token' => 'fake-token', 'user' => ['id' => $this->userId]];
    }
}
