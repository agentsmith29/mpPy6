import os
import time

import mpPy6


class ChildProcess2(cmp.CProcess):

    def __init__(self, state_queue, cmd_queue, kill_flag, internal_log, internal_log_level):
        super().__init__(state_queue, cmd_queue, kill_flag,
                         internal_log=internal_log,
                         internal_log_level=internal_log_level)
        self.logger = None

    def postrun_init(self):
        self.logger, self.logger_h = self.create_new_logger(f"{self.__class__.__name__}-({os.getpid()})")
    @mpPy6.CProcess.register_signal()
    def call_without_mp(self, a, b, c=None, **kwargs):
        self.logger.info(f"{os.getpid()} -> call_without_mp with {a}, {b}, {c} and {kwargs}!")
        time.sleep(1)
        return c

    @mpPy6.CProcess.register_signal('_changed')
    def call_without_mp2(self, a, b, c=None, **kwargs):
        print(f"{os.getpid()} -> call_without_mp2 with {a}, {b}, {c} and {kwargs}!")
        time.sleep(1)
        return b, c, b+c

    #@CProccess.register_function
    def call_all(self, *args, **kwargs):
       self.call_without_mp(1, 2, c=3)
       self.call_without_mp2(4, 7, c=5)
