<?php
/**
 * IPP 2018 project 1 - lexical analyzer part
 * @file parse_lib/scanner.php
 * @author Jiri Jurica
 */

# Tokens structure:
# header array(tokenNumber)
# opcode array(tokenNumber, instructionNumber)
# labelType array(tokenNumber, text)
# label array(tokenNumber, text)
# var array(tokenNumber, text)
# constant array(tokenNumber, type, value)
# eof array(tokenNumber)

/**
 * @param $word - which is should checking
 * @return int - if $word is instruction, returns instruction number else -1
 */
function isInstruction($word) {
    global $instructions;
    $counter = 0;
    $result = false;

    foreach ($instructions as $inst) {
        if (preg_match("~^" . $inst . "$~i", $word)) {
            $result = true;
            break;
        }

        $counter++;
    }

    return ($result ? $counter : -1);
}

function scanner() {
    global $STDIN;  # !!!!
    global $comments;
    $result = array();

    # Getting line with code
    while (true) {
        if (($rawLine = fgets($STDIN)) == false) { # If EOF
            printLog("Scanner: End of file occurs\n");
            array_push($result, array(tokenEOF));
            return $result;
        }

        # Analyzes new line if first char of line is '#' or '\n'
        if (preg_match("~^\s*#~", $rawLine)) {
            $comments++;
            continue;
        }
        elseif (preg_match("~^\s*$~", $rawLine)) continue;

        # Gets info about comment in middle of line
        $splitLine = explode("#", $rawLine);
        $words = preg_split("~\s+~", $splitLine[0]);   #Array like ("MOVE", "GF@counter", "string@")
        # If line starts or ends with white chars, explode fills also "" to start or end
        if (end($words) == "") array_pop($words);
        if ($words[0] == "") array_shift($words);

        if (count($splitLine) > 1) $comments++;
        break;
    }
    $wordNumber = 0;
    printLog("Scanner: new line\n");

    # Checking words
    foreach ($words as $word) {
        # If word contains "@" is constant or var
        if (preg_match("~@~", $word)) {
            # If starts with int|bool|string it is constant
            if (preg_match("~^(int|bool|string)~", $word)) {
                # Checking correct write of constant
                if (preg_match("~^int@[+-]?[0-9]+$~", $word) ||
                    preg_match("~^bool@(true|false)$~", $word) ||
                    (preg_match("~^string@~", $word) &&
                    !preg_match("~(\\\\[0-9]{0,2}($|\p{L}|\p{M}|\p{S}|\p{P}\p{Z}|\p{C}| )|\\\\[0-9]{4,})~u", $word))) {
                    $token = array_merge(array(tokenConst), explode("@", $word, 2));
                    array_push($result, $token);
                    printLog("Scanner: constant\n");
                }

                else {
                    printLog("Scanner: constant error\n");
                    exit(lexicalSyntaxError);
                }
            }
            # Else it is variable
            else {
                # Checking correct write of var
                if (preg_match("~^(LF|TF|GF)@[a-zA-Z_\-$&%*][a-zA-Z0-9_\-$&%*]*$~", $word)) {
                    array_push($result, array(tokenVar, $word));
                    printLog("Scanner: variable\n");
                }

                else {
                    printLog("Scanner: var error\n");
                    exit(lexicalSyntaxError);
                }
            }
        }
        # In other case is opcode, label, labelType or header
        else {
            # If word is exactly int|bool|string it is labelType
            if (preg_match("~^(int|bool|string)$~", $word)) {
                array_push($result, array(tokenLabelType, $word));
                printLog("Scanner: labelType\n");
            }
            # Else it is opcode, label or header
            else {
                # If word is .ippcode18, token is header
                if (preg_match("~^\.ippcode18$~i", $word)) {
                    array_push($result, array(tokenHeader));
                    printLog("Scanner: header\n");
                }
                # Opcode or label
                else {
                    # If words is in names of instructions is it opcode or label
                    if (($instructionNumber = isInstruction($word)) != -1) {
                        # Opcode
                        if ($wordNumber == 0) {
                            array_push($result, array(tokenOpcode, $instructionNumber));
                            printLog("Scanner: opcode\n");
                        }
                        # Label
                        else {
                            array_push($result, array(tokenLabel, $word));
                            printLog("Scanner: label\n");
                        }
                    }
                    # Label
                    else {
                        # Checking correct write of label
                        if (preg_match("~^[a-zA-Z_\-$&%*][a-zA-Z0-9_\-$&%*]*$~", $word)) {
                            array_push($result, array(tokenLabel, $word));
                            printLog("Scanner: label\n");
                        }

                        else {
                            printLog("Scanner: label error\n");
                            exit(lexicalSyntaxError);
                        }
                    }
                }
            }
        }

        $wordNumber++;
    }

    return $result;
}