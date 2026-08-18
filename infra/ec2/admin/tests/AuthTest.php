<?php

declare(strict_types=1);

namespace Surveyle\Admin\Tests;

use PHPUnit\Framework\TestCase;
use Surveyle\Admin\AdminAuthError;
use Surveyle\Admin\Auth;
use Surveyle\Admin\Tests\Fakes\FakeSupabaseAuthClient;
use Surveyle\Admin\Tests\Fakes\FakeSupabaseClient;

class AuthTest extends TestCase
{
    public function testValidAdminCredentialsLogIn(): void
    {
        $authClient = new FakeSupabaseAuthClient(
            ['email' => 'admin@surveyle.co.uk', 'password' => 'correct-horse'],
            'user-1'
        );
        $db = new FakeSupabaseClient(['admins' => [['user_id' => 'user-1']]]);
        $auth = new Auth($authClient, $db);

        $session = $auth->login('admin@surveyle.co.uk', 'correct-horse');

        self::assertSame('user-1', $session['user_id']);
        self::assertSame('admin@surveyle.co.uk', $session['email']);
    }

    public function testInvalidCredentialsAreRejected(): void
    {
        $authClient = new FakeSupabaseAuthClient(
            ['email' => 'admin@surveyle.co.uk', 'password' => 'correct-horse'],
            'user-1'
        );
        $db = new FakeSupabaseClient(['admins' => [['user_id' => 'user-1']]]);
        $auth = new Auth($authClient, $db);

        $this->expectException(AdminAuthError::class);
        $auth->login('admin@surveyle.co.uk', 'wrong-password');
    }

    public function testNonAdminUserIsRejectedEvenWithValidSupabaseCredentials(): void
    {
        $authClient = new FakeSupabaseAuthClient(
            ['email' => 'someone@example.com', 'password' => 'pw'],
            'user-2'
        );
        $db = new FakeSupabaseClient(['admins' => [['user_id' => 'user-1']]]);
        $auth = new Auth($authClient, $db);

        $this->expectException(AdminAuthError::class);
        $auth->login('someone@example.com', 'pw');
    }
}
