<?php

declare(strict_types=1);

namespace Surveyle\Admin;

/**
 * Loads server-side secrets from /etc/surveyle/surveyle.env -- same file and KEY=VALUE
 * format as the Python ingestion side's db.load_env() -- falling back to real process
 * environment variables. Never exposed to the browser (admin/src is outside the Apache
 * document root, see public/).
 */
class Env
{
    public const DEFAULT_PATH = '/etc/surveyle/surveyle.env';

    public static function load(string $path = self::DEFAULT_PATH): array
    {
        $env = [];
        foreach (getenv() as $key => $value) {
            $env[$key] = $value;
        }

        if (is_file($path)) {
            foreach (file($path, FILE_IGNORE_NEW_LINES) ?: [] as $line) {
                $line = trim($line);
                if ($line === '' || str_starts_with($line, '#') || !str_contains($line, '=')) {
                    continue;
                }
                [$key, $value] = explode('=', $line, 2);
                $env[trim($key)] = trim($value);
            }
        }
        return $env;
    }
}
