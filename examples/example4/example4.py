# -*- coding: utf-8 -*-
"""
Author(s): Christoph Schmidt <christoph.schmidt@tugraz.at>
Created: 2023-10-19 12:35
Package Version:
"""
import logging
import signal
import sys
from multiprocessing import Process, Queue, Pipe
from threading import Thread

from PySide6.QtCore import QObject, Signal, SIGNAL
from PySide6.QtWidgets import QDialog, QApplication, QTextBrowser, QLineEdit, QVBoxLayout, QMainWindow, QMessageBox



sys.path.append('./src')
from ChildProcessControl4 import ChildProcessControl4
from ExampleModel4 import ExampleModel4

class Form(QDialog):
    on_text_converted = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)



        child_con = ChildProcessControl4(self, internal_log=True, internal_log_level=logging.DEBUG)
        self.model = ExampleModel4(child_con)

        #self.model.signals.testfield1_changed.connect(child_con.child.test_call)

        self.model.testfield1 = 123

        child_con.mp_finished.connect(self.updateUI)

        self.browser = QTextBrowser()
        self.lineedit = QLineEdit('Type text and press <Enter>')
        self.lineedit.selectAll()
        layout = QVBoxLayout()
        layout.addWidget(self.browser)
        layout.addWidget(self.lineedit)
        self.setLayout(layout)
        self.lineedit.setFocus()
        self.setWindowTitle('Upper')
        # self.lineedit.returnPressed.connect(lambda: child_con.call_without_mp(1, 2, c=3))
        self.lineedit.returnPressed.connect(lambda: child_con.set_testfield1(1))

    def updateUI(self, text):
        print("updateUI: ", text)
        self.browser.append("->" + str(text))

    def closeEvent(self, arg__1):
        self.destroyed.emit()
        #print("Form destroyed.")


if __name__ == '__main__':

    try:
        app = QApplication(sys.argv)
        form = Form()
        form.show()
        app.exec()
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
        sys.exit(0)


#if __name__ == '__main__':

    #model = ExampleModel4()
    #model.testfield1 = 123
