<?php
/**
 * IPP 2018 project 1 - parse instruction from input, check structure and syntax and generate xml file for next
 * processing
 * @file parse.php
 * @author Jiri Jurica
 */

# Global constants for return codes
const badParameter = 10;
const inFileError = 11;
const outFileError = 12;
const lexicalSyntaxError = 21;
const internalError = 99;

# Functions part
function printLog($message) {
    global $verbose;
    if ($verbose) fwrite(STDERR, $message);
}

# Main control structure
# Parameter parsing

$shortOpts = "hs:lcv";
$longOpts = array("help", "stats:", "loc", "comments", "verbose");
$getOpts = getopt($shortOpts, $longOpts);

if (array_key_exists("help", $getOpts) || array_key_exists("h", $getOpts)) {    # Prints help
    if ($argc == 2 && $argv[1] == "-h" || $argv[1] == "--help") {
        echo "parse.php help:\n";
        echo "-h, --help            Prints this help.\n";
        echo "-v, --verbose         Prints debug information.\n";
        echo "-s FILE, --stats FILE Select file for statistics. One of the following parameters is required.\n";
        echo "-l, --loc             Saves to statistic file count of instructions.\n";
        echo "-c, --comments        Saves to statistic file count of comments.\n";
        exit;
    }
    else exit(badParameter);
}

$statsShort = false;    # Stats extension
$statsLong = false;
$loc = false;
$comments = false;

if (array_key_exists("s", $getOpts)) {
    $fileName = $getOpts["s"];
    $statsShort = true;
}

if (array_key_exists("stats", $getOpts)) {
    if ($statsShort) exit(badParameter);
    else {
        $fileName = $getOpts["stats"];
        $statsLong = true;
    }
}

if (array_key_exists("l", $getOpts) || array_key_exists("loc", $getOpts)) $loc = true;
if (array_key_exists("c", $getOpts) || array_key_exists("comments", $getOpts)) $comments = true;
# If stats is used, comments or loc is required
if (($statsShort || $statsLong) && !$loc && !$comments) exit(badParameter);

$verbose = false;   # Own debug parameter
if (array_key_exists("v", $getOpts) || array_key_exists("verbose", $getOpts)) $verbose = true;

printLog("Verbose mode is on");
#var_dump($argv);
#var_dump($getOpts);
#echo $argc, "\n";

?>