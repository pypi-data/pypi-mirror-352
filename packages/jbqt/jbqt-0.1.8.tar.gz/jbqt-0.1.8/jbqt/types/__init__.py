from collections.abc import Callable
from typing import Optional

from PyQt6.QtCore import QSize
from PyQt6.QtGui import QIcon


IconGetter = Callable[[str, QSize | int | None], QIcon]
