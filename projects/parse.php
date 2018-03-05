<?php
/**
 * IPP 2018 project 1 - parse instruction from input, check structure and syntax and generate xml file for next
 * processing
 * @file parse.php
 * @author Jiri Jurica
 */

include 'parse_lib/scanner.php';
include 'parse_lib/syntax.php';
include 'parse_lib/others.php';

# Global constants and vars
# Return codes
const badParameter = 10;
const inFileError = 11;
const outFileError = 12;
const lexicalSyntaxError = 21;
const internalError = 99;

# Tokens
const tokenHeader = 0;
const tokenOpcode = 1;
const tokenLabelType = 2;
const tokenLabel = 3;
const tokenVar = 4;
const tokenConst = 5;
const tokenEOF = 6;

# Instructions - items must be upper for correct xml
$instructions = array(
    0 => "MOVE",
    1 => "CREATEFRAME",
    2 => "PUSHFRAME",
    3 => "POPFRAME",
    4 => "DEFVAR",
    5 => "CALL",
    6 => "RETURN",
    7 => "PUSHS",
    8 => "POPS",
    9 => "ADD",
    10 => "SUB",
    11 => "MUL",
    12 => "IDIV",
    13 => "LT",
    14 => "GT",
    15 => "EQ",
    16 => "AND",
    17 => "OR",
    18 => "NOT",
    19 => "INT2CHAR",
    20 => "STRI2INT",
    21 => "READ",
    22 => "WRITE",
    23 => "CONCAT",
    24 => "STRLEN",
    25 => "GETCHAR",
    26 => "SETCHAR",
    27 => "TYPE",
    28 => "LABEL",
    29 => "JUMP",
    30 => "JUMPIFEQ",
    31 => "JUMPIFNEQ",
    # Debug instructions
    32 => "DPRINT",
    33 => "BREAK");

# !!!!
#$STDIN = fopen("tests/input3", "r");
$STDIN = STDIN;

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
$locFlag = false;
$commentsFlag = false;

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

if (array_key_exists("l", $getOpts) || array_key_exists("loc", $getOpts)) $locFlag = true;
if (array_key_exists("c", $getOpts) || array_key_exists("comments", $getOpts)) $commentsFlag = true;
# If stats is used, comments or loc is required
if (($statsShort || $statsLong) && !$locFlag && !$commentsFlag) exit(badParameter);

if (($statsShort || $statsLong) && ($statsFile = fopen($fileName, "w")) == false) exit(outFileError);

$verbose = false;   # Own debug parameter
if (array_key_exists("v", $getOpts) || array_key_exists("verbose", $getOpts)) $verbose = true;

printLog("Verbose mode is on\n");

# Lexical analysis
$loc = 0;
$comments = 0;

syntaxer();

# Write statistics
if ($statsShort || $statsLong) {
    if (($locOrder = array_search("--loc", $argv)) == false) $locOrder = array_search("-l", $argv);
    if (($commentsOrder = array_search("--comments", $argv)) == false)
        $commentsOrder  = array_search("-c", $argv);

    if ($locOrder && $commentsOrder && $locOrder < $commentsOrder) {
        fwrite($statsFile, $loc . "\n");
        fwrite($statsFile, $comments . "\n");
    }
    elseif ($locOrder && $commentsOrder && $locOrder > $commentsOrder) {
        fwrite($statsFile, $comments . "\n");
        fwrite($statsFile, $loc . "\n");
    }
    elseif ($locOrder) fwrite($statsFile, $loc . "\n");
    elseif ($commentsOrder) fwrite($statsFile, $comments . "\n");

    fclose($statsFile);
}
