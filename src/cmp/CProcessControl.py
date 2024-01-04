import inspect
import logging
import logging.handlers
import os
import re
import signal
import time
import traceback
from multiprocessing import Queue, Process, Value
from typing import Type

from PySide6.QtCore import QObject, QThreadPool, Signal
from PySide6.QtGui import QWindow
from PySide6.QtWidgets import QWidget, QMessageBox
from rich.logging import RichHandler

import cmp
from cmp import CException
from cmp.CBase import CBase


class CProcessControl(CBase, QObject):
    on_exception_raised = Signal(object, name='on_exception_raised')

    def __init__(self, parent: QObject = None,
                 signal_class: QObject = None,
                 internal_log: bool = True, internal_log_level: int = logging.WARNING, log_file: str = None):
        QObject.__init__(self, parent)
        CBase.__init__(self)

        self.log_file = log_file
        self._internal_logger = self.create_new_logger(f"(cmp) {self.name}",
                                                       to_file=self.log_file, enabled=internal_log, level=internal_log_level)

        self.logger = self.create_new_logger(f"{self.__class__.__name__}({os.getpid()})",
                                             to_file=self.log_file, enabled=internal_log)

        if isinstance(parent, QWidget) or isinstance(parent, QWindow):
            parent.destroyed.connect(lambda: self.safe_exit(reason="Parent destroyed."))

        # Register this class as signal class (all signals will be implemented in and emitted from this class)
        if signal_class is not None:
            self.register_signal_class(signal_class)
        else:
            self.register_signal_class(self)

        # The child process
        self._child: cmp.CProcess = None

        # Queues for data exchange
        self.cmd_queue = Queue()
        self.state_queue = Queue()

        # Thread manager for monitoring the state queue
        self.thread_manager = QThreadPool()

        # The child process pid
        self._pid = os.getpid()
        self._child_process_pid = None

        self.name = f"{self._pid}({self.__class__.__name__})"

        self._child_kill_flag = Value('i', 1)


        self.on_exception_raised.connect(self.display_exception)
        self.msg_box = QMessageBox()

    # ==================================================================================================================
    #
    # ==================================================================================================================
    def register_signal_class(self, signal_class: QObject):
        self._signal_class = signal_class

    @property
    def child_process_pid(self):
        return self._child_process_pid

    def register_child_process(self, child, *args, **kwargs):
        self._internal_logger.debug(f"Registering child process.")

        self._child = child(self.state_queue, self.cmd_queue,
                            kill_flag=self._child_kill_flag,
                            internal_log=self.internal_log_enabled,
                            internal_log_level=self.internal_log_level,
                            log_file=self.log_file,
                            *args, **kwargs)
        # self._child.register_kill_flag(self._child_kill_flag)
        self._child_process_pid = child.pid
        self._child.start()
        self._internal_logger.info(f"Child process {self._child.name} created.")
        self.thread_manager.start(self._monitor_result_state)

    @property
    def child(self):
        return self._child

    def _monitor_result_state(self):
        self._internal_logger.info("Starting monitor thread.")
        try:
            while self._child.is_alive():
                try:
                    res = self.state_queue.get(block=True, timeout=1)
                except:
                    continue

                if isinstance(res, logging.LogRecord):
                    try:
                        self.logger.handle(res)
                    except Exception as e:
                        self.logger.warning(f"Error cannot handle log record: {e}")
                elif isinstance(res, cmp.CResultRecord):
                    try:
                        res.emit_signal(self._signal_class)
                    except Exception as e:
                        self._internal_logger.error(f"Error while emitting {res} in {self.__class__.__name__}: {e}")
                elif isinstance(res, cmp.CException):
                    self._internal_logger.error(f"Received exception: {res}")
                    try:
                        self.on_exception_raised.emit(res)
                    except Exception as e:
                        self._internal_logger.error(f"Error while emitting exception: {e}")
                else:
                    self._internal_logger.error(f"Received unknown result {res}!")

        except:
            self._internal_logger.error(f"Error in monitor thread")
            time.sleep(1)

        self._internal_logger.info(f"Ended monitor thread. Child process alive: {self._child.is_alive()}")
        self.state_queue.close()
        self.cmd_queue.close()

    def display_exception(self, e: cmp.CException):
        # Create a message box
        try:
            self.msg_box = QMessageBox()
            self.msg_box.setIcon(QMessageBox.Critical)
            self.msg_box.setText(f"Error executing {e.function_name} in {e.parent_name}")
            self.msg_box.setInformativeText(f"Error: {e.exception}")
            self.msg_box.setWindowTitle("Error")
            self.msg_box.setDetailedText(e.traceback_short())
            self.msg_box.setStandardButtons(QMessageBox.Ok)
            self.msg_box.show()
            self.logger.error(f"Error executing {e.function_name} in {e.parent_name}: {e.exception}\n"
                              f"{e.traceback()}")
        except Exception as e:
            self._internal_logger.error(f"Error while displaying exception: {e}")

    def execute_function(self, func: callable, signal: Signal = None):
        self.register_function(signal)(func)(self)

    @staticmethod
    def register_function(signal: Signal = None):
        """
        Decorator for registering functions in the command queue.
        This automatically puts the command into the queue and executes the function.
        If a signal_name is specified, the given Signal name will be emitted after the function has been executed.
        :param signal:
        :return:
        """

        def register(func):
            def match_signal_name(_signal: Signal):
                pattern = re.compile(r'(\w+)\(([^)]*)\)')
                match = pattern.match(str(_signal))
                name = match.group(1).strip()
                args = match.group(2).split(',')
                return name, args

            def get_signature(self, *args, **kwargs):

                arguments = locals().copy()
                arguments.pop("func")

                name = getattr(func, '__name__', 'unknown')
                args = arguments.pop("args")
                kwargs = arguments.pop("kwargs")

                cmd = cmp.CCommandRecord(self._child.name, name, *args, **kwargs)
                if signal is not None:
                    sig_name, sig_args = match_signal_name(signal)
                    cmd.register_signal(sig_name)
                    self._internal_logger.debug(f"New function registered: {cmd} -> "
                                                f"{cmd.signal_name if cmd.signal_name is not None else 'None'}("
                                                f"{', '.join(str(a) for a in sig_args) if sig_args is not None else 'None'})")
                else:
                    self._internal_logger.debug(f"New function registered: {cmd}")

                try:
                    self._internal_logger.debug(f"Executing {name} with args {args} and kwargs {kwargs}")
                    func(self, *args, **kwargs)
                except Exception as e:
                    self._internal_logger.error(f"Error while executing {cmd}: {e}")
                    raise e

                try:
                    self.cmd_queue.put(cmd)
                    self._internal_logger.debug(f"{cmd} put into cmd_queue.")
                except Exception as e:
                    self._internal_logger.error(f"Error while putting {cmd} into cmd_queue: {e}")
                    raise e

            return get_signature

        return register

    @register_function()
    def set_internal_log_level(self, level):
        self.internal_log_level = level

    @register_function()
    def set_internal_log_enabled(self, enabled):
        self.internal_log_enabled = enabled

    @register_function()
    def set_child_log_level(self, level):
        """
        Sets the regular logging level of the child process.
        :param level:
        :return:
        """

    @register_function()
    def set_child_log_enabled(self, enabled):
        """
        Enables or disables logging of the child process.
        :param enabled:
        :return:
        """

    def safe_exit(self, reason: str = ""):
        self._internal_logger.warning(f"Shutting down ProcessControl {os.getpid()}. Reason: {reason}")
        self._child_kill_flag.value = 0

    def __del__(self):
        self._internal_logger.warning(f"Closing ProcessControl {self.__class__.__name__} with pid {os.getpid()}")
