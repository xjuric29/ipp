from .instructions import *
import re
import xml.etree.ElementTree as ET


class Xml:
    """Class for loading and checking xml file which generate list with executable instructions."""
    def __init__(self, xml_file, logger, stack, frames, flowControl):
        self.__instructionList = None
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
            self.__instructionList = []  # For right order of instructions

            # Check required attribute language="IPPcode18"
            try:
                if not re.match('^ippcode18$', self.__xmlRoot.attrib['language'], re.IGNORECASE):
                    self.__logger.print('bad programming language in root element')
                    exit(ExitCodes.xmlError)
            except KeyError:
                self.__logger.print('missing attribute language in root element')
                exit(ExitCodes.xmlError)

            # Instructions check
            for child in self.__xmlRoot:
                if child.tag != 'instruction':
                    self.__logger.print('bad element (expected instruction) in xml: {0}'.format(child.tag))
                    exit(ExitCodes.xmlError)

                instAttribs = child.attrib
                # Instruction attributes check
                if 'opcode' not in instAttribs or 'order' not in instAttribs or len(instAttribs) != 2:
                    self.__logger.print('bad args in instruction: {0}'.format(instAttribs))
                    exit(ExitCodes.xmlError)

                # Set args in instruction element
                operands = []
                self.__logger.print('xml child: {0} {1}'.format(child.tag, instAttribs))

                # Check args number in order. In case of random order this leads to error
                for number, childsChild in enumerate(child, 1):
                    if number > 3 or childsChild.tag != 'arg' + str(number):
                        self.__logger.print('bad element (expected arg1-3) in xml: {0}'.format(childsChild.tag))
                        exit(ExitCodes.xmlError)

                    argAttribs = childsChild.attrib

                    if 'type' not in argAttribs or len(argAttribs) != 1:
                        self.__logger.print('bad attributes in arg: {0}'.format(argAttribs))
                        exit(ExitCodes.xmlError)

                    # Xml tree represents '' value by None
                    operandValue = childsChild.text if childsChild.text is not None else ''
                    operands.append(self.__convert_arg(argAttribs['type'], operandValue))
                    self.__logger.print('xml child\'s child: {0} {1} {2}'.format(childsChild.tag, childsChild.attrib,
                                                                               childsChild.text))

                # Creating of instruction
                self.__instructionList.append(eval(instAttribs['opcode'])(operands, self._stack, self._frames,
                                                                         self._flowControl))

            self.__instructionList.append(None)  # For mark as end
            return self.__instructionList

    def __convert_arg(self, type, value):
        """For easy data type definition"""
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
    """Variables management"""
    def __init__(self):
        self.globalFrame = {}
        self.__frameStack = []
        self.__tmpFrame = None

    def create_frame(self):
        """Creates new tmp frame"""
        self.__tmpFrame = {}

    def push_frame(self):
        """Saves tmp frame to frame stack"""
        self.__frameStack.append(self.get_frame())
        self.__tmpFrame = None

    def pop_frame(self):
        """From top of frame stack saves frame to tmpFrame var"""
        self.__tmpFrame = self.get_local_frame()
        self.__frameStack.pop()

    def get_frame(self):
        """Returns tmp frame if exists"""
        if self.__tmpFrame is None:
            exit(ExitCodes.runErrorMissingFrame)

        return self.__tmpFrame

    def get_local_frame(self):
        """Returns local frame if exists"""
        try:
            return self.__frameStack[-1]
        except IndexError:
            exit(ExitCodes.runErrorMissingFrame)

    def get_var_count(self):
        """Returns actual number of vars in all frames"""
        count = 0

        for gVar in self.globalFrame:
            count += 1

        for frame in self.__frameStack:
            for lVar in frame:
                count += 1

        if type(self.__tmpFrame) == dict:
            for tVar in self.__tmpFrame:
                count += 1

        return count


class FlowControl:
    """Instructions order management"""
    def __init__(self):
        self.instructionCounter = 0
        self.positionStack = []
        self.labelDict = {}
