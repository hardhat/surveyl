<?php

declare(strict_types=1);

namespace Surveyle\Admin\Tests;

use PHPUnit\Framework\TestCase;
use Surveyle\Admin\Editors;
use Surveyle\Admin\Tests\Fakes\FakeSupabaseClient;

class EditorsTest extends TestCase
{
    public function testUpdateCluePersistsContent(): void
    {
        $db = new FakeSupabaseClient(['round1_clues' => [['id' => 'clue-1', 'content' => 'old']]]);
        $editors = new Editors($db);

        $result = $editors->updateClue('clue-1', 'new clue text');

        self::assertSame('new clue text', $result['content']);
        self::assertSame('new clue text', $db->select('round1_clues', ['id' => 'eq.clue-1'])[0]['content']);
    }

    public function testUpdateStorySummaryPersists(): void
    {
        $db = new FakeSupabaseClient(['canonical_stories' => [['id' => 's1', 'summary' => null]]]);
        $editors = new Editors($db);

        $result = $editors->updateStorySummary('s1', 'a satirical summary');

        self::assertSame('a satirical summary', $result['summary']);
    }

    public function testUpdateCandidatePromptPersists(): void
    {
        $db = new FakeSupabaseClient(['round3_candidates' => [['id' => 'c1', 'prompt' => 'old']]]);
        $editors = new Editors($db);

        $result = $editors->updateCandidatePrompt('c1', 'new prompt');

        self::assertSame('new prompt', $result['prompt']);
    }

    public function testUpdateExplanationPersists(): void
    {
        $db = new FakeSupabaseClient(['round2_questions' => [['id' => 'q1', 'explanation' => null]]]);
        $editors = new Editors($db);

        $result = $editors->updateExplanation('q1', 'a cheeky explanation');

        self::assertSame('a cheeky explanation', $result['explanation']);
    }
}
