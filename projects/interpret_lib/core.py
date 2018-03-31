from .components import *
import os
import sys


class Interpret:
    def __init__(self):
        # STATI extension
        self.__inst = 0
        self.__vars = 0

        # interpret vars
        self.__instructionList = []
        self._flowControl = FlowControl()   # Contains instruction counter, position stack and labels dict
        self._stack = []
        self._frames = Frames()  # Contains frame stack and all frame types. More in components.py

        # command line argument parsing
        self.__argument_parse()

        # debugging
        self._logger = Logger(self.args.verbose)
        self._logger.print('Verbose mode is on')

    def __argument_parse(self):
        argc = len(sys.argv) - 1

        parser = ArgumentParser(add_help=False)
        parser.add_argument('-h', '--help', help='Show this text', action='store_true')
        parser.add_argument('-f', '--source', help='File with assembly code in XML structure', metavar='FILE', type=str)
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
            try:
                fp = open(self.args.stats, 'w')
                fp.close()
                os.remove(self.args.stats)
            except OSError:
                exit(ExitCodes.outFileError)

            if not self.args.insts and not self.args.vars:
                parser.error('missing inst/vars option')

    def start(self):
        xml = Xml(self.args.source, self._logger, self._stack, self._frames, self._flowControl)
        self.__instructionList = xml.get_instruction_list()

        self._logger.print('instruction list:\n{0}'.format(self.__instructionList))
