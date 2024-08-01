import logging
import sys
import time
from random import random

from PySide6.QtWidgets import QApplication
from rich.logging import RichHandler

sys.path.append('../../src')
import mpPy6


class ChildProcess(mpPy6.CProcess):

    def __init__(self, state_queue, cmd_queue, kill_flag, *args, **kwargs):
        super().__init__(state_queue, cmd_queue, kill_flag, *args, **kwargs)

        self._myProperty = "Hello World!"


    def postrun_init(self):
        # Place it here (__init__ does not fully initialize the object), thus the post-run initialization
        # is necessary
        self.set_myProperty("Hello World 2!")

    def cleanup(self):
        print("Exited ChildProcess...")

    @mpPy6.CProperty
    def myProperty(self):
        """ Returns if the laser is connected. """
        return self._myProperty

    @myProperty.setter('myProperty_changed')
    def myProperty(self, value: str):
        """ Sets the connected state of the laser. Only used internally by the process. """
        self._myProperty = value

    def set_myProperty(self, value: str):
        # random sleep to simulate a process
        time.sleep(random() * 3 + 1) # sleep for 1 to 4 seconds
        self.myProperty = value


class ChildProcessControl(mpPy6.CProcessControl):
    # Is emitted when the property myProperty in the Child is changed
    myProperty_changed = mpPy6.Signal(str, name='myProperty_changed')

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        # Register the child process
        self.register_child_process(ChildProcess)