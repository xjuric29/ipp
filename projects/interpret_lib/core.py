from .components import *
import os
import sys


class Interpret:
    """Hearth of interpret which controls all operations"""
    def __init__(self):
        # STATI extension
        self.__inst = 0
        self.__vars = set()

        # Interpret vars
        self.__instructionList = []
        self._flowControl = FlowControl()   # Contains instruction counter, position stack and labels dict
        self._stack = []
        self._frames = Frames()  # Contains frame stack and all frame types. More in components.py

        # Command line argument parsing
        self.__argument_parse()

        # Debugging
        self._logger = Logger(self.args.verbose)
        self._logger.print('Verbose mode is on')

    def __argument_parse(self):
        argc = len(sys.argv) - 1

        parser = ArgumentParser(add_help=False)
        parser.add_argument('-h', '--help', help='Show this text', action='store_true')
        parser.add_argument('-f', '--source', help='File with IPP18 code in XML structure', metavar='FILE', type=str)
        parser.add_argument('-s', '--stats',
                            help='File for statistics. One of the following options is required', metavar='FILE',
                            type=str)
        parser.add_argument('-i', '--insts', help='Saves to statistic file count of executed instructions',
                            action='store_true')
        parser.add_argument('-v', '--vars', help='Saves to statistic file count of used vars', action='store_true')
        parser.add_argument('-d', '--verbose', help='Show debug information', action='store_true')
        self.args = parser.parse_args()

        if self.args.help:
            if argc == 1:
                parser.print_help()
                exit()
            else:
                parser.error('bad combination of options')

        if self.args.source:
            if not os.path.isfile(self.args.source):
                exit(ExitCodes.inFileError)
        else:
            parser.error('missing source file')

        # STATI extension options
        if self.args.stats:
            if not self.args.insts and not self.args.vars:
                parser.error('missing inst/vars option')

            try:
                fp = open(self.args.stats, 'w')  # Path check
                fp.close()
                os.remove(self.args.stats)
            except OSError:
                exit(ExitCodes.outFileError)

    def start(self):
        """Starts instruction executing"""
        xml = Xml(self.args.source, self._logger, self._stack, self._frames, self._flowControl)
        self.__instructionList = xml.get_instruction_list()

        self._logger.print('instructions load ok\ninstruction list:\n{0}'.format(self.__instructionList))

        self.__set_labels()  # Loads labels first

        while True:
            instruction = self.__instructionList[self._flowControl.instructionCounter]

            if instruction is None:  # None is always on end of instruction list
                break

            self._logger.print('{0} {1} {2}'.format(self._flowControl.instructionCounter, instruction,
                                                    self._frames.globalFrame))
            instruction.exec()

            self._flowControl.instructionCounter += 1

            # STATI
            self.__inst += 1

            if self.args.vars:
                self.__vars.add(self._frames.get_var_count())

            self.__stati()

    def __set_labels(self):
        """Loads all labels address and replaces all labels instruction to nop"""
        self._logger.print('start loading labels and changing it to nop')

        nop = NOP([], self._stack, self._frames, self._flowControl)

        for instruction in self.__instructionList:
            if isinstance(instruction, LABEL):
                instruction.exec()
                self.__instructionList[self._flowControl.instructionCounter] = nop

            self._flowControl.instructionCounter += 1

        self._flowControl.instructionCounter = 0

        self._logger.print('labels load ok\ninstruction list:\n{0}\nlabels: {1}'.format(self.__instructionList,
                                                                                        self._flowControl.labelDict))

    def __stati(self):
        """Saves statistics information to given file"""
        maxVars = max(self.__vars)

        if self.args.stats:
            with open(self.args.stats, 'w') as fp:
                if self.args.insts and not self.args.vars:
                    print(str(self.__inst), file=fp)
                elif not self.args.insts and self.args.vars:
                    print(str(maxVars), file=fp)
                else:
                    try:
                        if sys.argv.index("--insts") > sys.argv.index("--vars"):
                            print(str(maxVars), file=fp)
                            print(str(self.__inst), file=fp)
                        else:
                            print(str(self.__inst), file=fp)
                            print(str(maxVars), file=fp)
                    except ValueError:
                        exit(ExitCodes.internalError)
