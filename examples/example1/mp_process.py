import sys

from PySide6.QtCore import Signal

import cmp



class ChildProcess(cmp.CProcess):

    def __init__(self, state_queue, cmd_queue, kill_flag, *args, **kwargs):
        super().__init__(state_queue, cmd_queue, kill_flag, *args, **kwargs)

    # The signal (add_two_finished) name mus correspond to the signal in the control class "ChildProcessControl"
    # in order to get executed.
    # The function (add_two) and function's signature name must correspond to the function in the control class
    @cmp.CProcess.register_signal(signal_name='add_two_finished')
    def add_two(self, num1: int, num2: int):
        # "return" automatically sends the result to the control class and triggers the signal with the
        # name "add_two_finished"
        return num1 + num2



class ChildProcessControl(cmp.CProcessControl):
    add_two_finished = Signal(int, name='test_call_finished')

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        # Register the child process
        self.register_child_process(ChildProcess)

    # Create a body for your function. This does not necessarily have to include code, you can just print a message
    # or add "pass", a comment, or a docstring.
    @cmp.CProcessControl.register_function()
    def add_two(self, num1: int, num2: int):
        print("I will add two numbers in a separate process")
