from PySide6.QtCore import Signal

import cmp
from ChildProcess3 import ChildProcess3


class ChildProcessControl3(cmp.CProcessControl):
    mp_finished = Signal(int, name='mp_finished')
    mp_finished_untriggered = Signal(int)

    def __init__(self, parent, internal_logging, internal_logging_level):
        super().__init__(parent,
                         internal_logging=internal_logging,
                         internal_logging_level=internal_logging_level)
        self.register_child_process(ChildProcess3)

    @cmp.CProcessControl.register_function(signal=mp_finished)
    def test_call(self, a):
        pass
        #print(f"{os.getpid()} -> call_without_mp with {a}, {b}, {c}!")

