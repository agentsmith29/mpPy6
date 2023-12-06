import logging.handlers
import logging
import os
import time
import traceback
from multiprocessing import Process, Queue, Value

import cmp


class CProcess(Process):

    def __init__(self, state_queue: Queue, cmd_queue: Queue, kill_flag,
                 internal_logging: bool = False,
                 internal_log_level=logging.DEBUG,
                 *args, **kwargs):
        Process.__init__(self)
        self._internal_log_enabled = internal_logging
        self._internal_log_level = internal_log_level

        self.logger = None
        self.logger_handler = None

        self._internal_logger = None
        self._il_handler = None

        self.cmd_queue = cmd_queue
        self.state_queue = state_queue
        self._kill_flag = kill_flag

    # ==================================================================================================================
    #   Logging
    # ==================================================================================================================
    def create_new_logger(self, name: str) -> (logging.Logger, logging.Handler):
        _handler = logging.handlers.QueueHandler(self.state_queue)
        _logger = logging.getLogger(name)
        _logger.handlers.clear()
        _logger.handlers = [_handler]
        _logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(message)s')
        _handler.setFormatter(formatter)
        return _logger, _handler

    @property
    def internal_log_enabled(self):
        self._internal_logger.debug(f"internal_log_enabled: {not self._internal_logger.disabled}")
        return not self._internal_logger.disabled

    @internal_log_enabled.setter
    def internal_log_enabled(self, enable: bool) -> None:
        """
        Enables or disables internal logging. If disabled, the internal logger will be disabled and no messages will be
        emitted to the state queue.
        :param enable: True to enable, False to disable
        """
        self._internal_logger.disabled = not enable

    @property
    def internal_log_level(self):
        return self._internal_logger.level

    @internal_log_level.setter
    def internal_log_level(self, level: int) -> None:
        """
        Sets the internal logging level.
        :param level:
        :return:
        """
        self._internal_logger.setLevel(level)

    # ==================================================================================================================
    #   Process
    # ==================================================================================================================
    def postrun_init(self):
        """
            Dummy function  for initializing e.g. loggers (some handlers are not pickable)
            or pther non-pickable objects
        """
        pass

    def run(self):
        self.name = f"{os.getpid()}({self.name})"
        self.postrun_init()

        self._internal_logger, self._il_handler = self.create_new_logger(f"(cmp) {self.name}")
        self.internal_log_enabled = self._internal_log_enabled
        self.internal_log_level = self._internal_log_level

        self.logger, self.logger_handler = self.create_new_logger(f"{os.getpid()}({self.__class__.__name__})")
        self._internal_logger.debug(f"Child process {self.__class__.__name__} started.")

        try:
            while self._kill_flag.value:
                try:
                    cmd = self.cmd_queue.get(block=True, timeout=1)
                except:
                    continue
                if isinstance(cmd, cmp.CCommandRecord):
                    self._internal_logger.debug(
                        f"Received cmd: {cmd}, args: {cmd.args}, kwargs: {cmd.kwargs}, Signal to emit: {cmd.signal_name}")
                    try:
                        cmd.execute(self)
                    except Exception as e:
                        traceback_str = ''.join(traceback.format_tb(e.__traceback__))
                        self._internal_logger.error(f"Exception '{e}' occurred in {cmd}!. Traceback:\n{traceback_str}")
            self._internal_logger.error(f"Control Process exited. Terminating Process {os.getpid()}")
            if self._kill_flag.value == 0:
                self._internal_logger.error(f"Process {os.getpid()} received kill signal!")

        except KeyboardInterrupt:
            self._internal_logger.warning(f"Received KeyboardInterrupt! Exiting Process {os.getpid()}")
            time.sleep(1)
            self.close()
        except Exception as e:
            self._internal_logger.warning(f"Received Exception {e}! Exiting Process {os.getpid()}")

    def __del__(self):
        self.cmd_queue.close()
        self.state_queue.close()

    def _put_result_to_queue(self, func_name, signal_name, res):
        self._internal_logger.debug(f"{func_name} finished. Emitting signal {signal_name} in control class.")
        result = cmp.CResultRecord(func_name, signal_name, res)
        self.state_queue.put(result)


    @staticmethod
    def register_for_signal(postfix='_finished', signal_name: str = None):
        _postfix = postfix.strip() if postfix is not None else None
        _signal_name = signal_name.strip() if signal_name is not None else None


        def register(func):

            def get_signature(self, *args, **kwargs):
                func_name = f"{func.__name__}->{self.pid}"

                if _signal_name is not None:
                    kwargs['signal_name'] = _signal_name

                if 'signal_name' in kwargs and kwargs['signal_name'] is not None:
                    sign = kwargs.pop('signal_name')
                elif _postfix is not None:
                    sign = f"{func.__name__}{_postfix}"
                    self._internal_logger.debug(f"Constructing signal name for function '{func.__name__}': {sign}")
                else:
                    raise ValueError(f"Cannot register function '{func_name}' for signal. No signal name provided!")
                res = func(self, *args, **kwargs)
                self._put_result_to_queue(func_name, sign, res)
                return res

            return get_signature

        return register

    @staticmethod
    def setter(sigal_same: str = None):
        def register(func):
            def get_signature(self, *args, **kwargs):
                func_name = f"{func.__name__}->{self.pid}"
                res = func(self, *args, **kwargs)
                self._internal_logger.debug(f"{func_name} finished. Emitting signal {sigal_same} in control class.")
                result = cmp.CResultRecord(func_name, sigal_same, res)
                self.state_queue.put(result)
                return res

            return get_signature

        return register