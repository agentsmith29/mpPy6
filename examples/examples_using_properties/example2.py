import logging
import sys
import os

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QDialog, QApplication, QPushButton, QMessageBox, QVBoxLayout
from rich.logging import RichHandler

# Get the path to the current file
file_path, _ = os.path.split(os.path.realpath(__file__))
src_path = f"{file_path}/../../src"
print("src_path:", src_path)
sys.path.append(src_path)

from mp_process import ChildProcessControl


class Form(QDialog):
    on_text_converted = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        child_con = ChildProcessControl(self)
        child_con.internal_log_enabled = True
        child_con.internal_log_level = logging.INFO

        self.btn_start = QPushButton("Start")

        # add the button to the layout
        layout = QVBoxLayout()
        layout.addWidget(self.btn_start)
        self.setLayout(layout)

        # Connect the signal to the slot
        child_con.myProperty_changed.connect(self.two_numbers_added)

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

    # Print the Python version and the file name
    print(f"Executing {__file__} with Python {sys.version}")
    try:
        app = QApplication(sys.argv)
        form = Form()
        form.show()
        app.exec()
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
        sys.exit(0)  # print(f"{os.getpid()} -> call_without_mp with {a}, {b}, {c}!")
