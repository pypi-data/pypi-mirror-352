"""This module contains logger related utilities."""

from __future__ import annotations

import logging
import os
from enum import Enum
from sys import stdout

from .style import Foreground_Colour, Style


class LogLevel(Enum):
    """Enum for log levels."""

    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


class Formatter(logging.Formatter):
    """An opinionated formatter for logging messages."""

    def format(self, record: logging.LogRecord):
        """Formats the log record with colours based on the log level.

        Args:
            record: The log record to format.
        """
        color = {
            logging.WARNING: Foreground_Colour.YELLOW,
            logging.ERROR: Foreground_Colour.RED,
            logging.FATAL: Foreground_Colour.RED,
            logging.INFO: Foreground_Colour.GREEN,
            logging.DEBUG: Foreground_Colour.CYAN,
        }.get(record.levelno, 0)
        # pylint: disable=protected-access
        self._style._fmt = (
            f"[%(asctime)s] [{color}%(levelname)7s{Style.RESET_ALL}] ::: %(message)s"
        )
        return super().format(record)


class Logger:
    """A generic logger class allowing logs to be send to stdout and a log file.

    Attributes:
        logger: The logger object.
    """

    def __init__(
        self,
        log_name: str,
        console_handler: None | logging.StreamHandler = logging.StreamHandler(stdout),
        log_file: None | str = None,
        log_level: int = logging.CRITICAL,
        log_format: str | logging.Formatter | None = None,
    ):
        """Initializes the logger.

        Args:
            log_name: A name for the logger, allowing differentiating between logs.
            console_handler: The handler to use for logging to stdout.
            log_file: The path to the log file.
            log_level: The level threshold of the logs to be displayed.
            log_format: The format of the logs.

        Example using the Logger class to log to stdout and a file:
        >>> logger = Logger(log_name="my_logger", log_file="my_log.log", log_level=logging.DEBUG)

        Example using the Logger class to log to stdout only:
        >>> logger = Logger(log_name="my_logger", log_level=logging.DEBUG)

        Example using the Logger class to log to a file only:
        >>> logger = Logger(log_name="my_logger", console_handler=None, log_level=logging.DEBUG)

        Example using the Logger class to log to a file only with a custom log format:
        >>> log_format = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        >>> logger = Logger(log_name="my_logger", console_handler=None, log_level=logging.DEBUG, log_format=log_format)
        """
        self.logger = logging.getLogger(log_name)
        self.logger.setLevel(log_level)

        if isinstance(log_format, logging.Formatter):
            formatter = log_format
        elif isinstance(log_format, str):
            formatter = logging.Formatter(log_format)
        else:
            formatter = Formatter()
        if console_handler:
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

        if log_file:
            log_dir = os.path.dirname(log_file)
            if not os.path.exists(log_dir) and len(log_dir.strip()) > 0:
                os.makedirs(log_dir, exist_ok=True)
            file_handler = logging.FileHandler(log_file, mode="w")
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def _log(self, msg: str, level: str) -> None:
        """Logs a message with a given level.

        Args:
            msg: The message to log.
            level: The level of the message.
        """
        if level == "info":
            self.logger.info(msg)
        if level == "debug":
            self.logger.debug(msg)
        if level == "warning":
            self.logger.warning(msg)
        if level == "error":
            self.logger.error(msg)

    def debug(self, msg: str) -> None:
        """Logs a debug message.

        Args:
            msg: The message to log.
        """
        self._log(msg, "debug")

    def info(self, msg: str) -> None:
        """Logs an info message.

        Args:
            msg: The message to log.
        """
        self._log(msg, "info")

    def warning(self, msg: str) -> None:
        """Logs a warning message.

        Args:
            msg: The message to log.
        """
        self._log(msg, "warning")

    def error(self, msg: str) -> None:
        """Logs an error message.

        Args:
            msg: The message to log.
        """
        self._log(msg, "error")
