from PySide6.QtCore import Signal

import cmp
from ChildProcess3 import ChildProcess3


class ChildProcessControl3(cmp.CProcessControl):
    mp_finished = Signal(int, name='mp_finished')
    mp_finished_untriggered = Signal(int)

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.register_child_process(ChildProcess3)

    @cmp.CProcessControl.register_function()
    def test_call(self, a):
        print(a)
        #print(f"{os.getpid()} -> call_without_mp with {a}, {b}, {c}!")

    @cmp.CProcessControl.register_function()
    def exception_call(self, a):
       pass
