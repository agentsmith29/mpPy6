import functools

import cmp
from cmp import CProcess, CProcessControl


class CModel:

    def __init__(self, cprocess_control: CProcessControl):
        self.cprocess_control: CProcessControl = cprocess_control

    @staticmethod
    def wrap(fun):
        """ Decoraetor for wrapping a property""
        """
        @functools.wraps(fun)
        def wrapper(self, *args, **kwargs):
            print(f"Calling {fun.__name__}!")
            cmd = cmp.CCommandRecord("self._child.name", fun.__name__, *args, **kwargs)
            print(cmd)
            #self.cprocess_control.cmd_queue.put(cmd)
            return fun(self, *args, **kwargs)
        return wrapper
