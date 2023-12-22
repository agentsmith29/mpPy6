# -*- coding: utf-8 -*-
"""
Author(s): Christoph Schmidt <christoph.schmidt@tugraz.at>
Created: 2023-10-19 12:35
Package Version: 
"""
import os
import sys
import time

from PySide6.QtCore import Signal

sys.path.append('./src')
import cmp


class Sceleton:

    def call_without_mp(self, a, b, c=None, **kwargs):
        raise NotImplementedError()


class ChildProc(cmp.CProcess, Sceleton):

    def __init__(self, state_queue, cmd_queue, enable_interal_logging):
        super().__init__(state_queue, cmd_queue, enable_interal_logging=enable_interal_logging)

    @cmp.CProcess.register_signal()
    def call_without_mp(self, a, b, c=None, **kwargs):
        print(f"{os.getpid()} -> call_without_mp with {a}, {b}, {c} and {kwargs}!")
        time.sleep(1)
        return c

    @cmp.CProcess.register_signal('_changed')
    def call_without_mp2(self, a, b, c=None, **kwargs):
        print(f"{os.getpid()} -> call_without_mp2 with {a}, {b}, {c} and {kwargs}!")
        time.sleep(1)
        return b, c, b+c

    #@CProccess.register_function
    def call_all(self, *args, **kwargs):
       self.call_without_mp(1, 2, c=3)
       self.call_without_mp2(4, 7, c=5)


class ChildControl(cmp.CProcessControl, Sceleton):
    call_without_mp_finished = Signal(int)
    call_without_mp2_changed = Signal(int, int, int)

    def __init__(self, parent, internal_logging):
        super().__init__(parent, internal_logging=internal_logging)
        self.register_child_process(ChildProc(self.state_queue, self.cmd_queue, enable_interal_logging=internal_logging))

    @cmp.CProcessControl.register_function()
    def call_without_mp(self, a, b, c=None):
        pass
        #print(f"{os.getpid()} -> call_without_mp with {a}, {b}, {c}!")

    @cmp.CProcessControl.register_function()
    def call_without_mp2(self, a, b, c=None, **kwargs):
      pass

    @cmp.CProcessControl.register_function()
    def call_all(self):
       pass
       #print(f"{os.getpid()} -> Executing call_all in Control Class.")
