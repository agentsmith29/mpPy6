import os
import time

import cmp


class ChildProcess3(cmp.CProcess):

    def __init__(self, state_queue, cmd_queue, enable_internal_logging):
        super().__init__(state_queue, cmd_queue, enable_internal_logging=enable_internal_logging)
        self.logger = None

    def postrun_init(self):
        self.logger, self.logger_h = self.create_new_logger(f"{self.__class__.__name__}-({os.getpid()})")

    @cmp.CProcess.register_for_signal()
    def test_call(self, a):
        self.logger.info(f"{os.getpid()} -> test_call!")
        time.sleep(1)
        return a