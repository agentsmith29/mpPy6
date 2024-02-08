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
