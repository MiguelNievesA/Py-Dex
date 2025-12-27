from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QLabel
from PyQt5.QtCore import (
    Qt,
    pyqtSignal,
    QPropertyAnimation,
    QEasingCurve,
    QTimer
)
from PyQt5.uic import loadUi

from structure.threads.pokemon_loader import PokemonLoader
from structure.styles.apply_typeStyleSheet import apply_type

from qfluentwidgets.components.widgets.info_bar import InfoBarPosition
from qfluentwidgets.components.widgets.info_bar import InfoBar

from enum import Enum


# ==================================================
# Gender Indicator Helper Class
# ==================================================

class GenderIndicator:
    """
    Helper class responsible for displaying Pokémon gender indicators.
    """

    def __init__(self, btn_male, btn_female, layout):

        self.btn_male = btn_male
        self.btn_female = btn_female
        self.layout = layout

        self.no_gender_label = None

        self.reset()


    # --------------------------------------------------
    # Gender State Management
    # --------------------------------------------------

    def reset(self):

        self.btn_male.hide()
        self.btn_female.hide()

        if self.no_gender_label:
            self.no_gender_label.hide()


    def apply(self, gender_rate: int):

        self.reset()

        # No gender Pokémon
        if gender_rate == -1:
            self._show_no_gender()
            return

        # Male-only Pokémon
        if gender_rate == 0:
            self.btn_male.show()
            return

        # Female-only Pokémon
        if gender_rate == 8:
            self.btn_female.show()
            return

        # Pokémon with both genders
        self.btn_male.show()
        self.btn_female.show()


    def _show_no_gender(self):

        if not self.no_gender_label:
            self.no_gender_label = QLabel("No gender")
            self.no_gender_label.setAlignment(Qt.AlignCenter)
            self.no_gender_label.setObjectName("label_no_gender")
            self.layout.addWidget(self.no_gender_label)

        self.no_gender_label.show()


# ==================================================
# Widget State Enumeration
# ==================================================

class WidgetState(Enum):
    """
    Represents the internal loading state of the Pokémon widget.
    """
    READY = 1
    ERROR = 2


# ==================================================
# Pokémon Card Widget
# ==================================================

class WidgetPokemon(QWidget):
    """
    Visual card widget representing a single Pokémon.
    """

    # Signals
    loaded = pyqtSignal()
    failed = pyqtSignal(object)
    selected = pyqtSignal(dict)  # Emits full Pokémon data


    def __init__(self, id_: int | str, main_window):
        super().__init__(main_window)

        # ---------------- Internal Attributes ----------------

        self.query = id_
        self.pokemon_id = None
        self.main_window = main_window
        self.state = None
        self._animated = False

        # ---------------- UI Loading ----------------

        # Load the .ui file designed in Qt Designer
        loadUi("resources/UI/widgets/widget_pokemon.ui", self)

        self.setFixedSize(251, 171)

        # Object names for stylesheet targeting
        self.pokemon.setObjectName("pokemon")
        self.type_1.setObjectName("type_1")
        self.type_2.setObjectName("type_2")

        # Type label sizing
        self.type_1.setFixedWidth(90)
        self.type_2.setFixedWidth(90)
        self.type_2.hide()

        # ---------------- Initial Visual State ----------------

        # Start invisible for appear animation
        self.target_height = 171
        self.setMaximumHeight(0)
        self.setVisible(False)

        # Begin loading Pokémon data
        self._startLoading()

        # Cursor and hover behavior
        self.setCursor(Qt.PointingHandCursor)
        self.setAttribute(Qt.WA_Hover, True)


    # ==================================================
    # Data Loading Logic
    # ==================================================

    def _startLoading(self):
        """
        Start asynchronous loading of Pokémon data.
        """
        self.loader = PokemonLoader(self.query)
        self.loader.finished.connect(self._onLoaded)
        self.loader.error.connect(self._onError)
        self.loader.start()


    # ==================================================
    # Loader Callbacks
    # ==================================================

    def _onLoaded(self, data: dict):

        # Basic Pokémon info
        self.pokemon_name = data["name"].lower()
        self.label_name.setText(self.pokemon_name.capitalize())

        # Real Pokémon ID from API
        self.pokemon_id = int(data["id"])

        # Formatted ID (e.g., #001)
        self.label_id.setText(f"#{self.pokemon_id:03d}")

        # Pokémon types
        self.types = data["types"]
        self.type_1.setText(self.types[0])

        if len(self.types) > 1:
            self.type_2.setText(self.types[1])
            self.type_2.show()

        # Pokémon image
        self.img_pokemon = QPixmap(
            f"resources/images_pokemon/{data['id']:03d}.png"
        )
        self.label_img.setPixmap(self.img_pokemon)

        # Apply dynamic stylesheet based on Pokémon types
        apply_type(self, self.types)

        # Update widget state
        self._set_state(WidgetState.READY)

        # Play appear animation once data is loaded
        QTimer.singleShot(0, self._playAppearAnimation)

        self.loaded.emit()
        self.data = data


    def _onError(self, message: str):

        self._set_state(WidgetState.ERROR)
        self.failed.emit(self)


    def retry_loading(self):

        if self.state == WidgetState.ERROR:
            self._startLoading()


    # ==================================================
    # State Management
    # ==================================================

    def _set_state(self, state: WidgetState):

        self.state = state

        if state == WidgetState.READY:
            self.state_stacked.setCurrentWidget(self.pokemon)

        elif state == WidgetState.ERROR:
            self.state_stacked.setCurrentWidget(self.loading)
            self.label_loading.setText("Error loading Pokémon")
            self._set_error_image(
                "resources/icons/error_loading_pokemon.png"
            )


    def _set_error_image(self, path: str):

        if hasattr(self, "movie"):
            self.movie.stop()

        self.label_loading_animation.setMovie(None)
        self.label_loading_animation.setPixmap(QPixmap(path))


    # ==================================================
    # Animations
    # ==================================================

    def _playAppearAnimation(self):

        if self._animated:
            return

        self._animated = True
        self.setVisible(True)

        animation = QPropertyAnimation(self, b"maximumHeight", self)
        animation.setDuration(670)
        animation.setStartValue(0)
        animation.setEndValue(self.target_height)
        animation.setEasingCurve(QEasingCurve.OutCubic)
        animation.start(QPropertyAnimation.DeleteWhenStopped)


    # ==================================================
    # Mouse Events
    # ==================================================

    def mousePressEvent(self, event):

        if (
            event.button() == Qt.LeftButton
            and self.state == WidgetState.READY
        ):
            self.selected.emit(self.data)

        super().mousePressEvent(event)