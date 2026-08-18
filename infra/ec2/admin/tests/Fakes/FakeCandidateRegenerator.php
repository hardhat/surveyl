<?php

declare(strict_types=1);

namespace Surveyle\Admin\Tests\Fakes;

use Surveyle\Admin\CandidateRegeneratorInterface;

class FakeCandidateRegenerator implements CandidateRegeneratorInterface
{
    /** @var list<string> */
    public array $regeneratedIds = [];

    public function __construct(private array $result = ['id' => 'regenerated', 'prompt' => 'new prompt'])
    {
    }

    public function regenerate(string $candidateId): array
    {
        $this->regeneratedIds[] = $candidateId;
        return $this->result;
    }
}
