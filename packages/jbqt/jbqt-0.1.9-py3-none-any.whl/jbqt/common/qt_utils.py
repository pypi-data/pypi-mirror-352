from datetime import date
from typing import Any

from PyQt6.QtCore import Qt, QDate
from PyQt6.QtWidgets import (
    QListWidgetItem,
    QCalendarWidget,
    QApplication,
    QWidget,
    QLineEdit,
    QTextEdit,
    QSpinBox,
    QCheckBox,
    QDoubleSpinBox,
)

from jbqt.common import consts
from jbqt.models import IChipsWidget


def get_item_value(item: QListWidgetItem) -> str:
    value = item.data(consts.LIST_ITEM_ROLE) or item.text()
    return value.strip()


def register_app(app: QApplication, icon_dir: str = "") -> None:
    consts.GlobalRefs.app = app
    consts.set_icon_dir(icon_dir)


def get_widget_value(widget: QWidget, key: str = "") -> Any:

    if isinstance(widget, QLineEdit):
        return widget.text()
    if isinstance(widget, QTextEdit):
        return widget.toPlainText().strip()
    if isinstance(widget, (QSpinBox, QDoubleSpinBox)):
        return widget.value()
    if isinstance(widget, IChipsWidget):
        return widget.values
    if isinstance(widget, QCheckBox):
        return widget.checkState == Qt.CheckState.Checked
    if isinstance(widget, QCalendarWidget):
        return widget.selectedDate().toString()

    print(f"No handler defined for {key} of type `{type(widget)}`")


def set_widget_value(widget: QWidget, value: Any) -> None:
    if isinstance(widget, (QLineEdit, QTextEdit)):
        widget.setText(str(value))
    elif isinstance(widget, QSpinBox):
        try:
            widget.setValue(int(value))
        except Exception as e:
            print(e)
            print(type(e))

    elif isinstance(widget, QDoubleSpinBox):
        try:
            widget.setValue(float(value))
        except Exception as e:
            print(e)
            print(type(e))

    elif isinstance(widget, IChipsWidget) and isinstance(value, list):
        widget.add_chips(value)
    elif isinstance(widget, QCheckBox):
        state = Qt.CheckState.Unchecked
        if isinstance(value, Qt.CheckState):
            state = value
        elif value is True:
            state = Qt.CheckState.Checked
        elif value is False:
            state = Qt.CheckState.Unchecked

        widget.setCheckState(state)

    elif isinstance(widget, QCalendarWidget):
        if isinstance(value, (date, QDate)):
            widget.selectedDate(value)
