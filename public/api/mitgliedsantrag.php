<?php
// mitgliedsantrag.php - Handles membership application submissions

// Allow CORS only from specific origins (Security)
$allowed_origins = ['https://ks-polonia.de', 'https://www.ks-polonia.de', 'http://localhost:4321', 'http://127.0.0.1:4321'];
$origin = isset($_SERVER['HTTP_ORIGIN']) ? $_SERVER['HTTP_ORIGIN'] : '';

if (in_array($origin, $allowed_origins)) {
    header('Access-Control-Allow-Origin: ' . $origin);
} else {
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

// Get POST data
$input = file_get_contents('php://input');
$data = json_decode($input, true);

if (!$data) {
    $data = $_POST;
}

// Security: Honeypot Check (Spam Protection)
$honeypot = isset($data['website_url']) ? trim($data['website_url']) : '';
if (!empty($honeypot)) {
    // Silently reject the bot
    echo json_encode(['success' => true, 'message' => 'Vielen Dank! Ihr Antrag wurde erfolgreich übermittelt.']);
    exit;
}

// Basic validation for critical fields
$vorname = isset($data['vorname']) ? trim($data['vorname']) : '';
$nachname = isset($data['nachname']) ? trim($data['nachname']) : '';
$email = isset($data['email']) ? trim($data['email']) : '';
$geburtsdatum = isset($data['geburtsdatum']) ? trim($data['geburtsdatum']) : '';

if (empty($vorname) || empty($nachname) || empty($email) || empty($geburtsdatum)) {
    http_response_code(400);
    echo json_encode(['error' => 'Bitte füllen Sie alle erforderlichen Felder aus.']);
    exit;
}

if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
    http_response_code(400);
    echo json_encode(['error' => 'Ungültige E-Mail-Adresse.']);
    exit;
}

// Map the rest of the fields securely
function get_field($key, $default = '') {
    global $data;
    return isset($data[$key]) ? trim($data[$key]) : $default;
}

$strasse = get_field('strasse');
$plz = get_field('plz');
$ort = get_field('ort');
$land = get_field('land');
$geschlecht = get_field('geschlecht');
$telefon = get_field('telefon');
$eintrittsdatum = get_field('eintrittsdatum');
$abteilungen = get_field('abteilungen', 'Keine ausgewählt');
$zahlungsart = get_field('zahlungsart', 'Überweisung');
$bemerkungen = get_field('bemerkungen');

// Include PHPMailer
require __DIR__ . '/Exception.php';
require __DIR__ . '/PHPMailer.php';
require __DIR__ . '/SMTP.php';

use PHPMailer\PHPMailer\PHPMailer;
use PHPMailer\PHPMailer\Exception;

$mail = new PHPMailer(true);

try {
    // Server settings
    $mail->isSMTP();
    $mail->Host       = 'mail.your-server.de';
    $mail->SMTPAuth   = true;
    $mail->Username   = 'info@ks-polonia.de';
    $mail->Password   = 'C4XOidAid08XX7U6';
    $mail->SMTPSecure = PHPMailer::ENCRYPTION_STARTTLS; 
    $mail->Port       = 587;                         

    // Internal encoding
    $mail->CharSet = 'UTF-8';

    // Recipients
    $mail->setFrom('info@ks-polonia.de', 'KS Polonia Mitgliedsantrag');
    $mail->addReplyTo($email, "$vorname $nachname");
    $mail->addAddress('info@ks-polonia.de', 'KS Polonia Verwaltung'); // Send to info@ks-polonia

    // Content
    $mail->isHTML(false); 
    $mail->Subject = "Neuer Mitgliedsantrag online: $vorname $nachname";
    
    // Build email body
    $body  = "Es wurde ein neuer Mitgliedsantrag über das Online-Formular eingereicht:\n\n";
    $body .= "=== 1. ANTRAGSTELLER*IN / MITGLIEDSDATEN ===\n";
    $body .= "Vorname: $vorname\n";
    $body .= "Nachname: $nachname\n";
    $body .= "Straße: $strasse\n";
    $body .= "PLZ/Ort: $plz $ort\n";
    $body .= "Land: $land\n";
    $body .= "Geburtsdatum: $geburtsdatum\n";
    $body .= "Geschlecht: $geschlecht\n\n";

    $body .= "=== 2. KONTAKTDATEN ===\n";
    $body .= "E-Mail: $email\n";
    $body .= "Telefon: $telefon\n\n";

    $body .= "=== 3. VEREINSEINTRITT & ABTEILUNGEN ===\n";
    $body .= "Gewünschtes Eintrittsdatum: $eintrittsdatum\n";
    $body .= "Gewählte Abteilungen: $abteilungen\n\n";

    $body .= "=== 4. ZAHLUNGSART ===\n";
    $body .= "Art: $zahlungsart\n\n";

    if (!empty($bemerkungen)) {
        $body .= "=== 5. ZUSATZDATEN ===\n";
        $body .= "Bemerkungen:\n$bemerkungen\n\n";
    }

    $body .= "=== 6. ZUSTIMMUNGEN ===\n";
    $body .= "✓ DSGVO und BDSG zugestimmt.\n";
    $body .= "✓ Rechtsverbindlichkeit des Antrags bestätigt.\n";

    $mail->Body = $body;

    $mail->send();
    echo json_encode(['success' => true, 'message' => 'Vielen Dank! Ihr Antrag wurde erfolgreich übermittelt. Wir werden uns in Kürze bei Ihnen melden.']);
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode(['error' => "Der Antrag konnte leider nicht gesendet werden. Server Error: {$mail->ErrorInfo}"]);
}
