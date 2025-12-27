
from PyQt5.QtWidgets import QMenu, QWidget, QVBoxLayout, QWidgetAction, QFrame, QButtonGroup, QSizePolicy, QPushButton, QScrollArea
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect
from PyQt5.QtGui import QIcon

class OptionMenu:
    """
    Generic widget-based menu for buttons.
    Allows custom widgets, exclusive groups, separators
    and action buttons.
    """

    def __init__(self, parent_button, width=220, animation_duration=160):


        # ----- MENU ------
        self.menu = QMenu(parent_button)
        self.menu.setWindowFlags(
            self.menu.windowFlags() | Qt.FramelessWindowHint
        )
        self.menu.setAttribute(Qt.WA_TranslucentBackground)

        # ------ ROOT CONTAINER ------
        self.container = QWidget(self.menu)
        self.container.setFixedWidth(width)
    
        self.layout = QVBoxLayout(self.container)
        self.layout.setContentsMargins(8, 6, 8, 6)
        self.layout.setSpacing(6)

        # ----- WIDGET ACTION -----
        self._action = QWidgetAction(self.menu)
        self._action.setDefaultWidget(self.container)
        self.menu.addAction(self._action)

        parent_button.setMenu(self.menu)

        # ------ INTERNAL GROUPS ------
        self._groups: dict[str, QButtonGroup] = {}

        # ------ ANIMATION ------
        self._animation = QPropertyAnimation(self.container, b"geometry")
        self._animation.setDuration(animation_duration)
        self._animation.setEasingCurve(QEasingCurve.OutCubic)

        self.menu.aboutToShow.connect(self._animate_show)
        self.menu.aboutToHide.connect(self._animate_hide)

        self._final_height = 0

    # --------------------------------------------------
    # Widget Management
    # --------------------------------------------------

    def add_widget(self, widget):

        widget.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.layout.addWidget(widget)
        return widget
    
    def add_spacing(self, value: int = 6):
        self.layout.addSpacing(value)

    def add_separator(self):
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFixedHeight(1)
        self.layout.addWidget(separator)

    # --------------------------------------------------
    # Exclusive Groups
    # --------------------------------------------------

    def create_exclusive_group(self, name: str):

        if name in self._groups:
            raise ValueError(f"Group '{name}' already exists.")

        group = QButtonGroup(self.container)
        group.setExclusive(True)
        self._groups[name] =  group
        return group

    def add_to_group(self, group_name: str, button):

        if group_name not in self._groups:
            raise ValueError(f"Group '{group_name}' does not exist.")
        self._groups[group_name].addButton(button)

    # --------------------------------------------------
    # Action Button
    # --------------------------------------------------

    def add_action_button(
         self,
         text: str,
         icon_path: str | None = None,
         callback=None,
         height: int = 28,
         qss_path: str | None = None
    ):
        
        btn = QPushButton(text)
        btn.setFixedHeight(height)
        btn.setCursor(Qt.PointingHandCursor)

        # ------ SIZE & POLICY ------
        btn.setFixedHeight(height)
        btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        btn.setMinimumWidth(self.container.width() - 16)

        if icon_path:
            btn.setIcon(QIcon(icon_path))

        if qss_path:
            from structure.styles.apply_qss import StyleManager
            StyleManager.apply_to_widget(btn, qss_path)

        if callable(callback):
            btn.clicked.connect(callback)

        self.layout.addWidget(btn)
        return btn

    # --------------------------------------------------
    # Combo Box
    # --------------------------------------------------
    
    def add_combo_box(
        self,
        combobox,
        height: int  = 28,
    ):

        combobox.setFixedHeight(height)
        combobox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.layout.addWidget(combobox)

        return combobox

    # --------------------------------------------------
    # Control
    # --------------------------------------------------

    def close(self):
        self.menu.close()

    # ==================================================
    # Animation logic
    # ==================================================

    def _update_height(self):

        self.container.adjustSize()
        self._final_height =  self.container.sizeHint().height()

    def _animate_show(self):

        self._update_height()

        start_rect = QRect(
            0,
            0,
            self.container.width(),
            0
        )

        end_rect = QRect(
            0,
            0,
            self.container.width(),
            self._final_height
        )

        self.container.setGeometry(start_rect)

        self._animation.stop()
        self._animation.setStartValue(start_rect)
        self._animation.setEndValue(end_rect)
        self._animation.start()

    def _animate_hide(self):

        start_rect = self.container.geometry()

        end_rect = QRect(
            start_rect.x(),
            start_rect.y(),
            start_rect.width(),
            0
        )

        self._animation.stop()
        self._animation.setStartValue(start_rect)
        self._animation.setEndValue(end_rect)
        self._animation.start()