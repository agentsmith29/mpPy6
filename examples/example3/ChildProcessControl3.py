from PySide6.QtCore import Signal

import cmp
from ChildProcess3 import ChildProcess3


class ChildProcessControl3(cmp.CProcessControl):
    mp_finished = Signal(int, name='mp_finished')

    def __init__(self, parent, enable_internal_logging):
        super().__init__(parent, enable_internal_logging=enable_internal_logging)
        self.register_child_process(ChildProcess3(
            self.state_queue,
            self.cmd_queue,
            enable_internal_logging=enable_internal_logging))

    @cmp.CProcessControl.register_function(signal=mp_finished)
    def test_call(self, a):
        pass
        #print(f"{os.getpid()} -> call_without_mp with {a}, {b}, {c}!")

