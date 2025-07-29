"""Model for chips widget"""

from abc import abstractmethod, ABC

from PyQt6.QtCore import QObject
from PyQt6.QtWidgets import QWidget


class IChipButton(QWidget):
    """ChipButton model"""

    def __init__(self, parent: QObject = None) -> None:
        super().__init__(parent)
