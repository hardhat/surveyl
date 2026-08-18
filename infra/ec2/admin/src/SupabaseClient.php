<?php

declare(strict_types=1);

namespace Surveyle\Admin;

/**
 * Thin PostgREST client for the admin dashboard, authenticated with the service-role
 * key so it bypasses RLS -- the same convention as the Python ingestion pipeline's
 * db.py (infra/ec2/ingestion/db.py). The key is loaded server-side only via Env::load()
 * and is never sent to the browser.
 */
class SupabaseClient implements SupabaseClientInterface
{
    private string $baseUrl;
    private string $serviceRoleKey;

    public function __construct(string $url, string $serviceRoleKey)
    {
        $this->baseUrl = rtrim($url, '/') . '/rest/v1';
        $this->serviceRoleKey = $serviceRoleKey;
    }

    public static function fromEnv(?array $env = null): self
    {
        $env = $env ?? Env::load();
        return new self($env['SUPABASE_URL'], $env['SUPABASE_SERVICE_ROLE_KEY']);
    }

    public function select(string $table, array $params = []): array
    {
        $query = http_build_query($params);
        $url = "{$this->baseUrl}/{$table}" . ($query !== '' ? "?{$query}" : '');
        return $this->request('GET', $url);
    }

    public function insert(string $table, array $rows): array
    {
        return $this->request('POST', "{$this->baseUrl}/{$table}", $rows, ['Prefer: return=representation']);
    }

    public function update(string $table, array $params, array $patch): array
    {
        $query = http_build_query($params);
        $url = "{$this->baseUrl}/{$table}" . ($query !== '' ? "?{$query}" : '');
        return $this->request('PATCH', $url, $patch, ['Prefer: return=representation']);
    }

    private function request(string $method, string $url, ?array $body = null, array $extraHeaders = []): array
    {
        $headers = array_merge([
            "apikey: {$this->serviceRoleKey}",
            "Authorization: Bearer {$this->serviceRoleKey}",
            'Content-Type: application/json',
        ], $extraHeaders);

        $ch = curl_init($url);
        curl_setopt_array($ch, [
            CURLOPT_CUSTOMREQUEST => $method,
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_HTTPHEADER => $headers,
            CURLOPT_TIMEOUT => 30,
        ]);
        if ($body !== null) {
            curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($body));
        }

        $response = curl_exec($ch);
        if ($response === false) {
            $error = curl_error($ch);
            curl_close($ch);
            throw new \RuntimeException("Supabase request failed: {$error}");
        }
        $status = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);

        if ($status >= 400) {
            throw new \RuntimeException("Supabase request failed ({$status}): {$response}");
        }
        return $response !== '' ? (json_decode($response, true) ?? []) : [];
    }
}
