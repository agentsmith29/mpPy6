import logging
import logging.handlers
import os
import signal
import time
from multiprocessing import Queue, Process, Value

from PySide6.QtCore import QObject, QThreadPool
from PySide6.QtGui import QWindow
from PySide6.QtWidgets import QWidget
from rich.logging import RichHandler

import cmp


class CProcessControl(QObject):

    def __init__(self, kill_child_process_flag: Value,
                 parent: QObject = None,
                 signal_class: QObject = None,
                 enable_internal_logging: bool = False):
        super().__init__(parent)
        self._kill_child_process_flag = kill_child_process_flag
        self._enable_internal_logging = enable_internal_logging

        if parent is not None:
            parent.destroyed.connect(self.safe_exit)

        # Register this class as signal class (all signals will be implemented and emitted from this class)
        if signal_class is not None:
            self.register_signal_class(signal_class)
        else:
            self.register_signal_class(self)


        # The child process
        self._child: Process = None
        # Queues for data exchange
        self.cmd_queue = Queue()
        self.state_queue = Queue()

        # Thread manager for monitoring the state queue
        self.thread_manager = QThreadPool()

        # The child process pid
        self._child_process_pid = None
        self._child_kill_flag = Value('i', 1)

        self._internal_logger, self._il_handler = self.create_new_logger(f"{self.__class__.__name__}-Int({os.getpid()})")
        self.logger, self.logger_handler = self.create_new_logger(f"{self.__class__.__name__}({os.getpid()})")
        self.enable_internal_logging(enable_internal_logging)

    def create_new_logger(self, name: str) -> (logging.Logger, logging.Handler):
        qh = RichHandler(rich_tracebacks=True)
        _internal_logger = logging.getLogger(name)
        _internal_logger.handlers = [qh]
        _internal_logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(name)s %(message)s')
        qh.setFormatter(formatter)
        return _internal_logger, qh

    def enable_internal_logging(self, enable: bool):
        self._enable_internal_logging = enable
        if self._internal_logger is not None:
            self._internal_logger.disabled = not enable

    def register_signal_class(self, signal_class: QObject):
        self._signal_class = signal_class

    @property
    def child_process_pid(self):
        return self._child_process_pid

    def register_child_process(self, child: cmp.CProcess):
        self._child = child
        self._child.register_kill_flag(self._child_kill_flag)
        self._child_process_pid = child.pid
        self._child.enable_internal_logging(self._enable_internal_logging)
        self._child.start()
        self.thread_manager.start(self._monitor_result_state)

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
                        self._internal_logger.debug(f"Emitted {res} in {self._signal_class.__class__.__name__}.")
                    except Exception as e:
                        self._internal_logger.error(f"Error while emitting {res} in {self.__class__.__name__}: {e}")
        except:
            print(f"Error in monitor thread")
            time.sleep(1)

        self._internal_logger.info("Ended monitor thread.")
        self.state_queue.close()
        self.cmd_queue.close()

    @staticmethod
    def register_function(signal_name: str = None):
        def register(func):
            def get_signature(self: CProcessControl, *args, **kwargs):
                arguments = locals().copy()
                arguments.pop("func")

                args = arguments.pop("args")
                kwargs = arguments.pop("kwargs")
                name = getattr(func, '__name__', 'unknown')
                cmd = cmp.CCommandRecord(name, *args, **kwargs)
                func(self, *args, **kwargs)
                self.cmd_queue.put(cmd)
            return get_signature
        return register
    def safe_exit(self):
        self._internal_logger.warning(f"Shutting down ProcessControl {os.getpid()}")
        self._child_kill_flag.value = 0

    def __del__(self):
        self._internal_logger.warning(f"Closing ProcessControl {self.__class__.__name__} with pid {os.getpid()}")
