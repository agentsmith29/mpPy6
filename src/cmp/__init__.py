import logging
import os
import sys

from rich.logging import RichHandler

from .CCommandRecord import CCommandRecord
from .CResultRecord import CResultRecord

from .CProcess import CProcess
from .CProcessControl import CProcessControl

sys.path.append(os.path.join(os.path.dirname(__file__), '../'))
