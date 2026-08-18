<?php

declare(strict_types=1);

namespace Surveyle\Admin;

interface CandidateRegeneratorInterface
{
    /** Regenerates a single Round 3 candidate's content and returns the updated row. */
    public function regenerate(string $candidateId): array;
}
