from .others import *
import re


# Defines ippcode18 data types
class Var:
    def __init__(self, arg_value, frames):
        if re.match(r'^(LF|TF|GF)@[a-zA-Z_\-$&%*][a-zA-Z0-9_\-$&%*]*$', arg_value):
            self.__frame, self.__name = arg_value.split('@')
        else:
            exit(ExitCodes.syntaxError)

        self.__frames = frames

    def get_frame(self):
        return self.__frame

    def get_name(self):
        return self.__name

    def define(self):
        if self.__frame == 'GF':
            self.__frames.globalFrame[self.__name] = None
        elif self.__frame == 'LF':
            self.__frames.get_local_frame()[self.__name] = None
        elif self.__frame == 'TF':
            self.__frames.get_frame()[self.__name] = None

    def set_value(self, value):
        if self.__frame == 'GF':
            self.__frames.globalFrame[self.__name] = value
        elif self.__frame == 'LF':
            self.__frames.get_local_frame()[self.__name] = value
        elif self.__frame == 'TF':
            self.__frames.get_frame()[self.__name] = value

    def get_value(self):    # Put access to var if is defined in frame. Does not check if is initialized or not
        if self.__frame == 'GF':
            try:
                return self.__frames.globalFrame[self.__name]
            except KeyError:
                exit(ExitCodes.runErrorMissingVar)
        elif self.__frame == 'LF':
            try:
                return self.__frames.get_local_frame()[self.__name]
            except KeyError:
                exit(ExitCodes.runErrorMissingVar)
        elif self.__frame == 'TF':
            try:
                return self.__frames.get_frame()[self.__name]
            except KeyError:
                exit(ExitCodes.runErrorMissingVar)

    def get_value_protected(self):  # If var contains None, program wil exit with error code
        value = self.get_value()

        if value is None:
            exit(ExitCodes.runErrorMissingValue)
        else:
            return value


class SimpleType:  # Helping class
    def __init__(self):
        self._value = None

    def get_value(self):
        return self._value


class Const(SimpleType):
    def __init__(self, type, value):
        if type == 'int' and re.match(r'^[+-]?[0-9]+$', value):
            self._value = int(value)
        elif type == 'bool' and re.match(r'^(true|false)$', value):
            if value == 'true':
                self._value = True
            else:
                self._value = False
        elif type == 'string' and not re.match(r'(\\[0-9]{0,2}($|[^0-9\\])|\\[0-9]{4,})', value, re.UNICODE):
            self.__replace_escape_seq(value)
        else:
            exit(ExitCodes.syntaxError)

    def __replace_escape_seq(self, value):
        escapePattern = re.compile(r'(\\[0-9]{3})', re.UNICODE)

        parts = escapePattern.split(value)
        value = ''

        for part in parts:
            if escapePattern.match(part):
                part = chr(int(part[1:]))  # From \065 -> 065 -> 65 -> A

            value += part

            self._value = value


class Label(SimpleType):
    def __init__(self, value):
        if re.match(r'^[a-zA-Z_\-$&%*][a-zA-Z0-9_\-$&%*]*$', value):
            self._value = value
        else:
            exit(ExitCodes.syntaxError)


class Type(SimpleType):
    def __init__(self, value):
        if value == 'int':
            self._value = int
        elif value == 'bool':
            self._value = bool
        elif value == 'string':
            self._value = str
        else:
            exit(ExitCodes.syntaxError)


# Instructions part
class Instruction:
    def __init__(self, stack, frames, flow_control):
        self._instructionRequiredTypes = None  # Expects some list like [Var, [Const, Var], [Const, Var]]
        self._operands = None  # Checked final operands for executing
        self._stack = stack
        self._frames = frames
        self._flowControl = flow_control

    def _check_operands(self, operand_list):
        if len(operand_list) != len(self._instructionRequiredTypes):
            exit(ExitCodes.syntaxError)

        for entity, operand in zip(self._instructionRequiredTypes, operand_list):
            if isinstance(entity, list):
                correct = False

                for type in entity:  # If is there moore possibilities in list. This part expand them
                    if isinstance(operand, type):
                        correct = True

                if not correct:
                    exit(ExitCodes.semanticError)
            else:
                if not isinstance(operand, entity):  # Checking just one possibility for operand
                    exit(ExitCodes.semanticError)

        self._operands = operand_list

    def _get_checked_value(self, entity):
        if isinstance(entity, Const):
            return entity.get_value()
        else:
            return entity.get_value_protected()


