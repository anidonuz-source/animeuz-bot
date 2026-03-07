<?php
try {
    // PDO ulanishini sozlash
    $pdo = new PDO("mysql:host=localhost;dbname=moviebot", "moviebot", "moviebot123");
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    $pdo->exec("SET NAMES 'utf8mb4'");
} catch (PDOException $e) {
    die("❌ Ma'lumotlar bazasiga ulanishda xatolik: " . $e->getMessage());
}
?>
