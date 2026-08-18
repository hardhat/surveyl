<?php

declare(strict_types=1);

// No Composer/vendor dependency: the admin dashboard has zero external PHP packages,
// so a tiny PSR-4 autoloader is enough for both the app (src/) and tests (tests/).
spl_autoload_register(function (string $class): void {
    $prefixes = [
        'Surveyle\\Admin\\Tests\\' => __DIR__ . '/tests/',
        'Surveyle\\Admin\\' => __DIR__ . '/src/',
    ];
    foreach ($prefixes as $prefix => $baseDir) {
        if (str_starts_with($class, $prefix)) {
            $relative = substr($class, strlen($prefix));
            $file = $baseDir . str_replace('\\', '/', $relative) . '.php';
            if (is_file($file)) {
                require $file;
            }
            return;
        }
    }
});