# Work with frames, calling functions
class MOVE(Instruction):
    def __init__(self, operands_list, stack, frames, flow_control):
        super().__init__(stack, frames, flow_control)

        self._instructionRequiredTypes = [Var, [Const, Var]]
        self._check_operands(operands_list)

    def exec(self):
        value = self._get_checked_value(self._operands[1])

        self._operands[0].set_value(value)


class CREATEFRAME(Instruction):
    def __init__(self, operands_list, stack, frames, flow_control):
        super().__init__(stack, frames, flow_control)

        self._instructionRequiredTypes = []
        self._check_operands(operands_list)

    def exec(self):
        self._frames.create_frame()


class PUSHFRAME(Instruction):
    def __init__(self, operands_list, stack, frames, flow_control):
        super().__init__(stack, frames, flow_control)

        self._instructionRequiredTypes = []
        self._check_operands(operands_list)

    def exec(self):
        self._frames.push_frame()


class POPFRAME(Instruction):
    def __init__(self, operands_list, stack, frames, flow_control):
        super().__init__(stack, frames, flow_control)

        self._instructionRequiredTypes = []
        self._check_operands(operands_list)

    def exec(self):
        self._frames.pop_frame()


class DEFVAR(Instruction):
    def __init__(self, operands_list, stack, frames, flow_control):
        super().__init__(stack, frames, flow_control)

        self._instructionRequiredTypes = [Var]
        self._check_operands(operands_list)

    def exec(self):
        self._operands[0].define()


class CALL(Instruction):
    def __init__(self, operands_list, stack, frames, flow_control):
        super().__init__(stack, frames, flow_control)

        self._instructionRequiredTypes = [Label]
        self._check_operands(operands_list)

    def exec(self):
        instructionCounter = self._flowControl.instructionCounter
        positionStack = self._flowControl.positionStack
        labelDict = self._flowControl.labelDict

        # + 1 missing because after executing each instruction instruction counter increase value
        positionStack.append(instructionCounter)

        try:
            self._flowControl.instructionCounter = labelDict[self._operands[0].get_value()]
        except KeyError:
            exit(ExitCodes.semanticError)


class RETURN(Instruction):
    def __init__(self, operands_list, stack, frames, flow_control):
        super().__init__(stack, frames, flow_control)

        self._instructionRequiredTypes = []
        self._check_operands(operands_list)

    def exec(self):
        positionStack = self._flowControl.positionStack

        try:
            self._flowControl.instructionCounter = positionStack.pop()
        except KeyError:
            exit(ExitCodes.semanticError)


# Stack instructions
class PUSHS(Instruction):
    def __init__(self, operands_list, stack, frames, flow_control):
        super().__init__(stack, frames, flow_control)

        self._instructionRequiredTypes = [[Const, Var]]
        self._check_operands(operands_list)

    def exec(self):
        self._stack.append(self._get_checked_value(self._operands[0]))


class POPS(Instruction):
    def __init__(self, operands_list, stack, frames, flow_control):
        super().__init__(stack, frames, flow_control)

        self._instructionRequiredTypes = [Var]
        self._check_operands(operands_list)

    def exec(self):
        try:
            self._operands[0].set_value(self._stack.pop())
        except KeyError:
            exit(ExitCodes.runErrorMissingValue)


# Arithmetic instructions
class ADD(Instruction):
    def __init__(self, operands_list, stack, frames, flow_control):
        super().__init__(stack, frames, flow_control)

        self._instructionRequiredTypes = [Var, [Const, Var], [Const, Var]]
        self._check_operands(operands_list)

    def exec(self):
        operand1 = self._get_checked_value(self._operands[1])
        operand2 = self._get_checked_value(self._operands[2])

        if isinstance(operand1, int) and isinstance(operand2, int):
            self._operands[0].set_value(operand1 + operand2)
        else:
            exit(ExitCodes.runErrorBadType)


class SUB(Instruction):
    def __init__(self, operands_list, stack, frames, flow_control):
        super().__init__(stack, frames, flow_control)

        self._instructionRequiredTypes = [Var, [Const, Var], [Const, Var]]
        self._check_operands(operands_list)

    def exec(self):
        operand1 = self._get_checked_value(self._operands[1])
        operand2 = self._get_checked_value(self._operands[2])

        if isinstance(operand1, int) and isinstance(operand2, int):
            self._operands[0].set_value(operand1 - operand2)
        else:
            exit(ExitCodes.runErrorBadType)


class MUL(Instruction):
    def __init__(self, operands_list, stack, frames, flow_control):
        super().__init__(stack, frames, flow_control)

        self._instructionRequiredTypes = [Var, [Const, Var], [Const, Var]]
        self._check_operands(operands_list)

    def exec(self):
        operand1 = self._get_checked_value(self._operands[1])
        operand2 = self._get_checked_value(self._operands[2])

        if isinstance(operand1, int) and isinstance(operand2, int):
            self._operands[0].set_value(operand1 * operand2)
        else:
            exit(ExitCodes.runErrorBadType)


