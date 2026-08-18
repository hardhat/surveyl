<?php

declare(strict_types=1);

namespace Surveyle\Admin;

/**
 * Calls Supabase's password-grant auth endpoint using the project's anon key, mirroring
 * what supabase-js's signInWithPassword does client-side (spec 13.1). Requires
 * SUPABASE_ANON_KEY alongside SUPABASE_URL in the env file/service environment.
 */
class SupabaseAuthClient implements SupabaseAuthClientInterface
{
    public function __construct(private string $url, private string $anonKey)
    {
    }

    public static function fromEnv(?array $env = null): self
    {
        $env = $env ?? Env::load();
        return new self($env['SUPABASE_URL'], $env['SUPABASE_ANON_KEY']);
    }

    public function signInWithPassword(string $email, string $password): array
    {
        $url = rtrim($this->url, '/') . '/auth/v1/token?grant_type=password';

        $ch = curl_init($url);
        curl_setopt_array($ch, [
            CURLOPT_CUSTOMREQUEST => 'POST',
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_HTTPHEADER => [
                "apikey: {$this->anonKey}",
                'Content-Type: application/json',
            ],
            CURLOPT_POSTFIELDS => json_encode(['email' => $email, 'password' => $password]),
            CURLOPT_TIMEOUT => 30,
        ]);
        $response = curl_exec($ch);
        $status = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);

        $decoded = is_string($response) ? json_decode($response, true) : null;
        if ($response === false || $status >= 400 || !is_array($decoded)
            || empty($decoded['access_token']) || empty($decoded['user']['id'])) {
            throw new \RuntimeException('Supabase auth request failed');
        }
        return $decoded;
    }
}
