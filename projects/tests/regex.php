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

#$word = "string@jksaadlkf\\124\\12";
#echo $word, "\n";
#echo preg_match("~(\\\\[0-9]{0,2}($|\p{L}|\p{M}|\p{S}|\p{P}\p{Z}|\p{C}| )|\\\\[0-9]{4,})~u", $word);


#"~(\\[0-9]{0,2}($|\p{L}|\p{M}|\p{S}|\p{P}\p{Z}|\p{C}| )|\\[0-9]{4,})~u"

if (20) echo "jo!\n";