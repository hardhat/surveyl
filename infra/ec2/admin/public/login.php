<?php

declare(strict_types=1);

require __DIR__ . '/bootstrap.php';

use Surveyle\Admin\AdminAuthError;

$error = null;
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $email = (string) ($_POST['email'] ?? '');
    $password = (string) ($_POST['password'] ?? '');
    try {
        $session = $auth->login($email, $password);
        $_SESSION['admin_user_id'] = $session['user_id'];
        $_SESSION['admin_email'] = $session['email'];
        header('Location: review.php');
        exit;
    } catch (AdminAuthError $e) {
        $error = $e->getMessage();
    }
}

include __DIR__ . '/../templates/login.php';
