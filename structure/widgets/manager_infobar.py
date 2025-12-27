from qfluentwidgets import InfoBar
from PyQt5.QtCore import QEvent

class ManagedInfoBar(InfoBar):
    """
    InfoBar subclass that notifies when it is closed,
    using Qt event system instead of timers.
    """

    def __init__(self, *args, on_closed=None, **kwargs):
        super().__init__(*args, **kwargs)

        self._on_closed_callback = on_closed

    def closeEvent(self, event):

        if callable(self._on_closed_callback):
            self._on_closed_callback()

        super().closeEvent(event)