import os
from enum import IntEnum


class LogLevel(IntEnum):
    DEBUG = 0
    INFO = 1
    ERROR = 2


LOG_LEVEL = LogLevel[os.getenv('LOG_LEVEL', LogLevel.INFO.name)]


class Logger:
    """ Simple logger. Will use env variable `LOG_LEVEL` if set. """

    def __init__(self, level=LOG_LEVEL):
        self.level = level

    def log(self, msg, level=LogLevel.INFO):
        if (level >= self.level):
            print(msg)

    def debug(self, msg):
        self.log(msg, LogLevel.DEBUG)

    def info(self, msg):
        self.log(msg, LogLevel.INFO)

    def error(self, msg):
        self.log(msg, LogLevel.ERROR)