class IDIV(Instruction):
    def __init__(self, operands_list, stack, frames, flow_control):
        super().__init__(stack, frames, flow_control)

        self._instructionRequiredTypes = [Var, [Const, Var], [Const, Var]]
        self._check_operands(operands_list)

    def exec(self):
        operand1 = self._get_checked_value(self._operands[1])
        operand2 = self._get_checked_value(self._operands[2])

        if isinstance(operand1, int) and isinstance(operand2, int):
            if operand2 == 0:
                exit(ExitCodes.runErrorZeroDivision)

            self._operands[0].set_value(operand1 // operand2)
        else:
            exit(ExitCodes.runErrorBadType)


class LT(Instruction):
    def __init__(self, operands_list, stack, frames, flow_control):
        super().__init__(stack, frames, flow_control)

        self._instructionRequiredTypes = [Var, [Const, Var], [Const, Var]]
        self._check_operands(operands_list)

    def exec(self):
        operand1 = self._get_checked_value(self._operands[1])
        operand2 = self._get_checked_value(self._operands[2])

        if (isinstance(operand1, int) and isinstance(operand2, int)) or \
                (isinstance(operand1, bool) and isinstance(operand2, bool) or
                 (isinstance(operand1, str) and isinstance(operand2, str))):
            self._operands[0].set_value(operand1 < operand2)
        else:
            exit(ExitCodes.runErrorBadType)


class GT(Instruction):
    def __init__(self, operands_list, stack, frames, flow_control):
        super().__init__(stack, frames, flow_control)

        self._instructionRequiredTypes = [Var, [Const, Var], [Const, Var]]
        self._check_operands(operands_list)

    def exec(self):
        operand1 = self._get_checked_value(self._operands[1])
        operand2 = self._get_checked_value(self._operands[2])

        if (isinstance(operand1, int) and isinstance(operand2, int)) or \
                (isinstance(operand1, bool) and isinstance(operand2, bool) or
                 (isinstance(operand1, str) and isinstance(operand2, str))):
            self._operands[0].set_value(operand1 > operand2)
        else:
            exit(ExitCodes.runErrorBadType)


class EQ(Instruction):
    def __init__(self, operands_list, stack, frames, flow_control):
        super().__init__(stack, frames, flow_control)

        self._instructionRequiredTypes = [Var, [Const, Var], [Const, Var]]
        self._check_operands(operands_list)

    def exec(self):
        operand1 = self._get_checked_value(self._operands[1])
        operand2 = self._get_checked_value(self._operands[2])

        if (isinstance(operand1, int) and isinstance(operand2, int)) or \
                (isinstance(operand1, bool) and isinstance(operand2, bool)):
            self._operands[0].set_value(operand1 == operand2)
        elif isinstance(operand1, str) and isinstance(operand2, str):
            self._operands[0].set_value(len(operand1) == len(operand2))
        else:
            exit(ExitCodes.runErrorBadType)


class AND(Instruction):
    def __init__(self, operands_list, stack, frames, flow_control):
        super().__init__(stack, frames, flow_control)

        self._instructionRequiredTypes = [Var, [Const, Var], [Const, Var]]
        self._check_operands(operands_list)

    def exec(self):
        operand1 = self._get_checked_value(self._operands[1])
        operand2 = self._get_checked_value(self._operands[2])

        if isinstance(operand1, bool) and isinstance(operand2, bool):
            self._operands[0].set_value(operand1 and operand2)
        else:
            exit(ExitCodes.runErrorBadType)


class OR(Instruction):
    def __init__(self, operands_list, stack, frames, flow_control):
        super().__init__(stack, frames, flow_control)

        self._instructionRequiredTypes = [Var, [Const, Var], [Const, Var]]
        self._check_operands(operands_list)

    def exec(self):
        operand1 = self._get_checked_value(self._operands[1])
        operand2 = self._get_checked_value(self._operands[2])

        if isinstance(operand1, bool) and isinstance(operand2, bool):
            self._operands[0].set_value(operand1 or operand2)
        else:
            exit(ExitCodes.runErrorBadType)


class NOT(Instruction):
    def __init__(self, operands_list, stack, frames, flow_control):
        super().__init__(stack, frames, flow_control)

        self._instructionRequiredTypes = [Var, [Const, Var]]
        self._check_operands(operands_list)

    def exec(self):
        operand = self._get_checked_value(self._operands[1])

        if isinstance(operand, bool):
            self._operands[0].set_value(not operand)
        else:
            exit(ExitCodes.runErrorBadType)


class INT2CHAR(Instruction):
    def __init__(self, operands_list, stack, frames, flow_control):
        super().__init__(stack, frames, flow_control)

        self._instructionRequiredTypes = [Var, [Const, Var]]
        self._check_operands(operands_list)

    def exec(self):
        operand = self._get_checked_value(self._operands[1])

        try:
            self._operands[0].set_value(chr(operand))
        except TypeError:
            exit(ExitCodes.runErrorBadType)
        except ValueError:
            exit(ExitCodes.runErrorBadStringOperation)


class STRI2INT(Instruction):
    def __init__(self, operands_list, stack, frames, flow_control):
        super().__init__(stack, frames, flow_control)

        self._instructionRequiredTypes = [Var, [Const, Var], [Const, Var]]
        self._check_operands(operands_list)

    def exec(self):
        operand1 = self._get_checked_value(self._operands[1])
        operand2 = self._get_checked_value(self._operands[2])

        if not isinstance(operand1, str) or not isinstance(operand2, int):
            exit(ExitCodes.runErrorBadType)

        try:
            self._operands[0].set_value(ord(operand1[operand2]))
        except KeyError:
            exit(ExitCodes.runErrorBadStringOperation)


# I/O instructions
class READ(Instruction):
    def __init__(self, operands_list, stack, frames, flow_control):
        super().__init__(stack, frames, flow_control)

        self._instructionRequiredTypes = [Var, Type]
        self._check_operands(operands_list)

    def exec(self):
        type = self._operands[1].get_value()

        try:
            load = input()

            if type == int:
                try:
                    result = int(load)
                except ValueError:
                    result = 0
            elif type == bool:
                if re.match(r'^true$', load, re.IGNORECASE):
                    result = True
                else:
                    result = False
            else:
                result = load
        except EOFError:
            result = ''

        self._operands[0].set_value(result)


class WRITE(Instruction):
    def __init__(self, operands_list, stack, frames, flow_control):
        super().__init__(stack, frames, flow_control)

        self._instructionRequiredTypes = [[Const, Var]]
        self._check_operands(operands_list)

    def exec(self):
        value = self._get_checked_value(self._operands[0])

        if value is True:
            print('true')
        elif value is False:
            print('false')
        else:
            print(value)


# String instructions
class CONCAT(Instruction):
    def __init__(self, operands_list, stack, frames, flow_control):
        super().__init__(stack, frames, flow_control)

        self._instructionRequiredTypes = [Var, [Const, Var], [Const, Var]]
        self._check_operands(operands_list)

    def exec(self):
        operand1 = self._get_checked_value(self._operands[1])
        operand2 = self._get_checked_value(self._operands[2])

        if not isinstance(operand1, str) or not isinstance(operand2, str):
            exit(ExitCodes.runErrorBadType)

        self._operands[0].set_value(operand1 + operand2)


class STRLEN(Instruction):
    def __init__(self, operands_list, stack, frames, flow_control):
        super().__init__(stack, frames, flow_control)

        self._instructionRequiredTypes = [Var, [Const, Var]]
        self._check_operands(operands_list)

    def exec(self):
        operand = self._get_checked_value(self._operands[1])

        if not isinstance(operand, str):
            exit(ExitCodes.runErrorBadType)

        self._operands[0].set_value(len(operand))


class GETCHAR(Instruction):
    def __init__(self, operands_list, stack, frames, flow_control):
        super().__init__(stack, frames, flow_control)

        self._instructionRequiredTypes = [Var, [Const, Var], [Const, Var]]
        self._check_operands(operands_list)

    def exec(self):
        operand1 = self._get_checked_value(self._operands[1])
        operand2 = self._get_checked_value(self._operands[2])

        if not isinstance(operand1, str) or not isinstance(operand2, int):
            exit(ExitCodes.runErrorBadType)

        try:
            self._operands[0].set_value(operand1[operand2])
        except KeyError:
            exit(ExitCodes.runErrorBadStringOperation)


class SETCHAR(Instruction):
    def __init__(self, operands_list, stack, frames, flow_control):
        super().__init__(stack, frames, flow_control)

        self._instructionRequiredTypes = [Var, [Const, Var], [Const, Var]]
        self._check_operands(operands_list)

    def exec(self):
        operand1 = self._get_checked_value(self._operands[1])
        operand2 = self._get_checked_value(self._operands[2])
        value = self._operands[0].get_value_protected()

        if not isinstance(operand1, int) or not isinstance(operand2, str) or not isinstance(value, str):
            exit(ExitCodes.runErrorBadType)

        if len(operand2) != 1:
            exit(ExitCodes.runErrorBadStringOperation)

        value = list(value)

        try:
            value[operand1] = operand2
        except KeyError:
            exit(ExitCodes.runErrorBadStringOperation)

        self._operands[0].set_value(''.join(value))


# Work with types
class TYPE(Instruction):
    def __init__(self, operands_list, stack, frames, flow_control):
        super().__init__(stack, frames, flow_control)

        self._instructionRequiredTypes = [Var, [Const, Var]]
        self._check_operands(operands_list)

    def exec(self):
        value = self._get_checked_value(self._operands[1])

        # Is necessary to have first if with bool, from another kind of reason is true and false instance of bool but
        # also int!!
        if isinstance(value, bool):
            self._operands[0].set_value('bool')
        elif isinstance(value, int):
            self._operands[0].set_value('int')
        elif isinstance(value, str):
            self._operands[0].set_value('string')
        else:
            self._operands[0].set_value('')


# Flow control instructions
class LABEL(Instruction):
    def __init__(self, operands_list, stack, frames, flow_control):
        super().__init__(stack, frames, flow_control)

        self._instructionRequiredTypes = [Label]
        self._check_operands(operands_list)

    def exec(self):
        instructionCounter = self._flowControl.instructionCounter
        labelDict = self._flowControl.labelDict

        labelDict[self._operands[0].get_value()] = instructionCounter


class JUMP(Instruction):
    def __init__(self, operands_list, stack, frames, flow_control):
        super().__init__(stack, frames, flow_control)

        self._instructionRequiredTypes = [Label]
        self._check_operands(operands_list)

    def exec(self):
        labelDict = self._flowControl.labelDict

        try:
            self._flowControl.instructionCounter = labelDict[self._operands[0].get_value()]
        except KeyError:
            exit(ExitCodes.semanticError)


class JUMPIFEQ(Instruction):
    def __init__(self, operands_list, stack, frames, flow_control):
        super().__init__(stack, frames, flow_control)

        self._instructionRequiredTypes = [Label, [Const, Var], [Const, Var]]
        self._check_operands(operands_list)

    def exec(self):
        labelDict = self._flowControl.labelDict
        operand1 = self._get_checked_value(self._operands[1])
        operand2 = self._get_checked_value(self._operands[2])

        if (isinstance(operand1, int) and isinstance(operand2, int)) or \
                (isinstance(operand1, bool) and isinstance(operand2, bool) or
                 (isinstance(operand1, str) and isinstance(operand2, str))):
            if operand1 == operand2:
                try:
                    self._flowControl.instructionCounter = labelDict[self._operands[0].get_value()]
                except KeyError:
                    exit(ExitCodes.semanticError)
        else:
            exit(ExitCodes.runErrorBadType)


class JUMPIFNEQ(Instruction):
    def __init__(self, operands_list, stack, frames, flow_control):
        super().__init__(stack, frames, flow_control)

        self._instructionRequiredTypes = [Label, [Const, Var], [Const, Var]]
        self._check_operands(operands_list)

    def exec(self):
        labelDict = self._flowControl.labelDict
        operand1 = self._get_checked_value(self._operands[1])
        operand2 = self._get_checked_value(self._operands[2])

        if (isinstance(operand1, int) and isinstance(operand2, int)) or \
                (isinstance(operand1, bool) and isinstance(operand2, bool) or
                 (isinstance(operand1, str) and isinstance(operand2, str))):
            if operand1 != operand2:
                try:
                    self._flowControl.instructionCounter = labelDict[self._operands[0].get_value()]
                except KeyError:
                    exit(ExitCodes.semanticError)
        else:
            exit(ExitCodes.runErrorBadType)


# Debug instructions
class DPRINT(Instruction):
    def __init__(self, operands_list, stack, frames, flow_control):
        super().__init__(stack, frames, flow_control)

        self._instructionRequiredTypes = [[Const, Var]]
        self._check_operands(operands_list)

    def exec(self):
        operand = self._operands[0].get_value()

        print(operand, file=sys.stderr)


class BREAK(Instruction):
    def __init__(self, operands_list, stack, frames, flow_control):
        super().__init__(stack, frames, flow_control)

        self._instructionRequiredTypes = []
        self._check_operands(operands_list)

    def exec(self):
        print('Stack: {0}\nInstruction counter: {1}\nDefined labels: {2}'.format(self._stack,
                                                                                 self._flowControl.instructionCounter,
                                                                                 self._flowControl.labelDict),
              file=sys.stderr)
