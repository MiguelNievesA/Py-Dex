from PyQt5.QtWidgets import QFrame, QLabel, QWidget, QVBoxLayout, QApplication
from PyQt5.QtGui import QMovie, QFont
from PyQt5.QtCore import Qt, QPropertyAnimation, QTimer
from PyQt5.uic import loadUi
from structure.threads.app_loader import AppLoader

from qfluentwidgets import InfoBar, InfoBarIcon
from qfluentwidgets.components.widgets.info_bar import InfoBarPosition

import sys
import os
import traceback

class SplashScreen(QFrame):
    def __init__(self):
        super().__init__()

        self.gif_path = "resources/animation_pikachu.gif"

        # Cargar diseño
        loadUi("resources/UI/splashScreen.ui", self)

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.setFixedSize(657, 451)

        # GIF animation
        self.label_gif.setFixedSize(220, 160)
        self.movie = QMovie(self.gif_path)
        self.movie.setCacheMode(QMovie.CacheAll)

        # Redimensionar la animación
        target_width = 160

        scaled_size = self.label_gif.size().scaled(
            self.label_gif.size(),
            Qt.KeepAspectRatio
        )

        self.movie.setScaledSize(scaled_size)

        self.movie.start()
        self.label_gif.setMovie(self.movie)

        # Estado inicial
        self.progressBar.setValue(0)
        self.label_loading.setText("Iniciando Py-Dex...")

        # Loader
        self.loader = AppLoader(os.path.abspath(os.path.dirname(sys.argv[0])))
        self._connectLoader()

        self._load_success = False
        self._context = None

        self.show()

    def showEvent(self, event):
        super().showEvent(event)

        if not self.loader.isRunning():
            QTimer.singleShot(100, self.loader.start)

    def _connectLoader(self):

        self.loader.progress.connect(self._onProgress)
        self.loader.finished.connect(self._onSuccess)
        self.loader.error.connect(self._showLoaderError)

    def _onProgress(self, value, text):

        self.progressBar.setValue(value)
        self.label_loading.setText(text)

    def _onSuccess(self, context):
        self._load_success = True
        self._context = context

        self.label_loading.setText("Carga completada")
        QTimer.singleShot(8000, self._fadeOut)

    def _fadeOut(self):

        self.anim = QPropertyAnimation(self, b"windowOpacity")
        self.anim.setDuration(600)
        self.anim.setStartValue(1)
        self.anim.setEndValue(0)
        self.anim.finished.connect(self._onFadeFinished)
        self.anim.start()

    def _onFadeFinished(self):

        self.close()

        if self._load_success:
            self._openMain()

    def _openMain(self):
        from main import MainApp

        self.main = MainApp(self._context)
        self.main.show()

        self.close()

    def _showLoaderError(self, message):

        self.label_loading.setText(f"Error durante la carga!")

        InfoBar.error(
            parent=self,
            title="Error en la aplicación...",
            content=f"{message}",
            orient=Qt.Vertical,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=3500
        )

        QTimer.singleShot(5000, self.close)
