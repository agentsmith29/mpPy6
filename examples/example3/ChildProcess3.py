import os
import time

import mpPy6
from mpPy6.CProperty import CProperty, Cache


class ChildProcess3(mpPy6.CProcess):

    def __init__(self, state_queue, cmd_queue, kill_flag,*args, **kwargs):
        super().__init__(state_queue, cmd_queue, kill_flag, *args, **kwargs)
        self.logger = None


    @mpPy6.CProcess.register_signal()
    def test_call(self, a):
        self.logger.info(f"{os.getpid()} -> test_call!")
        self.logger.debug(f"{os.getpid()} -> test_call2!")
        time.sleep(1)
       # self.test_call2 = 1
        return a

    @CProperty
    def test_call2(self, value: int):
        self.my_value = value

    @test_call2.setter(emit_to='bar')
    def test_call2(self, value: int):
        self.my_value = value

    @mpPy6.CProcess.register_signal()
    def exception_call(self, value: int):
        return value/0