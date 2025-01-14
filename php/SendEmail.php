<?php

use PHPMAILER\PHPMAILER\PHPMAILER;
use PHPMailer\PHPMailer\Exception;

require '3rd_party/vendor/autoload.php';

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $email = $_POST['email'];

    if (empty($email)) {
        echo "O campo de e-mail é obrigatório!";
        exit();
    }

    $mail = new PHPMailer(true);

    try {
        
        $mail->isSMTP();
        $mail->Host = 'smtp.gmail.com';
        $mail->SMTPAuth = true;
        $mail->Username = 'seuemail@gmail.com';
        $mail->Password = 'suasenha';
        $mail->SMTPSecure = PHPMailer::ENCRYPTION_STARTTLS;
        $mail->Port = 587;

        $mail->setFrom('seuemail@gmail.com', 'FlowStock');
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