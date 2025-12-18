from PyQt5.QtCore import QThread, pyqtSignal
import json
import os


class AppLoader(QThread):
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, base_dir):
        super().__init__()

        self.base_dir = base_dir
        self.context = {}

    def run(self):

        try:
            steps = [
                (10, "Validando estructura del proyecto", self._check_paths),
                (30, "Cargando configuración de botones", self._load_hover_icons),
                (60, "Cargando biblioteca musical", self._load_music_data),
                (80, "Validando recursos de audio", self._validate_audio_files),
                (100, "Inicialización completada", None)
            ]

            for percent, text, task in steps:
                if task:
                    task()

                self.progress.emit(percent, text)

                self.msleep(700)

            self.finished.emit(self.context)

        except Exception as e:
            self.error.emit(str(e))

    # ──────────────────────────────

    def _check_paths(self):

        required_paths = [
            "resources/UI/MainApp.ui",
            "structure/hover_buttons.json",
            "structure/list_music.json",
            "resources/icons"
        ]

        for path in required_paths:
            full = os.path.join(self.base_dir, path)

            if not os.path.exists(full):
                raise FileNotFoundError(f"Recurso faltante: {path}")

    def _load_hover_icons(self):

        with open(os.path.join(self.base_dir, "structure/hover_buttons.json"), "r") as f:
            self.context["hover_icons"] = json.load(f)

    def _load_music_data(self):

        with open(os.path.join(self.base_dir, "structure/list_music.json"), "r", encoding="utf-8") as f:
            self.context["music_data"] = json.load(f)

    def _validate_audio_files(self):

        music_data = self.context["music_data"]

        invalid_files = []

        for game in music_data.values():
            base = game["path"]

            for song in game["songs"]:
                full = os.path.join(self.base_dir, base, song["file"])

                if not os.path.exists(full):
                    invalid_files.append(full)

        self.context["invalid_audio"] = invalid_files

