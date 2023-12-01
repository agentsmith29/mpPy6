# -*- coding: utf-8 -*-
"""
Author(s): Christoph Schmidt <christoph.schmidt@tugraz.at>
Created: 2023-10-19 12:35
Package Version: 
"""
import signal
import sys
from multiprocessing import Process, Queue, Pipe
from threading import Thread

from PySide6.QtCore import QObject, Signal, SIGNAL
from PySide6.QtWidgets import QDialog, QApplication, QTextBrowser, QLineEdit, QVBoxLayout, QMainWindow, QMessageBox

from mp_process import ChildProc, ChildControl


class Form(QDialog):

    on_text_converted = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        child_con = ChildControl(self, enable_internal_logging=True)

        child_con.call_without_mp_finished.connect(self.updateUI)
        child_con.call_without_mp2_changed.connect(self.updateUI2)


        self.browser = QTextBrowser()
        self.lineedit = QLineEdit('Type text and press <Enter>')
        self.lineedit.selectAll()
        layout = QVBoxLayout()
        layout.addWidget(self.browser)
        layout.addWidget(self.lineedit)
        self.setLayout(layout)
        self.lineedit.setFocus()
        self.setWindowTitle('Upper')
        #self.lineedit.returnPressed.connect(lambda: child_con.call_without_mp(1, 2, c=3))
        self.lineedit.returnPressed.connect(lambda: child_con.call_all())

        #self.emitter.register(self.on_text_converted, self.updateUI)

    def test(self):
        #Signal(str)
        self.data_to_child.put(self.to_child.__name__)
        #self.lineedit.clear()


    def updateUI(self, text):
        print("updateUI: ", text)
        self.browser.append(str(text))

    def updateUI2(self, text, text2, text3):
        print("updateUI2: ", text)
        self.browser.append("->" + str(text) + "+" + str(text2) + "=" + str(text3))

    def closeEvent(self, event):
        print("closeEvent")
        #try:
        self.destroyed.emit()
        #except KeyboardInterrupt:
        #    print("KeyboardInterrupt")
        #event.ignore()



if __name__ == '__main__':

    try:
        app = QApplication(sys.argv)
        form = Form()
        form.show()
        app.exec()
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
        sys.exit(0)

