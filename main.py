############################################
# Py-Dex: A Simple Application to Explore  #
#          the Pokémon Universe            #
#                                          #
############################################
#                BETA 2.1                  #
############################################

###########################################
#            Modulos PyQt                 #
###########################################

from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QAbstractButton, QSizePolicy, QGridLayout
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QEvent, QEasingCurve, QTimer
from PyQt5.uic import loadUi


from qfluentwidgets.components.widgets import InfoBar, InfoBarIcon
from qfluentwidgets.components.widgets.info_bar import InfoBarPosition
from qfluentwidgets.components.widgets import DropDownPushButton
from qfluentwidgets.components.widgets.menu import RoundMenu


###########################################
#         Modulos Secundarios             #
###########################################
import sys
import os
import json
import webbrowser

###########################################
#           Modulos Internos              #
###########################################
from structure.widgets.widget_pokemon import WidgetPokemon
from structure.threads.sounds_effects import SoundTrack

###########################################
#             Main Window                 #
###########################################

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class MainApp(QMainWindow):
    def __init__(self, context:dict | None = None):
        super().__init__()

        self.context = context or {}

        # Cargar el archivo .UI que contiene el diseño de la ventana
        loadUi("resources/UI/MainApp.ui", self)

        # Configuraciones basicas de la ventana
        self.setWindowTitle("Py-Dex Beta 2.1")
        self.setWindowIcon(QIcon("resources/icons/app_icon.png"))
        self.setFixedSize(988, 551)

        # Cargamos los elementos necesarios de la ventana y luego la mostramos
        self._createSubInterface()
        self.show()

    def _createSubInterface(self):

        self._pokemon_to_load = 0
        self._pokemon_loaded = 0

        # Atributos para controlar la carga de mas Pokemon
        self._batch_size = 20
        self._next_pokemon_id = 1

        # Variables para el manejo de la música
        self.current_track = None
        self.sound_track = None

        # Desactivar los botones del menú principal
        self.is_welcome = True
        self.btn_pokedex.setIcon(QIcon("resources/icons/menu/desactivate/pokedex_desactivate.svg"))
        self.btn_items.setIcon(QIcon("resources/icons/menu/desactivate/items_desactivate.svg"))
        self.btn_berries.setIcon(QIcon("resources/icons/menu/desactivate/berries_desactivate.svg"))
        self.btn_user.setIcon(QIcon("resources/icons/menu/desactivate/history_desactivate.svg"))

        # Diccionario de botones con efecto hover en sus iconos
        self.hover_icons = {}

        hover_data = self.context["hover_icons"]

        for obj_name, icons in hover_data.items():
            
            btn = self.findChild(QAbstractButton, obj_name)

            if btn is None:
                continue

            btn.installEventFilter(self)

            self.hover_icons[btn] = {
                "default": icons["default"],
                "hover": icons["hover"]
            }


        # Botón y ComboBox de Música
        self.btn_sound.is_mute = True
        self.btn_sound.clicked.connect(self._toggleMusic)

        # Añadimos el ComboBox de selección de música
        self.music_button = DropDownPushButton("Seleccionar música", self)
        self._createMusicMenu()

        self.frame_33.layout().addWidget(self.music_button)

        # Eventos - Botones de Bienvenida
        self.btn_repository.clicked.connect(lambda: webbrowser.open("https://github.com/MiguelNievesA/Py-Dex"))
        self.btn_email.clicked.connect(lambda: webbrowser.open("mailto:devBluePhoenix77@gmail.com?subject=Mensaje para proyecto Py-Dex-Beta2.1"))
        self.btn_start.clicked.connect(self._startPokedex)

        # Evento - Presione un boton desactivado
        self.btn_pokedex.clicked.connect(self.show_messageNotification)

        # Evento - Presionas a la img de Pikachu
        self.img_pikachu.installEventFilter(self)

        # Animaciones de widgets
        self.pages_app.setTransitionDirection(Qt.Horizontal)
        self.pages_app.setFadeTransition(True)
        self.pages_app.setTransitionSpeed(2000)
        self.pages_app.setFadeCurve(QEasingCurve.InOutQuad)

        # Desactivar slide
        self.pages_app.setSlideTransition(True)

        # Config ScrollArea
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setContentsMargins(0, 0, 0, 0)
        self.scrollArea.viewport().setContentsMargins(0, 0, 0, 0)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self._initPokedexLayout()

        # Config animacion del SmoothScrollArea
        self.scrollArea.setScrollAnimation(Qt.Vertical, 400, QEasingCurve.OutQuint)

        self.area_pokemon.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Preferred
        )

        # Evento de botones en general
        self.btn_more.clicked.connect(self._loadMorePokemon)

    def _startPokedex(self):

        self._showPokedexFlyout()
        self._loadInitialPokemon()

    def _showPokedexFlyout(self):
        
        InfoBar.new(
            icon=QIcon("resources/icons/buttons/icon_pokemon/pikachu.svg"),
            title="Mensaje para el usuario",
            content="Espere unos minutos mientras \ncargan los primeros Pokémon...",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=3500,
            parent=self
        ).show()

    def _initPokedexLayout(self):

        self.pokedex_layout = QGridLayout()
        self.pokedex_layout.setContentsMargins(8, 8, 8, 8)
        self.pokedex_layout.setHorizontalSpacing(6)
        self.pokedex_layout.setVerticalSpacing(12)

        self.area_pokemon.setLayout(self.pokedex_layout)

        self._columns = 3
        self._current_row = 0
        self._current_col = 0


    def _loadInitialPokemon(self):

        self._loadMorePokemon()


    def _loadMorePokemon(self):
        
        self._pokemon_loaded = 0
        self._pokemon_to_load = self._batch_size

        for _ in range(self._batch_size):

            pokemon_id = self._next_pokemon_id

            widget = WidgetPokemon(pokemon_id, self)
            widget.loaded.connect(self._onPokemonLoaded)
            widget.failed.connect(self._onPokemonLoaded)

            self.pokedex_layout.addWidget(
                widget,
                self._current_row,
                self._current_col
            )

            self._current_col += 1

            if self._current_col >= self._columns:
                self._current_col = 0
                self._current_row += 1

            self._next_pokemon_id += 1


    def _onPokemonLoaded(self):

        self._pokemon_loaded += 1

        if self._pokemon_loaded >= self._pokemon_to_load:
            self._onAllPokemonLoaded()

    def _onAllPokemonLoaded(self):

        # Espera 2 segundos antes de animar
        QTimer.singleShot(2000, self._showPokedexPage)

    def _showPokedexPage(self):

        index = self.pages_app.indexOf(self.pokedex)
        self.pages_app.slideToWidgetIndex(index)
         
