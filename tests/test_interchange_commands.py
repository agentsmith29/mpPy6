import os
import time

from PySide6.QtCore import Signal

import cmp

import unittest


class ChildProcessCustomSignals(cmp.CProcess):

    def __init__(self, state_queue, cmd_queue, enable_internal_logging):
        super().__init__(state_queue, cmd_queue, enable_internal_logging=enable_internal_logging)
        self.logger = None

    def postrun_init(self):
        self.logger, self.logger_h = self.create_new_logger(f"{self.__class__.__name__}-({os.getpid()})")

    @cmp.CProcess.register_for_signal()
    def call_without_mp(self, a, b, c=None, **kwargs):
        self.logger.info(f"{os.getpid()} -> call_without_mp with {a}, {b}, {c} and {kwargs}!")
        time.sleep(1)
        return c


class ChildProcessControlCustomSignals(cmp.CProcessControl):
    testSignals = Signal(int)

    # call_without_mp2_changed = Signal(int, int, int)

    def __init__(self, parent, signal_class, enable_internal_logging):
        super().__init__(parent, signal_class, enable_internal_logging=enable_internal_logging)
        self.register_child_process(ChildProcessCustomSignals(self.state_queue, self.cmd_queue,
                                                              enable_internal_logging=enable_internal_logging))

    @cmp.CProcessControl.register_function()
    def call_without_mp(self, a, b, c=None):
        pass


class TestInterchangeCommands(unittest.TestCase):


    def test_custom_signals(self):
        process_control = ChildProcessControlCustomSignals()



if __name__ == '__main__':
    unittest.main()
