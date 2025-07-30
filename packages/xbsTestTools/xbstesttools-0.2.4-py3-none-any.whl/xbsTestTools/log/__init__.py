# -*- coding: utf-8 -*-
import datetime
import functools
import inspect
import os
import re
import sys
import logging
from .colors import Fore as ForegroundColors
from .jsonlogger import JsonFormatter
from logging.handlers import TimedRotatingFileHandler, SysLogHandler,RotatingFileHandler
from logging import CRITICAL, ERROR, WARNING, WARN, INFO, DEBUG, NOTSET  # noqa: F401


try:
    import curses  # type: ignore
except ImportError:
    curses = None

__author__ = """Chris Hager"""
__email__ = 'chris@linuxuser.at'
__version__ = '1.7.0'

# Python 2+3 compatibility settings for logger
bytes_type = bytes
if sys.version_info >= (3,):
    unicode_type = str
    basestring_type = str
    xrange = range
else:
    # The names unicode and basestring don't exist in py3 so silence flake8.
    unicode_type = unicode  # noqa
    basestring_type = basestring  # noqa

# Formatter defaults
# 红色信息： %(end_color)s %(message)s
# 跟随等级颜色：%(color)s %(message)s
DEFAULT_FORMAT = '%(color)s[%(levelname)1.1s %(asctime)s %(pathname)s:%(lineno)d]%(color)s %(message)s'
DEFAULT_DATE_FORMAT = '%y%m%d %H:%M:%S'
DEFAULT_COLORS = {
    DEBUG: ForegroundColors.CYAN,
    INFO: ForegroundColors.GREEN,
    WARNING: ForegroundColors.YELLOW,
    ERROR: ForegroundColors.RED,
    CRITICAL: ForegroundColors.RED
}


# Attribute which all internal loggers carry
LOGZERO_INTERNAL_LOGGER_ATTR = "_is_logzero_internal"

# Logzero default logger
logger = None

# Current state of the internal logging settings
_loglevel = DEBUG
_logfile = None
_formatter = None


def setup_logger(name=__name__, logfile=None, level="DEBUG", maxBytes=0, backupCount=0, fileLoglevel=None, isRootLogger=False):

    if level == "DEBUG":
        level = DEBUG
    elif level == "WARNING":
        level = WARNING
    elif level == "ERROR":
        level = ERROR
    elif level == "WARN":
        level = WARN
    elif level == "NOTSET":
        level = NOTSET
    elif level == "CRITICAL":
        level = CRITICAL
    else:
        level = INFO

    _logger = logging.getLogger(None if isRootLogger else name)
    _logger.propagate = False

    _logger.setLevel(logging.DEBUG)

    # Setup default formatter
    _formatter = LogFormatter()

    # Reconfigure existing handlers
    stderr_stream_handler = None
    for handler in list(_logger.handlers):
        if hasattr(handler, LOGZERO_INTERNAL_LOGGER_ATTR):
            if isinstance(handler, logging.FileHandler):
                _logger.removeHandler(handler)
                continue
            elif isinstance(handler, logging.StreamHandler):
                stderr_stream_handler = handler

        handler.setLevel(level)
        handler.setFormatter(_formatter)


    stderr_stream_handler = logging.StreamHandler()
    setattr(stderr_stream_handler, LOGZERO_INTERNAL_LOGGER_ATTR, True)
    stderr_stream_handler.setLevel(level)
    stderr_stream_handler.setFormatter(_formatter)
    _logger.addHandler(stderr_stream_handler)

    if logfile:
        rotating_filehandler = RotatingFileHandler(filename=f"{logfile}{os.sep}{datetime.datetime.now().strftime('%Y%m%d')}.log", maxBytes=maxBytes, backupCount=backupCount)
        setattr(rotating_filehandler, LOGZERO_INTERNAL_LOGGER_ATTR, True)
        rotating_filehandler.setLevel(fileLoglevel or level)
        rotating_filehandler.setFormatter(_formatter)
        _logger.addHandler(rotating_filehandler)
    return _logger


