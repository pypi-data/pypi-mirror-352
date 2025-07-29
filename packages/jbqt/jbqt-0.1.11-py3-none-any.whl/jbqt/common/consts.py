import os
import re


import jbutils

from PyQt6.QtWidgets import QApplication, QMainWindow, QScrollArea, QWidget
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor

from jbqt.types import IconGetter

TAG_RE = re.compile(r"^\((.+)\)(\d+\.\d+)$")
LIST_ITEM_ROLE = Qt.ItemDataRole.UserRole - 1

STYLES = jbutils.STYLES
COLORS = jbutils.COLORS


class GlobalRefs:
    app: QApplication | None = None
    main_window: QMainWindow | None = None
    scroll_area: QScrollArea | None = None
    server_active: bool = False
    debug_set: bool = False
    seed_widget: QWidget | None = None


class QtPaths:
    icon_dir: str | None = None


THEME_ICONS: dict[str, QIcon] = {
    "save": QIcon.fromTheme("media-floppy-symbolic"),
    "new_file": QIcon.fromTheme("document-new-symbolic"),
    "open": QIcon.fromTheme("folder-open-symbolic"),
    "copy": QIcon.fromTheme("edit-paste-symbolic"),
    "inspect": QIcon.fromTheme("docviewer-app-symbolic"),
    "clone": QIcon.fromTheme("edit-copy-symbolic"),
    "plus": QIcon.fromTheme("list-add-symbolic"),
    "minus": QIcon.fromTheme("list-remove-symbolic"),
    "times": QIcon.fromTheme("cancel-operation-symbolic"),
    "refresh": QIcon.fromTheme("view-refresh-symbolic"),
    "reload": QIcon.fromTheme("update-symbolic"),
    "circle_check": QIcon.fromTheme("selection-checked"),
    "circle_x": QIcon.fromTheme("application-exit"),
    "code": QIcon.fromTheme("input-tablet-symbolic"),
    "font-selection-editor": QIcon.fromTheme("font-select-symbolic"),
    "trash": QIcon.fromTheme("trash-symbolic"),
    "edit_data": QIcon.fromTheme("document-edit-symbolic"),
    "preview": QIcon.fromTheme("view-layout-symbolic"),
    "sync": QIcon.fromTheme("mail-send-receive-symbolic"),
}
STD_ICONS: dict[str, QIcon] = {
    "save": QIcon.fromTheme(QIcon.ThemeIcon.DocumentSave),
    "new_file": QIcon.fromTheme(QIcon.ThemeIcon.DocumentNew),
    "open": QIcon.fromTheme(QIcon.ThemeIcon.FolderOpen),
    "copy": QIcon.fromTheme(QIcon.ThemeIcon.EditPaste),
    "inspect": QIcon.fromTheme(QIcon.ThemeIcon.DocumentPageSetup),
    "clone": QIcon.fromTheme(QIcon.ThemeIcon.EditCopy),
    "plus": QIcon.fromTheme(QIcon.ThemeIcon.ListAdd),
    "minus": QIcon.fromTheme(QIcon.ThemeIcon.DialogError),
    "times": QIcon.fromTheme(QIcon.ThemeIcon.ApplicationExit),
    "refresh": QIcon.fromTheme(QIcon.ThemeIcon.SystemReboot),
    "reload": QIcon.fromTheme(QIcon.ThemeIcon.MediaPlaylistRepeat),
    "circle_check": QIcon.fromTheme(QIcon.ThemeIcon.MediaPlaybackStart),
    "circle_x": QIcon.fromTheme(QIcon.ThemeIcon.ProcessStop),
    "code": QIcon.fromTheme(QIcon.ThemeIcon.Computer),
    "font-selection-editor": QIcon.fromTheme(QIcon.ThemeIcon.EditFind),
    "trash": QIcon.fromTheme(QIcon.ThemeIcon.EditDelete),
    "edit_data": QIcon.fromTheme(QIcon.ThemeIcon.InputTablet),
    "preview": QIcon.fromTheme(QIcon.ThemeIcon.ZoomIn),
    "sync": QIcon.fromTheme(QIcon.ThemeIcon.MediaPlaylistShuffle),
}


def set_icon_dir(path: str) -> None:
    QtPaths.icon_dir = path


class SIZES:
    ICON_XS = QSize(16, 16)
    ICON_SM = QSize(20, 20)
    ICON_MD = QSize(22, 22)
    ICON_LG = QSize(24, 24)
    ICON_XL = QSize(32, 32)
    ICON_XXL = QSize(48, 48)

    @classmethod
    def get(cls, key: str, default: QSize | None = None) -> QSize:
        if hasattr(cls, key):
            return getattr(cls, key)
        return default or cls.ICON_MD


def icon_dir(file_name: str) -> str:
    if QtPaths.icon_dir:
        return os.path.join(QtPaths.icon_dir, file_name)
    return file_name


def recolor_icon(
    image_path: str, color: str | QColor, scale: QSize | None = None
) -> QIcon:
    if not color:
        color = QColor("black")
    if isinstance(color, str):
        color = QColor(color)

    if scale is None:
        scale = SIZES.ICON_MD
    pixmap = QPixmap(image_path)
    icon_key = os.path.splitext(os.path.basename(image_path))[0]

    if pixmap.isNull():
        fallback = THEME_ICONS.get(icon_key, STD_ICONS.get(icon_key))
        if fallback:
            pixmap = fallback.pixmap()

    recolored_pixmap = QPixmap(pixmap.size())

    recolored_pixmap.fill(
        QColor("transparent")
    )  # Ensure the background is transparent
    painter = QPainter(recolored_pixmap)
    painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Source)

    # Draw the original pixmap
    painter.drawPixmap(0, 0, pixmap)

    # Apply the desired color
    painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
    painter.fillRect(pixmap.rect(), color)

    painter.end()
    return QIcon(recolored_pixmap.scaled(scale, Qt.AspectRatioMode.KeepAspectRatio))


def get_icon(file_name: str) -> IconGetter:
    def getter(color: str | QColor = "", size: QSize | int | None = None) -> QIcon:
        if isinstance(size, int):
            size = QSize(size, size)

        return recolor_icon(icon_dir(file_name), color, size)

    return getter


class ICONS:
    SAVE = get_icon("save.svg")
    NEW = get_icon("new_file.svg")
    OPEN = get_icon("open.png")
    COPY = get_icon("copy.png")
    INSPECT = get_icon("inspect.svg")
    CLONE = get_icon("clone.svg")
    PLUS = get_icon("plus.png")
    MINUS = get_icon("minus.png")
    TIMES = get_icon("times.svg")
    REFRESH = get_icon("refresh.svg")
    RELOAD = get_icon("reload.png")
    CIRCLE_CHECK = get_icon("circle_check.svg")
    CIRCLE_TIMES = get_icon("circle_x.svg")
    CODE = get_icon("code.png")
    EDIT = get_icon("font-selection-editor.png")
    TRASH = get_icon("trash.png")
    EDIT_DATA = get_icon("edit_data.svg")
    PREVIEW = get_icon("preview.png")
    SYNC = get_icon("sync.png")

    @classmethod
    def get(cls, name: str, default: str = "") -> IconGetter | str:
        if hasattr(cls, name):
            return getattr(cls, name)
        else:
            return default
