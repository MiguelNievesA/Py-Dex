from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QMovie
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.uic import loadUi

from structure.threads.pokemon_loader import PokemonLoader
from structure.styles.apply_typeStyleSheet import apply_type

from qfluentwidgets.components.widgets import InfoBar, InfoBarIcon
from qfluentwidgets.components.widgets.info_bar import InfoBarPosition
from enum import Enum

#####################################
#    Widget Pokémon Show            #
#####################################

class WidgetState(Enum):
    LOADING = 0
    READY = 1
    ERROR = 2


class WidgetPokemon(QWidget):
    loaded = pyqtSignal()
    failed = pyqtSignal()
    def __init__(self, id_:int, main_window):
        super().__init__(main_window)

        # Atributos de la clase
        self.pokemon_id = id_
        self.state = WidgetState.LOADING
        self.main_window = main_window

        # Cargar el diseño del arhcivo .UI
        loadUi("resources/UI/widgets/widget_pokemon.ui", self)

        self.setFixedSize(251, 171)

        self.pokemon.setObjectName("pokemon")
        self.type_1.setObjectName("type_1")
        self.type_2.setObjectName("type_2")

        self.type_1.setFixedWidth(90)
        self.type_2.setFixedWidth(90)

        self.type_2.hide()

        self._setup_ui()
        self._connect_signals()
        self._startLoading()

    # ---------------- UI ---------------- #

    def _setup_ui(self):

        self.state_stacked.setCurrentWidget(self.loading)

        self.btn_retry.hide()

        self._set_loading_animation("resources/animation_loading.gif")

    def _connect_signals(self):

        self.btn_retry.clicked.connect(self._startLoading)


    # ---------------- LOAD ---------------- #
    
    def _startLoading(self):

        self._set_state(WidgetState.LOADING)

        self.loader = PokemonLoader(self.pokemon_id)
        self.loader.finished.connect(self._onLoaded)
        self.loader.error.connect(self._onError)
        self.loader.start()

    # ---------------- CALLBACKS ---------------- #

    def _onLoaded(self, data:dict):

        # Datos Principales
        self.label_name.setText(data["name"].capitalize())
        self.label_id.setText(f"#{data['id']:03d}")

        # Tipos
        types = data["types"]

        self.type_1.setText(types[0])

        if len(types) > 1:
            self.type_2.setText(types[1])
            self.type_2.show()

        self.label_img.setPixmap(QPixmap(f"resources/images_pokemon/{data['id']:03d}.png"))

        apply_type(self, types)

        self._set_state(WidgetState.READY)
        self.loaded.emit()

    def _onError(self, message:str):
        
        self._set_state(WidgetState.ERROR)
        self.failed.emit()

        InfoBar.warning(
            parent=self.main_window,
            title="Error en la carga de datos",
            content="Verifique su conexión a internet",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=3500
        )

    def _set_state(self, state: WidgetState):

        self.state = state

        if state == WidgetState.LOADING:
            self.state_stacked.setCurrentWidget(self.loading)
            self.label_loading.setText("Cargando...")
            self.btn_retry.hide()
            self._set_loading_animation("resources/animation_loading.gif")

        elif state ==  WidgetState.READY:
            self.state_stacked.setCurrentWidget(self.pokemon)

        elif state == WidgetState.ERROR:

            self.state_stacked.setCurrentWidget(self.loading)
            self.label_loading.setText("Error al cargar Pokémon")
            self.btn_retry.show()
            self._set_error_image("resources/icons/error_loading_pokemon.png")

    def _set_loading_animation(self, path:str):

        movie = QMovie(path)
        self.label_loading_animation.setMovie(movie)
        movie.start()

    def _set_error_image(self, path:str):

        if hasattr(self, "movie"):
            self.movie.stop()

        self.label_loading_animation.setMovie(None)
        self.label_loading_animation.setPixmap(QPixmap(path))
