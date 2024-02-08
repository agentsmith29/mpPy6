import logging
import logging.handlers
import multiprocessing
import os
import time
import traceback
from multiprocessing import Process, Queue

import cmp
from cmp.CBase import CBase


# This is a Queue that behaves like stdout


class CProcess(CBase, Process):

    def __init__(self, state_queue: Queue, cmd_queue: Queue,
                 kill_flag,
                 internal_log, internal_log_level, log_file=None,
                 *args, **kwargs):
        Process.__init__(self)

        self._internal_log_enabled_ = internal_log
        self._internal_log_level_ = internal_log_level
        self.logger = None
        self.logger_handler = None
        self.log_file = log_file

        self.cmd_queue = cmd_queue
        self.state_queue = state_queue
        self._kill_flag = kill_flag

    # ==================================================================================================================
    #   Process
    # ==================================================================================================================
    def postrun_init(self):
        """
            Dummy function  for initializing e.g. loggers (some handlers are not pickable)
            or pther non-pickable objects
        """
        pass

    def _typecheck(self):
        if not isinstance(self.cmd_queue, multiprocessing.queues.Queue):
            raise TypeError(f"cmd_queue must be of type {Queue}, not {type(self.cmd_queue)}")

        if not isinstance(self.state_queue, multiprocessing.queues.Queue):
            raise TypeError(f"state_queue must be of type {Queue}, not {type(self.state_queue)}")

        return True

    def run(self):
        self.name = f"{os.getpid()}({self.name})"

        self._module_logger = self.create_new_logger(f"(cmp) {self.name}",
                                                     logger_handler=logging.handlers.QueueHandler(self.state_queue),
                                                     enabled=self._internal_log_enabled_,
                                                     level=self._internal_log_level_,
                                                     propagate=True
                                                     )

        self.logger = self.create_new_logger(f"{os.getpid()}({self.__class__.__name__})",
                                             logger_handler=logging.handlers.QueueHandler(self.state_queue),
                                             enabled=True)

        self._module_logger.debug(f"Child process {self.__class__.__name__} started.")

        # sys.stderr.write = self.logger.error
        # sys.stdout.write = self.logger.info

        self.postrun_init()

        try:
            self._typecheck()
            while self._kill_flag.value:
                try:
                    cmd = self.cmd_queue.get(block=True, timeout=1)
                except:
                    continue

                if isinstance(cmd, cmp.CCommandRecord):
                    self._module_logger.debug(
                        f"Received cmd: {cmd}, args: {cmd.args}, kwargs: {cmd.kwargs}, Signal to emit: {cmd.signal_name}")
                    try:
                        cmd.execute(self)
                    except Exception as e:
                        traceback_str = ''.join(traceback.format_tb(e.__traceback__))
                        self._module_logger.error(f"Exception '{e}' occurred in {cmd}!. Traceback:\n{traceback_str}")
                    self._module_logger.debug(f"Command {cmd} finished.")
                else:
                    self._module_logger.error(f"Received unknown command {cmd}!")
            self._module_logger.error(f"Control Process exited. Terminating Process {os.getpid()}")
            if self._kill_flag.value == 0:
                self._module_logger.error(f"Process {os.getpid()} received kill signal!")
        except KeyboardInterrupt:
            self._module_logger.warning(f"Received KeyboardInterrupt! Exiting Process {os.getpid()}")
            time.sleep(1)
            self.close()
        except Exception as e:
            self._module_logger.warning(f"Received Exception {e}! Exiting Process {os.getpid()}")

        self._module_logger.warning(f"Child process monitor {self.__class__.__name__} ended.")

    def __del__(self):
        # self.logger.warning(f"Child process {self.name} deleted.")
        self.cmd_queue.close()
        self.state_queue.close()

    def _put_result_to_queue(self, func_name, signal_name, res):
        if signal_name is not None:
            self._module_logger.debug(f"{func_name} finished. Emitting signal {signal_name} in control class.")
        else:
            self._module_logger.debug(f"{func_name} finished. No signal to emit.")
        result = cmp.CResultRecord(func_name, signal_name, res)
        self.state_queue.put(result)

    def _put_exception_to_queue(self, func_name, exc):
        self._module_logger.debug(f"Error executing {func_name}.")
        tb_str = traceback.format_exception(type(exc), value=exc, tb=exc.__traceback__)
        tb_join = "".join(tb_str[-2:len(tb_str)])
        result = cmp.CException(self.name, func_name, exc, )
        result.set_additional_info(tb_join)
        self.state_queue.put(result)

    #@staticmethod
    def register_signal(postfix=None, signal_name: str = None):
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
                    self._module_logger.debug(f"Constructing signal name for function '{func.__name__}': {sign}")
                else:
                    sign = None
                try:
                    res = func(self, *args, **kwargs)
                    self._put_result_to_queue(func_name, sign, res)
                    return res
                except Exception as e:
                    self._module_logger.error(f"Error in function {func_name}: {e} ({type(e)})")
                    self._put_exception_to_queue(func.__name__, e)
                    return None

            return get_signature

        return register

    @register_signal()
    def set_internal_log_level(self, level):
        self.internal_log_level = level

    @register_signal()
    def set_internal_log_enabled(self, enabled):
        self.internal_log_enabled = enabled

    @register_signal()
    def set_child_log_level(self, level):
        self.logger.setLevel(level)

    @register_signal()
    def set_child_log_enabled(self, enabled):
        self.logger.disabled = not enabled

    @staticmethod
    def setter(signal_same: str = None):
        def register(func):
            def get_signature(self, *args, **kwargs):
                func_name = f"{func.__name__}->{self.pid}"
                res = func(self, *args, **kwargs)
                self._module_logger.debug(f"{func_name} finished. Emitting signal {signal_same} in control class.")
                result = cmp.CResultRecord(func_name, signal_same, res)
                self.state_queue.put(result)
                return res

            return get_signature

        return register
