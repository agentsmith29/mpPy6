import logging

from rich.logging import RichHandler


class CBase:

    # ==================================================================================================================
    # Public methods
    # ==================================================================================================================
    def __init__(self):
        self._internal_logger = None
        self._internal_log_handler = None
        self.name = self.__class__.__name__

    def create_new_logger(self, logger_name: str,
                          logger_handler: logging.Handler = None,
                          logger_format: str = "%(asctime)s - %(name)s %(message)s",
                          to_file=None,
                          enabled=True, level=logging.DEBUG) -> logging.Logger:
        """
        Creates a new logger with the given name and handler. If no handler is given, a RichHandler will be used.

        :param enabled:
        :param logger_name:
        :param logger_handler:
        :param logger_format:
        :param to_file:
        :return:
        """
        formatter = logging.Formatter(logger_format)
        if logger_handler is None:
            logger_handler = RichHandler(rich_tracebacks=True)

        logger_handler.setLevel(level)
        logger_handler.setFormatter(formatter)

        _internal_logger = logging.getLogger(logger_name)
        _internal_logger.handlers = [logger_handler]
        _internal_logger.setLevel(logging.DEBUG)


        if to_file is not None:
            _file_handler = logging.FileHandler(to_file)
            _file_handler.setLevel(logging.DEBUG)
            _file_handler_formatter = logging.Formatter(f"%(levelname)s {logger_format})")
            _file_handler.setFormatter(_file_handler_formatter)
            _internal_logger.addHandler(_file_handler)

        if enabled:
            _internal_logger.disabled = False
            _internal_logger.info(f"Logger {logger_name} created with ({len(_internal_logger.handlers)}) handlers and has been enabled (Level {level}).")
        else:
            _internal_logger.info(f"Logger {logger_name} created and has been disabled.")
            _internal_logger.disabled = True

        return _internal_logger


    @property
    def internal_log_enabled(self):
        if self._internal_logger is not None:
            return not self._internal_logger.disabled
        else:
            raise Exception("Internal logger not initialized")

    @internal_log_enabled.setter
    def internal_log_enabled(self, enable: bool) -> None:
        """
        Enables or disables internal logging. If disabled, the internal logger will be disabled and no messages will be
        emitted to the state queue.
        :param enable: True to enable, False to disable
        """
        if self._internal_logger is not None:
            if enable:
                self._internal_logger.disabled = False
                self._internal_logger.info(f"Internal logger of {self.__class__.__name__} has been enabled.")

            else:
                self._internal_logger.warning(f"Internal logger of {self.__class__.__name__} has been disabled.")
                self._internal_logger.disabled = True
        else:
            raise Exception("Can't enable internal logger. Internal logger not initialized")#

    @property
    def internal_log_level(self):
        return self._internal_logger.handlers[0].level

    @internal_log_level.setter
    def internal_log_level(self, level: int) -> None:
        """
        Sets the internal logging level.
        :param level:
        :return:
        """
        if self._internal_logger is not None:
            if level == logging.DEBUG:
                self._internal_logger.info(f"Internal log level of {self.__class__.__name__} has been set to DEBUG.")
            elif level == logging.INFO:
                self._internal_logger.info(f"Internal log level of {self.__class__.__name__} has been set to INFO.")
            elif level == logging.WARNING:
                self._internal_logger.info(f"Internal log level of {self.__class__.__name__} has been set to WARNING.")
            elif level == logging.ERROR:
                self._internal_logger.info(f"Internal log level of {self.__class__.__name__} has been set to ERROR.")
            elif level == logging.CRITICAL:
                self._internal_logger.info(f"Internal log level of {self.__class__.__name__} has been set to CRITICAL.")
            else:
                self._internal_logger.info(f"Internal log level of {self.__class__.__name__} has been set to level {level}.")
            self._internal_logger.handlers[0].setLevel(level)
        else:
            raise Exception("Can't set internal log level. Internal logger not initialized")

