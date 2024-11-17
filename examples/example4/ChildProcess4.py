import os
import time

import sys
sys.path.append('../../src')
import mpPy6 as cmp

from mpPy6.CProperty import CProperty, Cache
from ExampleModel4 import ExampleModel4


class ChildProcess4(cmp.CProcess):

    def __init__(self, state_queue, cmd_queue, kill_flag,*args, **kwargs):
        super().__init__(state_queue, cmd_queue, kill_flag, *args, **kwargs)
        self.logger = None


    def postrun_init(self):
    #    self.model = ExampleModel4(self)
        pass


