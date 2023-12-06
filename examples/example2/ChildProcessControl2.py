from PySide6.QtCore import Signal

import cmp
from ChildProcess2 import ChildProcess2


class ChildProcessControl2(cmp.CProcessControl):
    call_without_mp_finished = Signal(int)
    #call_without_mp2_changed = Signal(int, int, int)

    def __init__(self, parent, signal_class, internal_logging, internal_logging_level):
        super().__init__(parent, signal_class,
                         internal_logging=internal_logging, internal_logging_level=internal_logging_level)
        self.register_child_process(ChildProcess2)

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
