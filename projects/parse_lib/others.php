<?php
/**
 * IPP 2018 project 1 - other functions
 * @file others.php
 * @author Jiri Jurica
 */

function printLog($message) {
    global $verbose;
    if ($verbose) fwrite(STDERR, $message);
}

