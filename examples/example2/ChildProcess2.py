import os
import time

import cmp


class ChildProcess2(cmp.CProcess):

    def __init__(self, state_queue, cmd_queue, enable_interal_logging):
        super().__init__(state_queue, cmd_queue, enable_interal_logging=enable_interal_logging)
        self.logger = None

    def postrun_init(self):
        self.logger, self.logger_h = self.create_new_logger(f"{self.__class__.__name__}-({os.getpid()})")
    @cmp.CProcess.register_for_signal()
    def call_without_mp(self, a, b, c=None, **kwargs):
        self.logger.info(f"{os.getpid()} -> call_without_mp with {a}, {b}, {c} and {kwargs}!")
        time.sleep(1)
        return c

    @cmp.CProcess.register_for_signal('_changed')
    def call_without_mp2(self, a, b, c=None, **kwargs):
        print(f"{os.getpid()} -> call_without_mp2 with {a}, {b}, {c} and {kwargs}!")
        time.sleep(1)
        return b, c, b+c

    #@CProccess.register_function
    def call_all(self, *args, **kwargs):
       self.call_without_mp(1, 2, c=3)
       self.call_without_mp2(4, 7, c=5)
