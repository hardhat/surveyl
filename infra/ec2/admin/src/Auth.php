<?php

declare(strict_types=1);

namespace Surveyle\Admin;

/**
 * Admin login (spec 13.1): authenticates against Supabase Auth (email/password), then
 * rejects the session unless the signed-in user is also listed in the `admins` table.
 */
class Auth
{
    public function __construct(
        private SupabaseAuthClientInterface $authClient,
        private SupabaseClientInterface $db
    ) {
    }

    /** @return array{user_id: string, email: string, access_token: string} */
    public function login(string $email, string $password): array
    {
        try {
            $session = $this->authClient->signInWithPassword($email, $password);
        } catch (\Throwable $e) {
            throw new AdminAuthError('Invalid email or password.');
        }

        $userId = $session['user']['id'];
        $adminRows = $this->db->select('admins', ['user_id' => "eq.{$userId}"]);
        if ($adminRows === []) {
            throw new AdminAuthError('This account is not an admin.');
        }

        return [
            'user_id' => $userId,
            'email' => $email,
            'access_token' => $session['access_token'],
        ];
    }
}
