import logging.handlers
import logging
import os
import time
import traceback
from multiprocessing import Process, Queue, Value

import cmp


class CProcess(Process):

    def __init__(self, state_queue: Queue, cmd_queue: Queue, enable_internal_logging=True):
        Process.__init__(self)

        self._enable_internal_logging = enable_internal_logging
        self.logger = None
        self.logger_handler = None

        self._internal_logger = None
        self._il_handler = None

        self.cmd_queue = cmd_queue
        self.state_queue = state_queue
        self._kill_flag = Value('i', 1)

    def register_kill_flag(self, kill_flag: Value):
        self._kill_flag = kill_flag

    def create_new_logger(self, name: str) -> (logging.Logger, logging.Handler):
        _handler = logging.handlers.QueueHandler(self.state_queue)
        _logger = logging.getLogger(name)
        _logger.handlers.clear()
        _logger.handlers = [_handler]
        _logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(message)s')
        _handler.setFormatter(formatter)
        return _logger, _handler

    def enable_internal_logging(self, enable: bool):
        self._enable_internal_logging = enable
        if self._internal_logger is not None and enable is False:
            self._internal_logger.disabled = True
            #self._internal_logger.handlers = []
        elif self._internal_logger is not None and enable is True:
            self._internal_logger.disabled = False
            #self._internal_logger.handlers = [self._il_handler]

    def postrun_init(self):
        """
            Dummy function  for initializing e.g. loggers (some handlers are not pickable)
            or pther non-pickable objects
        """
        pass

    def run(self):
        self.name = f"{self.name}/{os.getpid()}"
        self.postrun_init()

        self._internal_logger, self._il_handler = self.create_new_logger(f"{self.__class__.__name__}-Int({os.getpid()})")
        self.logger, self.logger_handler = self.create_new_logger(f"{self.__class__.__name__}({os.getpid()})")
        self.enable_internal_logging(self._enable_internal_logging)
        try:
            while self._kill_flag.value:
                try:
                    cmd = self.cmd_queue.get(block=True, timeout=1)
                except:
                    continue
                if isinstance(cmd, cmp.CCommandRecord):
                    self._internal_logger.info(f"Received cmd: {cmd}")
                    # print(f"Received cmd with args: {cmd_with_args}")
                    # cmd = cmd_with_args['func']
                    # args = cmd_with_args['args']
                    # kwargs = cmd_with_args['kwargs']
                    # if 'sig_name' is not None:
                    #    #sig_name = cmd_with_args['sig_name']
                    self._internal_logger.debug(
                        f"cmd: {cmd}, args: {cmd.args}, kwargs: {cmd.kwargs}, sig_name: {cmd.signal_name}")
                    try:
                        cmd.execute(self)
                    except Exception as e:
                        traceback_str = ''.join(traceback.format_tb(e.__traceback__))
                        self._internal_logger.error(f"Exception '{e}' occurred in {cmd}!. Traceback:\n{traceback_str}")
                    # else:
                    #    self._internal_logger.debug(f"cmd: {cmd}, args: {cmd.args}, kwargs: {cmd.kwargs}")
                    #    self._internal_logger.info(f"Executing {cmd} in Process Class.\n")
                    #    getattr(self, cmd.func_name)(*cmd.args, **cmd.kwargs)
            self._internal_logger.error(f"Control Process exited. Terminating Process {os.getpid()}")

        except KeyboardInterrupt:
            self._internal_logger.warning(f"Received KeyboardInterrupt! Exiting Process {os.getpid()}")
            time.sleep(1)
            self.close()
        except Exception as e:
            self._internal_logger.warning(f"Received Exception {e}! Exiting Process {os.getpid()}")

    def __del__(self):
        # if self._internal_logger is not None:
        #    self._internal_logger.warning(f"Exiting Process")
        self.cmd_queue.close()
        self.state_queue.close()

    @staticmethod
    def register_for_signal(postfix='_finished'):
        def register(func):
            def get_signature(self, *args, **kwargs):
                res = func(self, *args, **kwargs)

                # arguments = locals().copy()
                # print(f"arguments: {arguments}")
                # if 'sig_name' in arguments:
                if 'sig_name' in kwargs and kwargs['sig_name'] is None:
                    sign = kwargs['sig_name']
                else:
                    sign = f"{func.__name__}{postfix}"
                result = cmp.CResultRecord(sign, res)
                self.state_queue.put(result)
                return res

            return get_signature

        return register
