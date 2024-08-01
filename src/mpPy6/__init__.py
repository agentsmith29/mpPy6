import os
import sys

from .CCommandRecord import CCommandRecord
from .CException import CException
from .CProcess import CProcess
from .CProcessControl import CProcessControl
from .CResultRecord import CResultRecord

from .CProperty import CProperty

from PySide6.QtCore import Signal

sys.path.append(os.path.join(os.path.dirname(__file__), '../'))
