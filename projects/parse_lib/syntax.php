<?php
/**
 * IPP 2018 project 1 - syntax analyzer part
 * @file parse_lib/syntax.php
 * @author Jiri Jurica
 */

function syntaxer() {
    global $instructions;
    global $loc;

    # XML settings
    $domtree = new DOMDocument('1.0', 'UTF-8');
    $domtree->formatOutput = true;
    $xmlRoot = $domtree->createElement("program");
    $xmlRoot->setAttribute("language", "IPPcode18");
    $xmlRoot = $domtree->appendChild($xmlRoot);

    $line = scanner();
    # If first is not header
    if (count($line) > 1 || $line[0][0] != tokenHeader) {
        printLog("Syntaxer: missing header\n");
        exit(lexicalSyntaxError);
    }
    else printLog("Syntaxer: header\n");

    while (true) {
        $line = scanner();

        # Break in eof
        if (count($line) == 1 && $line[0][0] == tokenEOF) {
            printLog("Syntaxer: eof\n");
            break;
        }
        # Instructions checking
        elseif ($line[0][0] == tokenOpcode) {
            $loc++;

            # Creates element instruction
            $xmlInstruction = $domtree->createElement("instruction");
            $xmlInstruction->setAttribute("order", $loc);
            $xmlInstruction->setAttribute("opcode", $instructions[$line[0][1]]);

            switch ($line[0][1]) {
                # This instructions are without any operand
                case 1:     # CREATEFRAME
                case 2:     # PUSHFRAME
                case 3:     # POPFRAME
                case 6:     # RETURN
                case 33:    # BREAK
                    if (count($line) != 1) {
                        printLog("Syntaxer: bad operands " . $line[0][1] . "\n");
                        exit(lexicalSyntaxError);
                    }
                    break;
                # One var operand
                case 4:     # DEFVAR
                case 8:     # POPS
                    if (count($line) == 2 && $line[1][0] == tokenVar) {
                        # Sets first arg element
                        $xmlArg1 = $domtree->createElement("arg1", htmlspecialchars($line[1][1]));
                        $xmlArg1->setAttribute("type", "var");
                        # Sets arg1 element as instruction child
                        $xmlInstruction->appendChild($xmlArg1);
                    }
                    else {
                        printLog("Syntaxer: bad operands " . $line[0][1] . "\n");
                        exit(lexicalSyntaxError);
                    }
                    break;
                # One constant or var operand
                case 7:     # PUSHS
                case 22:    # WRITE
                case 32:    # DPRINT
                    if (count($line) == 2 && ($line[1][0] == tokenVar || $line[1][0] == tokenConst)) {
                        # Sets first arg element
                        if ($line[1][0] == tokenVar) {
                            $xmlArg1 = $domtree->createElement("arg1", htmlspecialchars($line[1][1]));
                            $xmlArg1->setAttribute("type", "var");
                        }
                        else {
                            $xmlArg1 = $domtree->createElement("arg1", htmlspecialchars($line[1][2]));
                            $xmlArg1->setAttribute("type", $line[1][1]);
                        }

                        # Sets arg1 element as instruction child
                        $xmlInstruction->appendChild($xmlArg1);
                    }
                    else {
                        printLog("Syntaxer: bad operands " . $line[0][1] . "\n");
                        exit(lexicalSyntaxError);
                    }
                    break;
                # One label operand
                case 5:     # CALL
                case 28:    # LABEL
                case 29:    # JUMP
                    if (count($line) == 2 && ($line[1][0] == tokenLabel || $line[1][0] == tokenLabelType)) {
                        # Sets first arg element
                        $xmlArg1 = $domtree->createElement("arg1", htmlspecialchars($line[1][1]));
                        $xmlArg1->setAttribute("type", "label");
                        # Sets arg1 element as instruction child
                        $xmlInstruction->appendChild($xmlArg1);
                    }
                    else {
                        printLog("Syntaxer: bad operands " . $line[0][1] . "\n");
                        exit(lexicalSyntaxError);
                    }
                    break;
                # One var operand and one constant or var operand
                case 0:     # MOVE
                case 18:    # NOT
                case 19:    # INT2CHAR
                case 24:    # STRLEN
                case 27:    # TYPE
                    if (count($line) == 3 && $line[1][0] == tokenVar && ($line[2][0] == tokenVar ||
                            $line[2][0] == tokenConst)) {
                        # Sets arg elements
                        $xmlArg1 = $domtree->createElement("arg1", htmlspecialchars($line[1][1]));
                        $xmlArg1->setAttribute("type", "var");

                        if ($line[2][0] == tokenVar) {
                            $xmlArg2 = $domtree->createElement("arg2", htmlspecialchars($line[2][1]));
                            $xmlArg2->setAttribute("type", "var");
                        }
                        else {
                            $xmlArg2 = $domtree->createElement("arg2", htmlspecialchars($line[2][2]));
                            $xmlArg2->setAttribute("type", $line[2][1]);
                        }

                        # Sets arg elements as instruction childs
                        $xmlInstruction->appendChild($xmlArg1);
                        $xmlInstruction->appendChild($xmlArg2);
                    }
                    else {
                        printLog("Syntaxer: bad operands " . $line[0][1] . "\n");
                        exit(lexicalSyntaxError);
                    }
                    break;
                # One var operand and one type operand
                case 21:    # READ
                    if (count($line) == 3 && $line[1][0] == tokenVar && $line[2][0] == tokenLabelType) {
                        # Sets arg elements
                        $xmlArg1 = $domtree->createElement("arg1", htmlspecialchars($line[1][1]));
                        $xmlArg2 = $domtree->createElement("arg2", htmlspecialchars($line[2][1]));
                        $xmlArg1->setAttribute("type", "var");
                        $xmlArg2->setAttribute("type", "type");
                        # Sets arg elements as instruction childs
                        $xmlInstruction->appendChild($xmlArg1);
                        $xmlInstruction->appendChild($xmlArg2);
                    }
                    else {
                        printLog("Syntaxer: bad operands " . $line[0][1] . "\n");
                        exit(lexicalSyntaxError);
                    }
                    break;
                # One var operand and two constant or var operand
                case 9:     # ADD
                case 10:    # SUB
                case 11:    # MUL
                case 12:    # IDIV
                case 13:    # LT
                case 14:    # GT
                case 15:    # EQ
                case 16:    # AND
                case 17:    # OR
                case 20:    # STRI2INT
                case 23:    # CONCAT
                case 25:    # GETCHAR
                case 26:    # SETCHAR
                    if (count($line) == 4 && $line[1][0] == tokenVar && ($line[2][0] == tokenVar ||
                            $line[2][0] == tokenConst) && ($line[3][0] == tokenVar ||
                            $line[3][0] == tokenConst)) {
                        # Sets arg elements
                        $xmlArg1 = $domtree->createElement("arg1", htmlspecialchars($line[1][1]));
                        $xmlArg1->setAttribute("type", "var");

                        if ($line[2][0] == tokenVar) {
                            $xmlArg2 = $domtree->createElement("arg2", htmlspecialchars($line[2][1]));
                            $xmlArg2->setAttribute("type", "var");
                        }
                        else {
                            $xmlArg2 = $domtree->createElement("arg2", htmlspecialchars($line[2][2]));
                            $xmlArg2->setAttribute("type", $line[2][1]);
                        }
                        if ($line[3][0] == tokenVar) {
                            $xmlArg3 = $domtree->createElement("arg3", htmlspecialchars($line[3][1]));
                            $xmlArg3->setAttribute("type", "var");
                        }
                        else {
                            $xmlArg3 = $domtree->createElement("arg3", htmlspecialchars($line[3][2]));
                            $xmlArg3->setAttribute("type", $line[3][1]);
                        }

                        # Sets arg elements as instruction childs
                        $xmlInstruction->appendChild($xmlArg1);
                        $xmlInstruction->appendChild($xmlArg2);
                        $xmlInstruction->appendChild($xmlArg3);
                    }
                    else {
                        printLog("Syntaxer: bad operands " . $line[0][1] . "\n");
                        exit(lexicalSyntaxError);
                    }
                    break;
                # One label operand and two constant or var operand
                case 30:    # JUMPIFEQ
                case 31:    # JUMPIFNEQ
                    if (count($line) == 4 && ($line[1][0] == tokenLabel || $line[1][0] == tokenLabelType) &&
                        ($line[2][0] == tokenVar || $line[2][0] == tokenConst) && ($line[3][0] == tokenVar ||
                            $line[3][0] == tokenConst)) {
                        # Sets arg elements
                        $xmlArg1 = $domtree->createElement("arg1", htmlspecialchars($line[1][1]));
                        $xmlArg1->setAttribute("type", "label");

                        if ($line[2][0] == tokenVar) {
                            $xmlArg2 = $domtree->createElement("arg2", htmlspecialchars($line[2][1]));
                            $xmlArg2->setAttribute("type", "var");
                        }
                        else {
                            $xmlArg2 = $domtree->createElement("arg2", htmlspecialchars($line[2][2]));
                            $xmlArg2->setAttribute("type", $line[2][1]);
                        }
                        if ($line[3][0] == tokenVar) {
                            $xmlArg3 = $domtree->createElement("arg3", htmlspecialchars($line[3][1]));
                            $xmlArg3->setAttribute("type", "var");
                        }
                        else {
                            $xmlArg3 = $domtree->createElement("arg3", htmlspecialchars($line[3][2]));
                            $xmlArg3->setAttribute("type", $line[3][1]);
                        }

                        # Sets arg elements as instruction childs
                        $xmlInstruction->appendChild($xmlArg1);
                        $xmlInstruction->appendChild($xmlArg2);
                        $xmlInstruction->appendChild($xmlArg3);
                    }
                    else {
                        printLog("Syntaxer: bad operands " . $line[0][1] . "\n");
                        exit(lexicalSyntaxError);
                    }
                    break;
                default:
                    printLog("Syntaxer: bad instruction " . $line[0][1] . "\n");
                    exit(lexicalSyntaxError);
            }

            printLog("Syntaxer: instruction " . $instructions[$line[0][1]] . "\n");
        }
        # Another error
        else {
            printLog("Syntaxer: another error\n");
            exit(lexicalSyntaxError);
        }

        $xmlRoot->appendChild($xmlInstruction);
    }

    echo $domtree->saveXML();
}