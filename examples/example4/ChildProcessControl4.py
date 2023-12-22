from PySide6.QtCore import Signal

import cmp
from ChildProcess4 import ChildProcess4
from ExampleModel4 import ExampleModel4


class ChildProcessControl4(cmp.CProcessControl):
    mp_finished = Signal(int, name='mp_finished')
    mp_finished_untriggered = Signal(int)
    test_call1_finished = Signal(int, name='test_call1_finished')

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.register_child_process(ChildProcess4)


    @cmp.CProcessControl.register_function(signal=mp_finished)
    def set_testfield1(self, a):
        pass
        #c: ChildProcess3 = self._child
        #.execute_function(lambda a: c.test_call1(a), signal=ChildProcessControl4.test_call1_finished)
        #print(a)
        #print(f"{os.getpid()} -> call_without_mp with {a}, {b}, {c}!")

