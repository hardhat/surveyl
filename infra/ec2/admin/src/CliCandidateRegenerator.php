<?php

declare(strict_types=1);

namespace Surveyle\Admin;

/**
 * Shells out to the Python ingestion package for regeneration (spec 11.4), so the LLM
 * prompt/safety-rule logic (ingestion/llm.py's LLMClient) stays defined in exactly one
 * place instead of being duplicated here in PHP.
 */
class CliCandidateRegenerator implements CandidateRegeneratorInterface
{
    public function __construct(private string $surveyleHome = '/opt/surveyle')
    {
    }

    public function regenerate(string $candidateId): array
    {
        $cmd = sprintf(
            'cd %s && venv/bin/python -m infra.ec2.ingestion.regenerate_candidate --candidate-id %s 2>&1',
            escapeshellarg($this->surveyleHome),
            escapeshellarg($candidateId)
        );

        exec($cmd, $output, $exitCode);
        if ($exitCode !== 0) {
            throw new \RuntimeException('Regeneration failed: ' . implode("\n", $output));
        }

        $decoded = json_decode((string) end($output), true);
        if (!is_array($decoded)) {
            throw new \RuntimeException('Regeneration produced unreadable output.');
        }
        return $decoded;
    }
}