class LogFormatter(logging.Formatter):
    """
    Log formatter used in Tornado. Key features of this formatter are:
    * Color support when logging to a terminal that supports it.
    * Timestamps on every log line.
    * Robust against str/bytes encoding problems.
    """

    def __init__(self,
                 color=True,
                 fmt=DEFAULT_FORMAT,
                 datefmt=DEFAULT_DATE_FORMAT,
                 colors=DEFAULT_COLORS):
        logging.Formatter.__init__(self, datefmt=datefmt)

        self._fmt = fmt
        self._colors = {}
        self._normal = ''

        if color and _stderr_supports_color():
            self._colors = colors
            self._normal = ForegroundColors.RESET

    def format(self, record):
        try:
            message = record.getMessage()
            assert isinstance(message,
                              basestring_type)  # guaranteed by logging
            # Encoding notes:  The logging module prefers to work with character
            # strings, but only enforces that log messages are instances of
            # basestring.  In python 2, non-ascii bytestri
            # ngs will make
            # their way through the logging framework until they blow up with
            # an unhelpful decoding error (with this formatter it happens
            # when we attach the prefix, but there are other opportunities for
            # exceptions further along in the framework).
            #
            # If a byte string makes it this far, convert it to unicode to
            # ensure it will make it out to the logs.  Use repr() as a fallback
            # to ensure that all byte strings can be converted successfully,
            # but don't do it by default so we don't add extra quotes to ascii
            # bytestrings.  This is a bit of a hacky place to do this, but
            # it's worth it since the encoding errors that would otherwise
            # result are so useless (and tornado is fond of using utf8-encoded
            # byte strings wherever possible).
            record.message = _safe_unicode(message)
        except Exception as e:
            record.message = "Bad message (%r): %r" % (e, record.__dict__)

        record.asctime = self.formatTime(record, self.datefmt)

        if record.levelno in self._colors:
            record.color = self._colors[record.levelno]
            record.end_color = self._normal
        else:
            record.color = record.end_color = ''

        formatted = self._fmt % record.__dict__

        if record.exc_info:
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)
        if record.exc_text:
            # exc_text contains multiple lines.  We need to _safe_unicode
            # each line separately so that non-utf8 bytes don't cause
            # all the newlines to turn into '\n'.
            lines = [formatted.rstrip()]
            lines.extend(
                _safe_unicode(ln) for ln in record.exc_text.split('\n'))
            formatted = '\n'.join(lines)
        return formatted.replace("\n", "\n    ")


def _stderr_supports_color():
    # Colors can be forced with an env variable
    if os.getenv('LOGZERO_FORCE_COLOR') == '1':
        return True

    # Windows supports colors with colorama
    if os.name == 'nt':
        return True

    # Detect color support of stderr with curses (Linux/macOS)
    if curses and hasattr(sys.stderr, 'isatty') and sys.stderr.isatty():
        try:
            curses.setupterm()
            if curses.tigetnum("colors") > 0:
                return True

        except Exception:
            pass

    return False


_TO_UNICODE_TYPES = (unicode_type, type(None))


def to_unicode(value):
    """
    Converts a string argument to a unicode string.
    If the argument is already a unicode string or None, it is returned
    unchanged.  Otherwise it must be a byte string and is decoded as utf8.
    """
    if isinstance(value, _TO_UNICODE_TYPES):
        return value
    if not isinstance(value, bytes):
        raise TypeError(
            "Expected bytes, unicode, or None; got %r" % type(value))
    return value.decode("utf-8")


def _safe_unicode(s):
    try:
        return to_unicode(s)
    except UnicodeDecodeError:
        return repr(s)


def __remove_internal_loggers(logger_to_update, disableStderrLogger=True):
    for handler in list(logger_to_update.handlers):
        if hasattr(handler, LOGZERO_INTERNAL_LOGGER_ATTR):
            if isinstance(handler, RotatingFileHandler):
                logger_to_update.removeHandler(handler)
            elif isinstance(handler, SysLogHandler):
                logger_to_update.removeHandler(handler)
            elif isinstance(handler, logging.StreamHandler) and disableStderrLogger:
                logger_to_update.removeHandler(handler)



def _get_json_formatter(json_ensure_ascii):
    supported_keys = [
        'asctime',
        'filename',
        'funcName',
        'levelname',
        'levelno',
        'lineno',
        'module',
        'message',
        'name',
        'pathname',
        'process',
        'processName',
        'threadName'
    ]

    def log_format(x):
        return ['%({0:s})s'.format(i) for i in x]

    custom_format = ' '.join(log_format(supported_keys))
    return JsonFormatter(custom_format, json_ensure_ascii=json_ensure_ascii)


def log(level="DEBUG",logfile=""):
    return setup_logger(level=level,logfile=logfile)
__all__ = ['log']