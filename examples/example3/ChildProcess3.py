import os
import time

import cmp
from cmp.CProperty import CProperty, Cache


class ChildProcess3(cmp.CProcess):

    def __init__(self, state_queue, cmd_queue, kill_flag, internal_logging, internal_log_level):
        super().__init__(state_queue, cmd_queue, kill_flag,
                         internal_logging=internal_logging,
                         internal_log_level=internal_log_level)
        self.logger = None

    def postrun_init(self):
        self.logger, self.logger_h = self.create_new_logger(f"{self.__class__.__name__}-({os.getpid()})")

    @cmp.CProcess.register_for_signal()
    def test_call(self, a):
        self.logger.info(f"{os.getpid()} -> test_call!")
        time.sleep(1)
        self.test_call2 = 1
        return a

    @CProperty
    def test_call2(self, value: int):
        self.my_value = value

    @test_call2.setter(emit_to='bar')
    def test_call2(self, value: int):
        self.my_value = value
