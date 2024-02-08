# pycmp: Python Module for Multiprocess Communication with PySide6 UIs

CMP (Communication Multiprocess Python module) is a Python module designed to facilitate communication between multiple processes while utilizing PySide for graphical user interfaces (GUIs). This module aims to provide a seamless solution for building applications with parallel processing capabilities and interactive UI components.
Features

* Multiprocess Communication: CMP enables efficient communication between multiple Python processes, allowing for concurrent execution of tasks.

* PySide Integration: CMP seamlessly integrates with PySide, a Python binding for the Qt framework, to create interactive and visually appealing user interfaces.

* Event Handling: CMP provides robust event handling mechanisms, allowing processes to communicate and synchronize events effectively.

# Installation

You can install CMP using pip:
```bash
pip install git+https://github.com/agentsmith29/fstools.cmp.git@main
```

# Usage

Here's a simple example demonstrating how to use CMP:

```python
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
```
Use your control class in your main application
```python
import logging
import sys

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QDialog, QApplication, QPushButton, QMessageBox, QVBoxLayout
from rich.logging import RichHandler

sys.path.append('./src')
from mp_process import ChildProcessControl


class Form(QDialog):
    on_text_converted = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        child_con = ChildProcessControl(self)
        child_con.internal_log_enabled = True
        child_con.internal_log_level = logging.INFO

        self.btn_start = QPushButton("Start")
        self.btn_start.clicked.connect(lambda: child_con.add_two(1, 2))
        # add the button to the layout
        layout = QVBoxLayout()
        layout.addWidget(self.btn_start)
        self.setLayout(layout)

        # Connect the signal to the slot
        child_con.add_two_finished.connect(self.two_numbers_added)

    def two_numbers_added(self, result):
        # Message box
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(f"The result is {result}")
        msg.setWindowTitle("Result")
        msg.exec()

    def closeEvent(self, arg__1):
        self.destroyed.emit()


if __name__ == '__main__':
    # Set up logging
    FORMAT = "%(name)s %(message)s"
    logging.basicConfig(
        level=logging.DEBUG, format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
    )

    try:
        app = QApplication(sys.argv)
        form = Form()
        form.show()
        app.exec()
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
        sys.exit(0)  # print(f"{os.getpid()} -> call_without_mp with {a}, {b}, {c}!")
```

In this example, when the button is clicked, CMP emits the "button_clicked" event, which triggers the process_function to be executed in a separate process.
Contributing

We welcome contributions from the community! If you encounter any issues or have suggestions for improvements, please feel free to open an issue or submit a pull request on the GitHub repository.

# License

This project is licensed under the GNU GENERAL PUBLIC LICENSE Version 3.0. See the LICENSE file for details.
