from PySide6.QtCore import Signal, QObject

from cmp.CProperty import CProperty
from CModel import CModel


class ExampleModel4Signals(QObject):
    testfield1_changed = Signal(int)
    testfield2_changed = Signal(int)
    testfield3_changed = Signal(int)


class ExampleModel4(CModel):

    def __init__(self, c_process_control):
        super().__init__(c_process_control)
        self.signals = ExampleModel4Signals(c_process_control)

        self._testfield1 = 0
        self._testfield2 = 0
        self._testfield3 = 0


    @property

    def testfield1(self):
        return self._testfield1

    @testfield1.setter
    @CModel.wrap
    def testfield1(self, value):
        self._testfield1 = value
        print(f"testfield1: {value}")
        self.signals.testfield1_changed.emit(value)

    @property
    def testfield2(self):
        return self._testfield2

    @testfield2.setter
    def testfield2(self, value):
        self._testfield2 = value
        self.signals.testfield2_changed.emit(value)

    @property
    def testfield3(self):
        return self._testfield3

    @testfield3.setter
    def testfield3(self, value):
        self._testfield3 = value
        self.signals.testfield3_changed.emit(value)


