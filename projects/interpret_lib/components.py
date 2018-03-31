from .instructions import *
import re
import xml.etree.ElementTree as ET


class Xml:
    def __init__(self, xml_file, logger, stack, frames, flowControl):
        self.__instructionList = None  # For right order of instructions
        self.__logger = logger
        self._stack = stack
        self._frames = frames
        self._flowControl = flowControl    # Contains instruction counter and label stack

        try:
            xml = ET.parse(xml_file)
            self.__xmlRoot = xml.getroot()
        except ET.ParseError:
            self.__logger.print('bad xml structure')
            exit(ExitCodes.xmlError)

    def get_instruction_list(self):
        if self.__instructionList:  # If instruction list has been generated, returns it
            return self.__instructionList
        else:
            self.__logger.print('xml parsing')
            self.__instructionList = []

            # Check required attribute language="IPPcode18"
            try:
                if not re.match('^ippcode18$', self.__xmlRoot.attrib['language'], re.IGNORECASE):
                    self.__logger.print('bad programming language in root element')
                    exit(ExitCodes.xmlError)
            except KeyError:
                self.__logger.print('missing attribute language in root element')
                exit(ExitCodes.xmlError)

            for child in self.__xmlRoot:
                if child.tag != 'instruction':
                    self.__logger.print('bad element (expected instruction) in xml: {0}'.format(child.tag))
                    exit(ExitCodes.xmlError)

                instAtribs = child.attrib
                if 'opcode' not in instAtribs or 'order' not in instAtribs or len(instAtribs) != 2:
                    self.__logger.print('bad args in instruction: {0}'.format(instAtribs))
                    exit(ExitCodes.xmlError)

                operands = []
                self.__logger.print('xml child: {0} {1}'.format(child.tag, instAtribs))

                for number, childsChild in enumerate(child, 1):
                    if number > 3 or childsChild.tag != 'arg' + str(number):
                        self.__logger.print('bad element (expected arg1-3) in xml: {0}'.format(childsChild.tag))
                        exit(ExitCodes.xmlError)

                    argAtribs = childsChild.attrib

                    if 'type' not in argAtribs or len(argAtribs) != 1:
                        self.__logger.print('bad attributes in arg: {0}'.format(argAtribs))
                        exit(ExitCodes.xmlError)

                    operands.append(self.__convert_arg(argAtribs['type'], str(childsChild.text)))
                    self.__logger.print('xml child\'s child: {0} {1} {2}'.format(childsChild.tag, childsChild.attrib,
                                                                               childsChild.text))

                self.__instructionList.append(eval(instAtribs['opcode'])(operands, self._stack, self._frames,
                                                                         self._flowControl))

            return self.__instructionList

    def __convert_arg(self, type, value):
        if type == 'var':
            return Var(value, self._frames)
        elif type in ['int', 'bool', 'string']:
            return Const(type, value)
        elif type == 'label':
            return Label(value)
        elif type == 'type':
            return Type(value)
        else:
            exit(ExitCodes.xmlError)


class Frames:
    def __init__(self):
        self.globalFrame = {}
        self.__frameStack = []
        self.__localFrame = None
        self.__tmpFrame = None

    def create_frame(self):
        self.__tmpFrame = {}

    def push_frame(self):
        self.__frameStack.append(self.get_frame())
        self.__tmpFrame = None

    def pop_frame(self):
        self.__tmpFrame = self.get_local_frame()
        self.__frameStack.pop()

    def get_frame(self):
        if self.__tmpFrame is None:
            exit(ExitCodes.runErrorMissingFrame)

        return self.__tmpFrame

    def get_local_frame(self):
        try:
            return self.__frameStack[-1]
        except IndexError:
            exit(ExitCodes.runErrorMissingFrame)


class FlowControl:
    def __init__(self):
        self.instructionCounter = 1
        self.positionStack = []
        self.labelDict = {}
