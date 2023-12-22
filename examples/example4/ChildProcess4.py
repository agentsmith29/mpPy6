import os
import time

import cmp
from cmp.CProperty import CProperty, Cache
from ExampleModel4 import ExampleModel4


class ChildProcess4(cmp.CProcess):

    def __init__(self, state_queue, cmd_queue, kill_flag,*args, **kwargs):
        super().__init__(state_queue, cmd_queue, kill_flag, *args, **kwargs)
        self.logger = None


    def postrun_init(self):
    #    self.model = ExampleModel4(self)
        pass