###########################################
#      Metodos del sistema de musica      #
###########################################

    def _playMusic(self):

        if self.sound_track and self.sound_track.isRunning():
            self.sound_track.resume()
            return

        self.sound_track = SoundTrack(self.current_track, loop=True)
        self.sound_track.start()
    
    def _onMusicSelected(self):

        action = self.sender()
        
        if not isinstance(action, QAction):
            return
        
        self.current_track = action.data()
        self.music_button.setText(action.text())
        
        if self.sound_track:
            self.sound_track.stop_sountrack()

        if not self.btn_sound.is_mute:
            self._playMusic()

################################################
#    Implementación en la interfaz grafica     #
################################################

    def _createMusicMenu(self):

        main_menu = RoundMenu(parent=self.music_button)

        # Crear submenú de cada juego

        music_data = self.context["music_data"]

        for game in music_data.keys():

            sub_menu = RoundMenu(game, main_menu)

            for song in music_data[game]["songs"]:

                action = QAction(song["title"], self)
                action.setData(music_data[game]["path"] + "/" + song["file"])
                action.triggered.connect(self._onMusicSelected)
                sub_menu.addAction(action)

            main_menu.addMenu(sub_menu)

        self.music_button.setMenu(main_menu)

    def _toggleMusic(self):

        if self.music_button.text() == "Seleccionar música":
            InfoBar(
                parent=self,
                title="Mensaje para el usuario",
                content="No has seleccionado ninguna pista de música para reproducir, \natrévete a seleccionar tu favorita!",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                icon=InfoBarIcon.INFORMATION,
                duration=3500
            ).show()
            return
        
        if self.btn_sound.is_mute:
            # Activar música
            self.btn_sound.is_mute = False
            self.btn_sound.setIcon(QIcon("resources/icons/buttons/volume_on.svg"))
            self._playMusic()

        else:
            # Desactivar música
            self.btn_sound.is_mute = True
            self.btn_sound.setIcon(QIcon("resources/icons/buttons/volume_mute.svg"))
            self.sound_track.pause()


    def show_messageNotification(self):

        notification = InfoBar(
            parent=self,
            title="Mensaje para el usuario",
            content="Antes de usar esta función, dale al botón de 'Comenzar' para empezar la aventura",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            icon=InfoBarIcon.INFORMATION,
            duration=3500
        )

        notification.show()
        

###########################################
#       Control de eventos globales       #
###########################################

    def eventFilter(self, obj, event):

        # Click sobre IMG Pikachu

        if obj == self.img_pikachu and event.type() == QEvent.MouseButtonPress:
            if event.button() == Qt.LeftButton:

                self.sound_pikachu = SoundTrack("resources/sounds_effects/cry_pikachu.wav", loop=False)
                self.sound_pikachu.start()

                return True

        if event.type() == QEvent.Enter and obj in self.hover_icons:

            obj.setIcon(QIcon(self.hover_icons[obj]["hover"]))

        elif event.type() == QEvent.Leave and obj in self.hover_icons:

            obj.setIcon(QIcon(self.hover_icons[obj]["default"]))

        return super().eventFilter(obj, event)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    from structure.widgets.splash_screen import SplashScreen
    splash = SplashScreen()

    sys.exit(app.exec_())