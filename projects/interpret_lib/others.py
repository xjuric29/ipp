import argparse
from .exit_codes import *
from datetime import datetime
import sys


class Logger:
    def __init__(self, verbose):
        self.verbose = verbose

    def print(self, message):
        if self.verbose:
            message = "{0} {1}".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), message)
            print(message, file=sys.stderr)


# Little change in argparse class for exit code value from task
class ArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        self.exit(ExitCodes.badParameter, '%s: error: %s\n' % (self.prog, message))