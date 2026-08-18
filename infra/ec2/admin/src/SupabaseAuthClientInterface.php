<?php

declare(strict_types=1);

namespace Surveyle\Admin;

interface SupabaseAuthClientInterface
{
    /**
     * Returns ['access_token' => string, 'user' => ['id' => string, ...], ...].
     * Throws on invalid credentials or any non-2xx response.
     */
    public function signInWithPassword(string $email, string $password): array;
}
