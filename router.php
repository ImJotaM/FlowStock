<?php

$request = $_SERVER['REQUEST_URI'];

$file = __DIR__ . $request;

if (file_exists($file) && !is_dir($file)) {
    return false;
}

include __DIR__ . '/src/login/HTML/index.html';

?>