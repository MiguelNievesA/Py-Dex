from PyQt5.QtCore import QThread, pyqtSignal
import json
import os


BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

class AppLoader(QThread):
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.base_dir = BASE_DIR

        # Central application context
        self.context = {
            "warnings": [],
            "invalid_audio": []
        }

    def run(self):

        try:
            steps = [
                (5, "Preparando la interfaz gráfica", self._check_ui),
                (15, "Validando estructura de la aplicación", self._check_paths),
                (30, "Cargando iconos interactivos", self._load_hover_icons),
                (45, "Cargando música del sistema", self._load_music_data),
                (65, "Comprobando archivos de audio", self._validate_audio_files),
                (80, "Cargando estilos visuales", self._validate_type_styles),
                (90, "Preparando recuersos gráficos de los Pokémon", self._validate_image),
                (100, "Inicialización completada", None)
            ]

            for percent, text, task in steps:
                if task:
                    task()

                self.progress.emit(percent, text)

                self.msleep(400)

            self.finished.emit(self.context)

        except Exception as e:
            self.error.emit(str(e))

    # ──────────────────────────────

    def _check_ui(self):

        ui_files = [
            "resources/UI/MainApp.ui",
            "resources/UI/widgets/widget_pokemon.ui"
        ]

        for f in ui_files:
            full = os.path.join(self.base_dir, f)

            if not os.path.exists(full):
                raise FileNotFoundError("Los archivos .UI no fueron encontrados")
            
        self.context["ui_ok"] = True

    def _check_paths(self):

        required_paths = [
            "resources/icons",
            "resources/styles_qss",
            "resources/images_pokemon",
            "resources/sounds_effects",
            "structure/styles"
        ]

        for path in required_paths:
            full = os.path.join(self.base_dir, path)

            if not os.path.exists(full):
                raise FileNotFoundError(f"Recurso faltante: {path}")

    def _load_hover_icons(self):

        path = os.path.join(self.base_dir, "structure/hover_buttons.json")

        try:

            with open(path, encoding="utf-8") as f:
                data = json.load(f)

        except json.JSONDecodeError:
            raise ValueError("El archivo 'hover_buttons.json' está corrupto o dañado.")
        
        # Validate expected structure

        for key, icons in data.items():

            if "default" not in icons or "hover" not in icons:
                raise ValueError("Icono hover inválido: {key}")
            
            self.context["hover_icons"] = data

    def _load_music_data(self):

        path = os.path.join(self.base_dir, "structure/list_music.json")

        try:

            with open(path, encoding="utf-8") as f:
                data = json.load(f)

        except json.JSONDecodeError:
            raise ValueError("El archivo 'list_music.json' está corrupto o dañado.")

        self.context["music_data"] = data

    def _validate_audio_files(self):

        music_data = self.context["music_data"]

        invalid_files = []
        total_files = 0

        for game in music_data.values():
            base = game["path"]
            valid_songs = []

            for song in game["songs"]:
                total_files += 1
                full = os.path.join(self.base_dir, base, song["file"])
                
                if os.path.exists(full):
                    valid_songs.append(song)
                else:
                    invalid_files.append(full)

            game["songs"] = valid_songs

        self.context["invalid_audio"] = invalid_files
        self.context["total_audio_files"] = total_files

        invalid = len(self.context["invalid_audio"])
        total = self.context["total_audio_files"]

        if invalid == total:
            raise RuntimeError(
                "La aplicación no puede iniciar: los archivos de música no fueron encontrados."
            )
        
        elif invalid > 0:
            self.context["warnings"].append(
                "Algunos archivos de música no fueron encontrados y por lo cual no estarán disponibles en la aplicación."
            )
    
    def _validate_type_styles(self):

        path = os.path.join(self.base_dir, "structure/styles/types_styles_v2.json")

        try:

            with open(path, encoding="utf-8") as f:
                styles = json.load(f)

        except json.JSONDecodeError:
            raise ValueError("El archivo 'types_styles_v2.json' está corrupto o dañado")
        
        required_keys = {"base_color", "accent_color", "text_color"}

        for t, style in styles.items():

            if not required_keys.issubset(style):
                raise ValueError(f"Invalid style definition for type: {t}")
            
        self.context["styles_ok"] = True
    
    def _validate_image(self):

        img_dir = os.path.join(self.base_dir, "resources/images_pokemon")

        if not os.listdir(img_dir):
            raise FileNotFoundError(f"Recurso faltante: {img_dir}")