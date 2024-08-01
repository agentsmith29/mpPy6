import logging
import sys
import time

from PySide6.QtWidgets import QApplication
from rich.logging import RichHandler

sys.path.append('../../src')
import mpPy6


class ChildProcess(mpPy6.CProcess):

    def __init__(self, state_queue, cmd_queue, kill_flag, *args, **kwargs):
        super().__init__(state_queue, cmd_queue, kill_flag, *args, **kwargs)

    # The signal (add_two_finished) name mus correspond to the signal in the control class "ChildProcessControl"
    # in order to get executed.
    # The function (add_two) and function's signature name must correspond to the function in the control class
    @mpPy6.CProcess.register_signal(signal_name='add_two_finished')
    def add_two(self, num1: int, num2: int):
        # "return" automatically sends the result to the control class and triggers the signal with the
        # name "add_two_finished"
        return num1 + num2


class ChildProcessControl(mpPy6.CProcessControl):
    add_two_finished = mpPy6.Signal(int, name='add_two_finished')

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        # Register the child process
        self.register_child_process(ChildProcess)

    # Create a body for your function. This does not necessarily have to include code, you can just print a message
    # or add "pass", a comment, or a docstring.
    @mpPy6.CProcessControl.register_function()
    def add_two(self, num1: int, num2: int):
        print("I will add two numbers in a separate process")


if __name__ == '__main__':
    # Set up logging
    FORMAT = "%(name)s %(message)s"
    logging.basicConfig(
        level=logging.DEBUG, format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
    )

    app = QApplication(sys.argv)

    child_con = ChildProcessControl(None)
    child_con.internal_log_enabled = True
    child_con.internal_log_level = logging.DEBUG

    def printres(res):
        print(f"->>>> {res}")
    child_con.add_two_finished.connect(printres)
    time.sleep(1)
    child_con.add_two(1, 2)

    app.exec()