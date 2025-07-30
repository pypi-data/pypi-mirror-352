"""The odd helper function."""
import argparse
import logging
import multiprocessing
import platform


_log_name = None


def get_main_logger(name):
    """Create the top-level logger."""
    global _log_name
    _log_name = name
    return logging.getLogger(name)


def get_named_logger(name):
    """Create a logger with a name.

    :param name: name of logger.
    """
    name = name.ljust(10)[:10]  # so logging is aligned
    logger = logging.getLogger('{}.{}'.format(_log_name, name))
    return logger


class ColorFormatter(logging.Formatter):
    """Custom formatter for colored logging output."""

    COLORS = {
        logging.DEBUG: "\033[90m",      # gray
        logging.INFO: "\033[37m",       # standard
        logging.WARNING: "\033[33m",    # yellow
        logging.ERROR: "\033[31m",      # red
        logging.CRITICAL: "\033[1;41m"  # white on red background
    }
    RESET = "\033[0m"

    def format(self, record):
        """Format the log record with color based on level."""
        color = self.COLORS.get(record.levelno, self.RESET)
        msg = super().format(record)
        return f"{color}{msg}{self.RESET}"


def _log_level():
    """Parser to set logging level and acquire software version/commit."""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter, add_help=False)

    modify_log_level = parser.add_mutually_exclusive_group()
    modify_log_level.add_argument(
        '--debug', action='store_const',
        dest='log_level', const=logging.DEBUG, default=logging.INFO,
        help='Verbose logging of debug information.')
    modify_log_level.add_argument(
        '--quiet', action='store_const',
        dest='log_level', const=logging.WARNING, default=logging.INFO,
        help='Minimal logging; warnings only.')

    return parser


class SafeJoinableQueue:
    """Cross-platform wrapper for multiprocessing.JoinableQueue.

    On macOS, disables qsize() and empty() which are unsupported.
    All other attributes/methods are forwarded to the underlying queue.
    """

    def __init__(self, *args, **kwargs):
        """Initialize the SafeJoinableQueue."""
        # JoinableQueue is not a class but a factory function, eugh
        object.__setattr__(
            self, "_queue", multiprocessing.JoinableQueue(*args, **kwargs))
        object.__setattr__(
            self, "_is_darwin", platform.system() == "Darwin")

    def qsize(self):
        """Return the approximate size of the queue."""
        if self._is_darwin:
            return "unknown"
        return object.__getattribute__(self, "_queue").qsize()

    def empty(self):
        """Check if the queue is empty."""
        if self._is_darwin:
            return False
        return object.__getattribute__(self, "_queue").empty()

    def full(self):
        """Check if the queue is full."""
        if self._is_darwin:
            return False
        return object.__getattribute__(self, "_queue").full()

    def __getattr__(self, attr):
        """Forward all other attributes/methods to the underlying queue."""
        return getattr(object.__getattribute__(self, "_queue"), attr)
