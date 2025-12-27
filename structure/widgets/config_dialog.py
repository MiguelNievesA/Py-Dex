from PyQt5.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QScrollArea,
    QWidget,
    QToolButton
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize, pyqtSignal, Qt

from qfluentwidgets import (
    FluentIcon,
    QConfig,
    RangeConfigItem,
    RangeValidator,
    qconfig,
    SettingCardGroup,
    RangeSettingCard,
    HyperlinkCard
)

# ==================================================
# Application Configuration Model
# ==================================================

class Config(QConfig):
    """
    Central configuration model for the application.
    """

    # ------------------------------
    # General Settings
    # ------------------------------

    numPokemon = RangeConfigItem(
        "General",          # Configuration group
        "NumPokemon",       # Configuration key
        20,                 # Default value
        RangeValidator(1, 40)  # Allowed range
    )

    # ------------------------------
    # Audio Settings
    # ------------------------------

    musicVolume = RangeConfigItem(
        "Audio",            # Configuration group
        "MusicVolume",      # Configuration key
        30,                 # Default value
        RangeValidator(0, 100)  # Allowed range
    )


# ==================================================
# Configuration Page UI
# ==================================================

class ConfigPage(QWidget):
    """
    Settings page widget for the Py-Dex application.
    """

    # Signal emitted when the user requests to go back
    backRequested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # Window-level configuration
        self.setWindowTitle("Configuration - Py-Dex")
        self.setMinimumSize(900, 490)

        # Initialize UI components
        self.initUI()

        # Apply background styling
        self.setStyleSheet("QWidget { background-color: white; }")


    # ==================================================
    # UI Initialization
    # ==================================================

    def initUI(self):
        """
        Builds and arranges all UI elements for the configuration page.
        """

        # ==================================================
        # Top Bar (Back Button)
        # ==================================================

        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(0, 0, 0, 8)

        self.btn_back = QToolButton(self)
        self.btn_back.setObjectName("btn_back")
        self.btn_back.setIcon(QIcon("resources/icons/buttons/arrow-right.svg"))
        self.btn_back.setIconSize(QSize(24, 24))
        self.btn_back.setToolTip("Return to Pokédex")
        self.btn_back.setCursor(Qt.PointingHandCursor)

        # Custom styling for the back button
        self.btn_back.setStyleSheet("""
            #btn_back {
                border: none;
                background-color: #ff8c54;
                padding: 3px;
                border-radius: 10px;
            }
        """)

        # Emit navigation signal when clicked
        self.btn_back.clicked.connect(self.backRequested.emit)

        top_bar.addWidget(self.btn_back, alignment=Qt.AlignLeft)
        top_bar.addStretch(1)

        # ==================================================
        # Scroll Area (Main Content)
        # ==================================================

        scroll = QScrollArea(self)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        scroll.setWidgetResizable(True)

        container = QWidget()
        layout = QVBoxLayout(container)

        # ==================================================
        # General Settings Section
        # ==================================================

        general_group = SettingCardGroup("Opciones generales", container)
        general_group.cardLayout.setContentsMargins(0, 0, 0, 30)
        general_group.titleLabel.setObjectName("titleLabel")

        # Highlight group title
        general_group.setStyleSheet(
            "#titleLabel { color: rgba(254, 144, 144, 1); }"
        )

        # Load persistent configuration
        self.cfg = Config()
        qconfig.load("config.json", self.cfg)

        # Pokémon amount selector
        self.range_num_pokemon = RangeSettingCard(
            self.cfg.numPokemon,
            FluentIcon.LABEL,
            "Número de Pokémon por carga",
            "Determina cuántos Pokémon se cargan cada vez que presionaste el botón 'Cargar más Pokémon' en la Pokédex.",
            general_group
        )

        general_group.addSettingCard(self.range_num_pokemon)

        # ==================================================
        # Audio Settings Section
        # ==================================================

        audio_group = SettingCardGroup("Música y Sonido", container)

        self.sound_volume = RangeSettingCard(
            self.cfg.musicVolume,
            FluentIcon.VOLUME,
            "Volumen de Música y Efectos de sonido",
            "Determina el volumen general de la música y los efectos de sonido en la aplicación.",
            audio_group
        )

        audio_group.addSettingCard(self.sound_volume)

        # ==================================================
        # Project Information Section
        # ==================================================

        project_group = SettingCardGroup("Proyecto", container)

        repo_link = HyperlinkCard(
            url="https://github.com/MiguelNievesA/Py-Dex",
            text="Repositorio del Proyecto",
            icon=FluentIcon.GITHUB,
            title="GitHub",
            content="Accede al código fuente del proyecto Py-Dex.",
            parent=project_group
        )

        project_group.addSettingCard(repo_link)

        # ==================================================
        # Layout Composition
        # ==================================================

        layout.addWidget(general_group)
        layout.addSpacing(24)
        layout.addWidget(audio_group)
        layout.addSpacing(24)
        layout.addWidget(project_group)
        layout.addStretch(1)

        scroll.setWidget(container)

        main_layout = QVBoxLayout(self)
        main_layout.addLayout(top_bar)
        main_layout.addWidget(scroll)
