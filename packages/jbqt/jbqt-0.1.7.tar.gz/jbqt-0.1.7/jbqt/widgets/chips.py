from re import Pattern

from PyQt6.QtCore import Qt, pyqtSignal, QObject, QEvent
from PyQt6.QtGui import QKeyEvent
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
    QComboBox,
)

import jbutils as utils
from jbqt.common import consts
from jbqt.models import IChipsWidget
from jbqt.widgets.chip_button import ChipButton
from jbqt.widgets.multiselect import MultiSelectComboBox
from jbqt.widgets.widget_utils import debug_scroll_pos


class ChipsWidget(IChipsWidget):
    valuesChanged = pyqtSignal(list)

    def __init__(
        self,
        chips=None,
        data: dict = None,
        path: str = "",
        label: str = "",
        weight_re: Pattern = None,
        use_weight: bool = False,
        debug: bool = False,
    ):
        super().__init__()
        self.values = chips or []
        # Main layout
        main_layout = QVBoxLayout()
        self.debug = debug
        if label:
            main_layout.addWidget(QLabel(label))
        self.installEventFilter(self)

        self.use_weight = use_weight
        if use_weight:
            weight_re = weight_re or consts.TAG_RE

        self.weight_re = weight_re
        self.options = data
        self.data = data or {}
        self.data_path = path
        self.list_widget: QComboBox | MultiSelectComboBox = None

        if data is not None:
            if isinstance(data, dict):
                if path:
                    self.options = utils.get_nested(self.data, path, [])

                self.list_widget = MultiSelectComboBox(
                    data=self.options, selected=self.values
                )
                self.list_widget.selectedChanged.connect(
                    self.handle_multiselect_change
                )

            elif isinstance(data, list):
                self.list_widget = QComboBox()

                # self.list_widget.addItems(self.options)
                for option in self.options:
                    self.list_widget.addItem(option)
                init_value = self.values[0] if self.values else ""
                self.list_widget.setCurrentText(init_value)
                self.list_widget.currentTextChanged.connect(
                    self.handle_multiselect_change
                )
            self.valuesChanged.connect(self.update_multiselect)
            main_layout.addWidget(self.list_widget)

        # Scroll area for the chips
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        # Widget inside the scroll area to hold the buttons
        self.chip_widget = QWidget()
        self.chip_layout = QHBoxLayout(self.chip_widget)
        self.chip_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # Add existing chips as buttons
        self.set_items(emit=False)

        scroll_area.setWidget(self.chip_widget)

        # Layout for the input and add button
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit(self)
        self.add_button = QPushButton("Add", self)
        self.add_button.clicked.connect(self.add_chip)

        self.clear_button = QPushButton(consts.ICONS.TRASH("darkred"), "", self)
        self.clear_button.clicked.connect(self.remove_all)
        # self.clear_button.setStyleSheet("color: red")

        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.add_button)
        input_layout.addWidget(self.clear_button)

        main_layout.addWidget(scroll_area)
        main_layout.addLayout(input_layout)

        self.setLayout(main_layout)

    def eventFilter(self, obj: QObject, event: QKeyEvent) -> bool:
        focus = consts.GlobalRefs.app.focusWidget()

        if event.type() == QEvent.Type.KeyPress and focus == self.input_field:
            match event.key():
                case Qt.Key.Key_Return | Qt.Key.Key_Enter:
                    self.add_chip()
        return super().eventFilter(obj, event)

    def get_unweight_chip(self, tag: str) -> str:
        if self.weight_re and self.weight_re.search(tag):
            return self.weight_re.search(tag).groups()[0]
        return tag

    def get_chip_list(self, tags: list[str]) -> list[str]:
        return [self.get_unweight_chip(tag) for tag in tags]

    def same_values(self, values: list[str]) -> bool:
        return set(self.get_chip_list(values)) == set(
            self.get_chip_list(self.values)
        )

    def handle_multiselect_change(self, selections: list[str] | str) -> None:
        if isinstance(selections, str):
            selections = [selections]

        selections = utils.dedupe_list(selections)
        if self.same_values(selections):
            return

        # self.values = selections
        self.set_items(selections, debug=True)

    def update_multiselect(self, values: list[str]) -> None:
        if isinstance(self.list_widget, MultiSelectComboBox):
            self.list_widget.set_selected(values, emit=False)
        else:
            value = values[0] if values else ""
            self.list_widget.setCurrentText(value)

    def clear_widgets(self) -> None:
        while self.chip_layout.count():
            widget = self.chip_layout.takeAt(0).widget()
            if widget is not None:
                widget.deleteLater()

    def set_items(
        self, values: list[str] = None, emit: bool = True, debug: bool = False
    ) -> None:
        self.clear_widgets()
        # TODO: Temp fix for weighted/custom tags and incoming multiselect values
        if values:
            tags = self.get_tag_list(self.values)
            for value in values:
                if value not in tags:
                    self.values.append(value)

            self.values = utils.dedupe_list(self.values)
        self.values = [value for value in self.values if value]
        for item in self.values:
            if not consts.GlobalRefs.debug_set:
                debug = True
                consts.GlobalRefs.debug_set = True
            else:
                debug = False
            chip_button = ChipButton(
                item,
                self.update_chip,
                self.remove_chip,
                debug=debug,
                weight_re=self.weight_re,
                use_weight=self.use_weight,
            )
            """ chip_button.setToolTip(
                f"Tag Count: {consts.TAG_COUNTS.get(item, "N/A")}"
            ) """

            self.chip_layout.addWidget(chip_button)

        if emit:
            self.emit_changes()

    def update_chip(self, prev_text: str, new_text: str) -> None:
        idx = self.values.index(prev_text)
        if idx >= 0:
            self.values[idx] = new_text

    def emit_changes(self):
        self.valuesChanged.emit(self.values)

    def add_chip(self):
        text = self.input_field.text().strip()
        if text and text not in self.values:
            chip_button = ChipButton(text, self.update_chip, self.remove_chip)

            self.chip_layout.addWidget(chip_button)
            self.values.append(text)
            self.emit_changes()
            self.input_field.setText("")

    def remove_chip(self, button: ChipButton):
        self.chip_layout.removeWidget(button)
        button.deleteLater()  # Schedule button widget for deletion
        self.values.remove(button.text)
        self.emit_changes()

    def add_chips(self, items: list[str]) -> None:
        utils.update_list_values(self.values, items)
        self.set_items()

    def remove_chips(self, items: list[str]) -> None:
        utils.remove_list_values(self.values, items)
        self.set_items()

    def remove_all(self, *_) -> None:
        self.values = []
        self.clear_widgets()
        self.emit_changes()
