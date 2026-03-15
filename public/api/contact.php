<?php
// contact.php - Handles form submissions from the Astro frontend

// Allow CORS only from specific origins (Security)
$allowed_origins = ['https://ks-polonia.de', 'https://www.ks-polonia.de', 'http://localhost:4321', 'http://127.0.0.1:4321'];
$origin = isset($_SERVER['HTTP_ORIGIN']) ? $_SERVER['HTTP_ORIGIN'] : '';

if (in_array($origin, $allowed_origins)) {
    header('Access-Control-Allow-Origin: ' . $origin);
} else {
    // If origin is not allowed, still return standard headers but block processing later
    // Could also just strictly deny, but this approach allows local testing to fail gracefully
    header('Access-Control-Allow-Origin: https://ks-polonia.de'); 
}

header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');
header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    exit(0);
}

// Security: Enforce allowed origin strictly for POST
if ($origin !== '' && !in_array($origin, $allowed_origins)) {
    http_response_code(403);
    echo json_encode(['error' => 'Forbidden: Invalid Origin.']);
    exit;
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['error' => 'Method Not Allowed']);
    exit;
}

// Get POST data (handle both JSON payload and standard form encodings)
$input = file_get_contents('php://input');
$data = json_decode($input, true);

if (!$data) {
    $data = $_POST;
}

// Security: Honeypot Check (Spam Protection)
// If the hidden 'website_url' field is filled out, it's a bot.
$honeypot = isset($data['website_url']) ? trim($data['website_url']) : '';
if (!empty($honeypot)) {
    // Silently reject the bot submission but pretend it was successful so they don't try again
    echo json_encode(['success' => true, 'message' => 'Vielen Dank! Ihre Nachricht wurde erfolgreich gesendet.']);
    exit;
}

// Basic validation
$name = isset($data['name']) ? trim($data['name']) : '';
$email = isset($data['email']) ? trim($data['email']) : '';
$subject = isset($data['subject']) ? trim($data['subject']) : '';
$message = isset($data['message']) ? trim($data['message']) : '';

if (empty($name) || empty($email) || empty($message)) {
    http_response_code(400);
    echo json_encode(['error' => 'Bitte alle Pflichtfelder ausfüllen.']);
    exit;
}

if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
    http_response_code(400);
    echo json_encode(['error' => 'Ungültige E-Mail-Adresse.']);
    exit;
}

// Include PHPMailer classes
require __DIR__ . '/Exception.php';
require __DIR__ . '/PHPMailer.php';
require __DIR__ . '/SMTP.php';

use PHPMailer\PHPMailer\PHPMailer;
use PHPMailer\PHPMailer\Exception;

$mail = new PHPMailer(true);

try {
    // Server settings
    // $mail->SMTPDebug = 2; // Enable verbose debug output (for testing only)
    $mail->isSMTP();
    $mail->Host       = 'mail.your-server.de';
    $mail->SMTPAuth   = true;
    $mail->Username   = 'info@ks-polonia.de';
    $mail->Password   = 'C4XOidAid08XX7U6';
    $mail->SMTPSecure = PHPMailer::ENCRYPTION_STARTTLS; // Enable TLS encryption
    $mail->Port       = 587;                         // TCP port to connect to

    // Internal encoding
    $mail->CharSet = 'UTF-8';

    // Recipients
    // The email must be sent FROM an address authorized on your server
    $mail->setFrom('info@ks-polonia.de', 'KS Polonia Website Formular');
    
    // Add the sender as Reply-To
    $mail->addReplyTo($email, $name);
    
    // Destination address (can be info@ks-polonia.de or any administrative address)
    $mail->addAddress('info@ks-polonia.de', 'KS Polonia Info');

    // Email Subject mapping
    $subjectPrefix = "Neue Nachricht über die Webseite";
    if ($subject === 'probetraining') {
        $subjectPrefix = "Anfrage Probetraining";
    } elseif ($subject === 'sponsoring') {
        $subjectPrefix = "Anfrage Sponsoring";
    } elseif ($subject === 'allgemein') {
        $subjectPrefix = "Allgemeine Anfrage";
    }

    // Content
    $mail->isHTML(false); // Send as plain text format
    $mail->Subject = $subjectPrefix . " - von " . $name;
    
    // Build email body
    $body  = "Du hast eine neue Nachricht über das Kontaktformular der Website erhalten:\n\n";
    $body .= "Name: " . $name . "\n";
    $body .= "E-Mail: " . $email . "\n";
    $body .= "Betreff: " . $subject . "\n\n";
    $body .= "Nachricht:\n";
    $body .= "-------------------------------------------\n";
    $body .= $message . "\n";
    $body .= "-------------------------------------------\n";

    $mail->Body = $body;

    $mail->send();
    echo json_encode(['success' => true, 'message' => 'Vielen Dank! Ihre Nachricht wurde erfolgreich gesendet.']);
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode(['error' => "Die Nachricht konnte leider nicht gesendet werden. Server Error: {$mail->ErrorInfo}"]);
}
