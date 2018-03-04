<?php
/**
 * IPP 2018 project 1 - other functions
 * @file others.php
 * @author Jiri Jurica
 */

/**Prints message on stderr if global var is set to true
 * @param $message
 */
function printLog($message) {
    global $verbose;
    if ($verbose) fwrite(STDERR, $message);
}

