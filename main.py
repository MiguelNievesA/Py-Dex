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

from PyQt5.QtWidgets import QApplication, QMainWindow, QAction
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QEvent, QSize, QEventLoop, QTimer
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
from structure.threads.api_pokemon import APIPokemon
from structure.threads.sounds_effects import SoundTrack


###########################################
#             Main Window                 #
###########################################

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Cargar el archivo .UI que contiene el diseño de la ventana
        loadUi("resources/UI/MainApp.ui", self)

        # Configuraciones basicas de la ventana
        self.setWindowTitle("Py-Dex Beta 2.1")
        self.setWindowIcon(QIcon("resources/icons/app_icon.png"))
        self.setFixedSize(929, 551)

        # Cargamos los elementos necesarios de la ventana y luego la mostramos
        self._createSubInterface()
        self.show()

    def _createSubInterface(self):

        # Desactivar los botones del menú principal
        self.is_welcome = True
        self.btn_pokedex.setIcon(QIcon("resources/icons/menu/desactivate/pokedex_desactivate.svg"))
        self.btn_items.setIcon(QIcon("resources/icons/menu/desactivate/items_desactivate.svg"))
        self.btn_berries.setIcon(QIcon("resources/icons/menu/desactivate/berries_desactivate.svg"))
        self.btn_user.setIcon(QIcon("resources/icons/menu/desactivate/history_desactivate.svg"))

        # Diccionario de mapas e iconos 

        self.hover_icons = {

            self.btn_repository: ("resources/icons/welcome/github_theme.svg", "resources/icons/welcome/github.svg"),
            self.btn_email: ("resources/icons/welcome/email_theme.svg", "resources/icons/welcome/email.svg"),
            self.btn_start: ("resources/icons/buttons/arrow-left_theme.svg", "resources/icons/buttons/arrow-left.svg")
        }

        for btn in self.hover_icons.keys():

            btn.installEventFilter(self)

        # Botón y ComboBox de Música
        self.btn_sound.is_mute = True
        self.btn_sound.clicked.connect(self._onMusicSelected)

        # Añadimos el ComboBox de selección de música
        self.music_button = DropDownPushButton("Seleccionar música", self)
        self._createMusicMenu()

        self.frame_33.layout().addWidget(self.music_button)

        # Eventos - Botones de Bienvenida
        self.btn_repository.clicked.connect(lambda: webbrowser.open("https://github.com/MiguelNievesA/Py-Dex"))
        self.btn_email.clicked.connect(lambda: webbrowser.open("mailto:devBluePhoenix77@gmail.com?subject=Mensaje para proyecto Py-Dex-Beta2.1"))

        # Evento - Presione un boton desactivado

        self.btn_pokedex.clicked.connect(self.show_messageNotification)

        loop = QEventLoop(self)
        QTimer.singleShot(3000, loop.quit)
        loop.exec_()

    def _createMusicMenu(self):

        main_menu = RoundMenu(parent=self.music_button)

        # Crear submenú de cada juego

        with open("structure/list_music.json", "r") as file:

            music_data = json.load(file)

            for game in music_data.keys():

                sub_menu = RoundMenu(game, main_menu)

                for song in music_data[game]["songs"]:

                    action = QAction(song["title"], triggered=lambda: self._onMusicSelected(song["title"], song["file"]))
                    sub_menu.addAction(action)

                main_menu.addMenu(sub_menu)

        self.music_button.setMenu(main_menu)


    def _onMusicSelected(self, title, file_path):

        self.music_button.setText(title)

        if self.btn_sound.is_mute:

            self.btn_sound.setIcon(QIcon("resources/icons/buttons/volume_on.svg"))
            self.btn_sound.is_mute = False

            # Reproducir la música seleccionada
            self.sound_track = SoundTrack(file_path, loop=True)
            self.sound_track.start()
            return

        self.btn_sound.setIcon(QIcon("resources/icons/buttons/volume_off.svg"))
        self.btn_sound.is_mute = True

        # Detener la música
        self.sound_track.stop_sountrack()

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


    def eventFilter(self, obj, event):

        if event.type() == QEvent.Enter and obj in self.hover_icons:

            obj.setIcon(QIcon(self.hover_icons[obj][1]))

        elif event.type() == QEvent.Leave and obj in self.hover_icons:

            obj.setIcon(QIcon(self.hover_icons[obj][0]))

        return super().eventFilter(obj, event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    sys.exit(app.exec_())