import logging

from rich.logging import RichHandler


class CBase:

    # ==================================================================================================================
    # Public methods
    # ==================================================================================================================
    def __init__(self):
        self._module_logger = None
        self._internal_log_handler = None
        self.name = self.__class__.__name__

    def create_new_logger(self, logger_name: str, logger_handler: logging.Handler = logging.NullHandler(),
                          enabled=True, level=logging.DEBUG, propagate=True) -> logging.Logger:
        #logger_handler.setLevel(level)
        _internal_logger = logging.getLogger(logger_name)
        _internal_logger.handlers = [logger_handler]
        _internal_logger.propagate = propagate
        _internal_logger.setLevel(level)

        if enabled:
            _internal_logger.disabled = False
            _internal_logger.info(f"Logger {logger_name} created with ({len(_internal_logger.handlers)}) "
                                  f"handlers and has been enabled (Level {_internal_logger.level}).")
        else:
            _internal_logger.info(f"Logger {logger_name} created and has been disabled.")
            _internal_logger.disabled = True

        return _internal_logger


    @property
    def internal_log_enabled(self):
        if self._module_logger is not None:
            return not self._module_logger.disabled
        else:
            raise Exception("Internal logger not initialized")

    @internal_log_enabled.setter
    def internal_log_enabled(self, enable: bool) -> None:
        """
        Enables or disables internal logging. If disabled, the internal logger will be disabled and no messages will be
        emitted to the state queue.
        :param enable: True to enable, False to disable
        """
        if self._module_logger is not None:
            if enable:
                self._module_logger.disabled = False
                self._module_logger.info(f"Internal logger of {self.__class__.__name__} has been enabled.")

            else:
                self._module_logger.warning(f"Internal logger of {self.__class__.__name__} has been disabled.")
                self._module_logger.disabled = True
        else:
            raise Exception("Can't enable internal logger. Internal logger not initialized")#

    @property
    def internal_log_level(self):
        return self._module_logger.level

    @internal_log_level.setter
    def internal_log_level(self, level: int) -> None:
        """
        Sets the internal logging level.
        :param level:
        :return:
        """
        if self._module_logger is not None:
            if level == logging.DEBUG:
                self._module_logger.info(f"Internal log level of {self.__class__.__name__} has been set to DEBUG.")
            elif level == logging.INFO:
                self._module_logger.info(f"Internal log level of {self.__class__.__name__} has been set to INFO.")
            elif level == logging.WARNING:
                self._module_logger.info(f"Internal log level of {self.__class__.__name__} has been set to WARNING.")
            elif level == logging.ERROR:
                self._module_logger.info(f"Internal log level of {self.__class__.__name__} has been set to ERROR.")
            elif level == logging.CRITICAL:
                self._module_logger.info(f"Internal log level of {self.__class__.__name__} has been set to CRITICAL.")
            else:
                self._module_logger.info(f"Internal log level of {self.__class__.__name__} has been set to level {level}.")
            self._module_logger.setLevel(level)
        else:
            raise Exception("Can't set internal log level. Internal logger not initialized")

