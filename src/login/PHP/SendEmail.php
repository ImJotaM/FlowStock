<?php

require '../../../3rd_party/PHP/vendor/autoload.php';

use PHPMailer\PHPMailer\PHPMailer;
use PHPMailer\PHPMailer\Exception;
use Dotenv\Dotenv;

$dotenv = Dotenv::createImmutable(__DIR__ . '/../../../private');
$dotenv->load();

$ouremail = 'weareflowstock@gmail.com';
$ourpass = $_ENV['SMTP_PASSWORD'];

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    
    $email = $_POST['email'];

    if (empty($email)) {
        echo "O campo de e-mail é obrigatório!";
        exit();
    }

    if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
        echo "Endereço de e-mail inválido!";
        exit();
    }

    $mail = new PHPMailer(true);

    try {
        
        $mail->isSMTP();
        $mail->Host = 'smtp.gmail.com';
        $mail->SMTPAuth = true;
        $mail->Username = $ouremail;
        $mail->Password = $ourpass;
        $mail->SMTPSecure = PHPMailer::ENCRYPTION_STARTTLS;
        $mail->Port = 587;

        $mail->setFrom($ouremail, 'FlowStock');
        $mail->addAddress($email);

        $mail->isHTML(true);
        $mail->Subject = 'Redefinição de senha';
        $mail->Body    = 'Clique no link para redefinir sua senha: <a href="http://seusite.com/redefinir_senha?email=' . urlencode($email) . '">Redefinir senha</a>';

        $mail->send();
        echo 'E-mail enviado com sucesso!';
    } catch (Exception $e) {
        echo "Erro ao enviar e-mail: {$mail->ErrorInfo}";
    }
}

?>