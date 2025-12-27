from PyQt5.QtWidgets import QFrame, QLabel, QWidget, QVBoxLayout, QApplication
from PyQt5.QtGui import QMovie, QFont
from PyQt5.QtCore import Qt, QPropertyAnimation, QTimer
from PyQt5.uic import loadUi

from structure.threads.app_loader import AppLoader

from qfluentwidgets import InfoBar, InfoBarIcon
from qfluentwidgets.components.widgets.info_bar import InfoBarPosition

import sys
import os


# ==================================================
# Splash Screen Widget
# ==================================================

class SplashScreen(QFrame):
    """
    Splash screen shown at application startup.
    """

    def __init__(self):
        super().__init__()

        # ---------------- Configuration ----------------

        # Path to the animated GIF displayed during loading
        self.gif_path = "resources/animation_pikachu.gif"

        # ---------------- UI Loading ----------------

        # Load the UI designed with Qt Designer
        loadUi("resources/UI/splashScreen.ui", self)

        # Remove window borders and enable transparency
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Fixed window size
        self.setFixedSize(657, 430)

        # ---------------- GIF Animation Setup ----------------

        self.label_gif.setFixedSize(220, 160)

        # Load and configure the GIF animation
        self.movie = QMovie(self.gif_path)
        self.movie.setCacheMode(QMovie.CacheAll)

        # Scale the GIF while keeping its aspect ratio
        scaled_size = self.label_gif.size().scaled(
            self.label_gif.size(),
            Qt.KeepAspectRatio
        )

        self.movie.setScaledSize(scaled_size)
        self.movie.start()

        # Assign the animation to the label
        self.label_gif.setMovie(self.movie)

        # ---------------- Initial UI State ----------------

        self.progressBar.setValue(0)
        self.label_loading.setText("Starting Py-Dex...")

        # ---------------- Application Loader ----------------

        # Loader thread responsible for preparing the app context
        self.loader = AppLoader(
            os.path.abspath(os.path.dirname(sys.argv[0]))
        )

        self._connectLoader()

        # Loader state tracking
        self._load_success = False
        self._context = None

        # Display splash screen
        self.show()


    # ==================================================
    # Qt Events
    # ==================================================

    def showEvent(self, event):
        super().showEvent(event)

        if not self.loader.isRunning():
            # Small delay to allow the UI to render first
            QTimer.singleShot(100, self.loader.start)


    # ==================================================
    # Loader Signal Connections
    # ==================================================

    def _connectLoader(self):

        self.loader.progress.connect(self._onProgress)
        self.loader.finished.connect(self._onSuccess)
        self.loader.error.connect(self._showLoaderError)


    # ==================================================
    # Loader Callbacks
    # ==================================================

    def _onProgress(self, value, text):

        self.progressBar.setValue(value)
        self.label_loading.setText(text)


    def _onSuccess(self, context):

        self._load_success = True
        self._context = context

        self.label_loading.setText("Loading completed")

        # Delay before fading out the splash screen
        QTimer.singleShot(800, self._fadeOut)


    # ==================================================
    # Transition Animations
    # ==================================================

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


    # ==================================================
    # Main Application Launch
    # ==================================================

    def _openMain(self):

        from main import MainApp

        self.main = MainApp(self._context)
        self.main.show()

        self.close()


    # ==================================================
    # Error Handling
    # ==================================================

    def _showLoaderError(self, message):

        self.label_loading.setText("Error during loading!")

        InfoBar.error(
            parent=self,
            title="Application Error",
            content=message,
            orient=Qt.Vertical,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=3500
        )

        # Auto-close splash screen after showing error
        QTimer.singleShot(5000, self.close)