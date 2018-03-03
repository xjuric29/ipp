<?php
/**
 * Created by PhpStorm.
 * User: jirkaj
 * Date: 3.3.18
 * Time: 20:47
 */

#$a = "anastazie k   p     j";
#var_dump(preg_split("~\s+~", $a));

#if (0) echo preg_match("~@~", "GF@co@unter");

#echo preg_match("~^(int|bool|string)~", "string@counter\\032obsahuje\\032");

#echo preg_match("~^int@[+-]?[0-9]+$~", "int@+9855445a");

#$a = "GF@counter";
#$b = array(9);
#$c = explode("@", $a);
#var_dump(array_merge(array(9), explode("@", $a)));

#echo "a"."b" . "\n" . "4";

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

var_dump($instructions);