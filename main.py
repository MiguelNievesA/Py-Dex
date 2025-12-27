############################################
# Py-Dex: A Simple Application to Explore  #
#          the Pokémon Universe            #
#                                          #
#                BETA 2.1                  #
############################################

# ======================================================
# Standard Library
# ======================================================
import sys
import os
import webbrowser


# ======================================================
# PyQt5 - Core
# ======================================================
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QAction, 
    QAbstractButton, QSizePolicy, QGridLayout
)
from PyQt5.QtGui import QIcon, QPixmap, QDesktopServices
from PyQt5.QtCore import Qt, QEvent, QEasingCurve, QTimer, QUrl
from PyQt5.uic import loadUi

# ======================================================
# External UI Components (qfluentwidgets)
# ======================================================
from qfluentwidgets.components.widgets import (
    InfoBar, InfoBarIcon, DropDownPushButton, CheckBox, ComboBox
)
from qfluentwidgets.components.widgets.info_bar import InfoBarPosition
from qfluentwidgets.components.widgets.menu import RoundMenu
from qfluentwidgets import InfoBarIcon
from qfluentwidgets import FluentIcon

# ======================================================
# Internal Project Modules
# ======================================================
from structure.widgets.widget_pokemon import WidgetPokemon, GenderIndicator, WidgetState
from structure.widgets.config_dialog import ConfigPage
from structure.widgets.manager_infobar import ManagedInfoBar
from structure.widgets.option_menu import OptionMenu

from structure.styles.apply_qss import StyleManager
from structure.threads.sounds_effects import SoundTrack
from structure.threads.pokemon_loader import PokemonLoader
from structure.threads.app_state import ConnectionManager

from structure.styles.stats_animator import StatsAnimator
from structure.styles.apply_typeStyleSheet import (
    PokemonTypeStyle,
    _apply_type_button,
    TypeButtonStyle,
    apply_abilities_buttons
)

# ======================================================
# Utility Functions
# ======================================================
def get_spanish_description(descriptions: list[dict]) -> str:
    for entry in descriptions:
        if entry["language"] == "es":
            return entry["text"]
    return descriptions[0]["text"] if descriptions else ""


# ======================================================
# Main Application Window
# ======================================================
class MainApp(QMainWindow):
    """
    Main application window for Py-Dex.
    """

    def __init__(self, context: dict | None = None):
        super().__init__()

        # Shared application context (icons, music data, etc.)
        self.context = context or {}

        # UI and application initialization pipeline
        self._load_ui()
        self._configure_window()
        self._init_state()
        self._init_ui_components()
        self._init_connections()

        self.show()

    # --------------------------------------------------
    # UI Loading & Window Configuration
    # --------------------------------------------------
    def _load_ui(self):
        loadUi("resources/UI/MainApp.ui", self)

    def _configure_window(self):
        self.setWindowTitle("Py-Dex Beta 2.1")
        self.setWindowIcon(QIcon("resources/icons/app_icon.png"))
        self.setFixedSize(1050, 551)

    # --------------------------------------------------
    # Application State Initialization
    # --------------------------------------------------
    def _init_state(self):

        # Pokedex batch loading state
        self._batch_size = 20
        self._next_pokemon_id = 1
        self._pokemon_loaded = 0
        self._pokemon_to_load = 0

        # Grid layout state
        self._columns = 3
        self._current_row = 0
        self._current_col = 0

        # Loaded and failed pokemon tracking
        self._loaded_pokemon_ids = set()
        self._cached_grid_widgets = []
        self._failed_widgets = set()

        # UI and connection flags
        self.is_initial_loading = False
        self._connection_error_shown = False
        self._is_searching = False

        # Audio state
        self.current_track = None
        self.sound_track = None
        self.is_muted = True

        # Pokemon stats animation state
        self._current_base_stats = {}
        self.stats_animator = StatsAnimator(self)

        # Buttons in development
        self.buttons_deveploment = [
            self.btn_items,
            self.btn_berries,
            self.btn_user
        ]

        for btn in self.buttons_deveploment:
            btn.clicked.connect(self.show_messageDevelopment)

        # Global InfoBar control
        self._active_infobar = None

        # Pokedex filter and ordering state
        self.active_filters = {"type_1": None}
        self.active_order = {
            "key": None,
            "reverse": False
        }

        self._all_pokemon_widgets = []

    # --------------------------------------------------
    # UI Components Setup
    # --------------------------------------------------
    def _init_ui_components(self):

        self._init_menu_buttons()
        self._init_hover_icons()
        self._init_music_menu()
        self._init_order_menu()
        self._init_filter_menu()
        self._init_config_page()
        self._init_gender_indicator()
        self._init_scroll_area()
        self._init_anim_stackedWidget()

        # Hide retry button by default (only shown on loading failures)
        self.btn_retry.setVisible(False)

        # Pointing hand cursor for interactive elements
        self.btn_start.setCursor(Qt.PointingHandCursor)
        self.btn_repository.setCursor(Qt.PointingHandCursor)
        self.btn_email.setCursor(Qt.PointingHandCursor)

        self.btn_pokedex.setCursor(Qt.PointingHandCursor)
        self.btn_items.setCursor(Qt.PointingHandCursor)
        self.btn_berries.setCursor(Qt.PointingHandCursor)
        self.btn_user.setCursor(Qt.PointingHandCursor)
        self.btn_settings.setCursor(Qt.PointingHandCursor)

        self.btn_filter.setCursor(Qt.PointingHandCursor)
        self.btn_order.setCursor(Qt.PointingHandCursor)
        self.btn_sound.setCursor(Qt.PointingHandCursor)
        self.btn_search.setCursor(Qt.PointingHandCursor)

        self.btn_more.setCursor(Qt.PointingHandCursor)
        self.btn_retry.setCursor(Qt.PointingHandCursor)

        self.page_button_info.setCursor(Qt.PointingHandCursor)
        self.page_button_stats.setCursor(Qt.PointingHandCursor)

        self.btn_return.setCursor(Qt.PointingHandCursor)
        self.config_page.btn_back.setCursor(Qt.PointingHandCursor)


        # Install a global event filter on the Pikachu image
        self.img_pikachu.installEventFilter(self)

    # --------------------------------------------------
    # Signals & Slots
    # --------------------------------------------------
    def _init_connections(self):

        self.btn_start.clicked.connect(self._startPokedex)
        self.btn_more.clicked.connect(self._loadMorePokemon)
        self.btn_retry.clicked.connect(self._retryFailedPokemon)

        self.btn_search.clicked.connect(self._searchPokemon)
        self.btn_settings.clicked.connect(self.show_messageNotification)

        self.page_button_info.clicked.connect(self._showInfoPage)
        self.page_button_stats.clicked.connect(self._showStatsPage)

        self.btn_sound.clicked.connect(self.toggleMusic)
        self.btn_return.clicked.connect(self._slideToHomePokedex)

        # Buttons page welcome
        self.btn_repository.clicked.connect(lambda: webbrowser.open("https://github.com/MiguelNievesA/Py-Dex"))
        self.btn_email.clicked.connect(self._openEmailClient)

        # Return button from config page to main Pokedex page
        self.config_page.backRequested.connect(lambda: self.pages_app.slideToWidget(self.pokedex))

        # Synchronize music volume slider width sound engine
        self.config_page.sound_volume.valueChanged.connect(self._onConfigChanged)

        # Connect range_num_pokemon to reload pokedex
        self.config_page.range_num_pokemon.valueChanged.connect(self._onNumPokemonChanged)

    def _openEmailClient(self):

        email = "devBluePhoenix77@gmail.com"
        subject = "Feedback Py-Dex"
        body = "Hola,\n\nMe gustaría compartir los siguientes comentarios sobre Py-Dex:\n"
        webbrowser.open(f"mailto:{email}?subject={subject}&body={body}")

    def _init_menu_buttons(self):

        self.is_welcome = True

        # Set inactive icon for main menu buttons
        self.btn_pokedex.setIcon(QIcon("resources/icons/menu/desactivate/pokedex_desactivate.svg"))
        self.btn_items.setIcon(QIcon("resources/icons/menu/desactivate/items_desactivate.svg"))
        self.btn_berries.setIcon(QIcon("resources/icons/menu/desactivate/berries_desactivate.svg"))
        self.btn_user.setIcon(QIcon("resources/icons/menu/desactivate/history_desactivate.svg"))

        # Notify user when clicking Pokedex during welcome state
        icon = QIcon()
        icon.addPixmap(
            QPixmap("resources/icons/menu/desactivate/pokedex_desactivate.svg"),
            QIcon.Normal
        )
        icon.addPixmap(
            QPixmap("resources/icons/menu/desactivate/pokedex_desactivate.svg"),
            QIcon.Disabled
        )
        self.btn_pokedex.setIcon(icon)
        self.btn_pokedex.clicked.connect(self.show_messagePokedex)

    def _init_hover_icons(self):

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

    def _init_music_menu(self):

        self.music_button = DropDownPushButton("Seleccionar música", self)
        main_menu = RoundMenu(parent=self.music_button)

        # Create a submenu for each Pokemon game

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

        # Insert music selector into de UI layout
        self.frame_20.layout().insertWidget(1, self.music_button)

    def _init_order_menu(self):

        # Hide default menu indicator arrow
        self.btn_order.setStyleSheet("""
        QPushButton::menu-indicator {
            image: none;
            width: 0px;
        }
        """)

        self.menu_order = OptionMenu(self.btn_order)

        # ----- SORT CRITERIA -----
        self.cb_id = CheckBox("ID (# / Número)")
        self.cb_alpha = CheckBox("Alfabético (A-Z)")
        self.cb_stats = CheckBox("Total Stats")

        self.menu_order.add_widget(self.cb_id)
        self.menu_order.add_widget(self.cb_alpha)
        self.menu_order.add_widget(self.cb_stats)

        # Group criteria checkboxes (exclusive selection)
        criteria_group = self.menu_order.create_exclusive_group("criteria")
        self.menu_order.add_to_group("criteria", self.cb_id)
        self.menu_order.add_to_group("criteria", self.cb_alpha)
        self.menu_order.add_to_group("criteria", self.cb_stats)

        # ----- SEPARATOR -----
        self.menu_order.add_spacing(4)
        self.menu_order.add_separator()
        self.menu_order.add_spacing(4)

        # ----- SORT DIRECTION -----
        self.cb_asc = CheckBox("Ascendente")
        self.cb_desc = CheckBox("Descendente")

        for cb in (self.cb_id, self.cb_alpha, self.cb_asc, self.cb_desc):
            cb.setFixedHeight(24)

        self.menu_order.add_widget(self.cb_asc)
        self.menu_order.add_widget(self.cb_desc)

        # Group direction checkboxes (exclusive selection)
        direction_group = self.menu_order.create_exclusive_group("direction")
        self.menu_order.add_to_group("direction", self.cb_asc)
        self.menu_order.add_to_group("direction", self.cb_desc)

        # ----- APPLY BUTTON -----
        self.menu_order.add_spacing(6)
        
        self.btn_apply_order = self.menu_order.add_action_button(
            text="Apply",
            icon_path="resources/icons/buttons/apply.svg",
            qss_path="resources/styles_qss/btn_apply.qss",
            callback=self._applyPokemonOrder,
            height=40
        )

        # ===== DEFAULT STATE =====
        self.cb_id.setChecked(True)
        self.cb_asc.setChecked(True)

    def _init_filter_menu(self):

        # Hide default menu indicator
        self.btn_filter.setStyleSheet("""
        QPushButton::menu-indicator {
            image: none;
            width: 0px;                              
        }
        """)

        # Hide default menu indicator
        self.menu_filter = OptionMenu(self.btn_filter)

        # ===============================
        # Type Filter (ComboBox)
        # ===============================

        self.cb_type = ComboBox()
        self.cb_type.setPlaceholderText("Filtrar por tipo")
        self.cb_type.addItem("Todos los tipos", None)

        types = [
        "fuego", "agua", "planta", "eléctrico", "psíquico",
        "roca", "tierra", "hielo", "dragón", "siniestro",
        "hada", "acero", "fantasma", "lucha", "veneno",
        "bicho", "volador", "normal"
        ]

        for t in types:
            self.cb_type.addItem(t.capitalize(), t)

        self.menu_filter.add_combo_box(self.cb_type, height=32)

        # ==================================================
        # Separator
        # ==================================================

        self.menu_filter.add_spacing(6)
        self.menu_filter.add_separator()
        self.menu_filter.add_spacing(8)

        # ==================================================
        # Apply Filters
        # ==================================================

        self.btn_apply_filter = self.menu_filter.add_action_button(
            text="Apply Filters",
            icon_path="resources/icons/buttons/filter.svg",
            qss_path="resources/styles_qss/btn_apply.qss",
            callback=self._applyPokemonFilters,
            height=40
        )

    # --------------------------------------------------
    # Configuration Page
    # --------------------------------------------------

    def _init_config_page(self):

        self.config_page = ConfigPage(self)
        self.pages_app.addWidget(self.config_page)

    # --------------------------------------------------
    # Gender Indicator
    # --------------------------------------------------

    def _init_gender_indicator(self):

        self.gender_indicator =  GenderIndicator(
            btn_male=self.gender_male,
            btn_female=self.gender_female,
            layout=self.gender_layout.layout()
        )

    # --------------------------------------------------
    # Stacked Widget Animations
    # --------------------------------------------------

    def _init_anim_stackedWidget(self):

        self.pages_app.setTransitionDirection(Qt.Horizontal)
        self.pages_app.setFadeTransition(True)
        self.pages_app.setTransitionSpeed(2000)
        self.pages_app.setFadeCurve(QEasingCurve.InOutQuad)

        # Enable slide animation effect
        self.pages_app.setSlideTransition(True)

    # --------------------------------------------------
    # ScrollArea Pokedex
    # --------------------------------------------------

    def _init_scroll_area(self):

        # ScrollArea base configuration
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setContentsMargins(0, 0, 0, 0)
        self.scrollArea.viewport().setContentsMargins(0, 0, 0, 0)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Initialize Pokedex grid layout
        self._initPokedexLayout()

        # Smmoth vertical scroll animation
        self.scrollArea.setScrollAnimation(Qt.Vertical, 400, QEasingCurve.OutQuint)

        # Allow Pokemon area to expand horizontally
        self.area_pokemon.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Preferred
        )


    # --------------------------------------------------
    # Pokédex – Initialization & Entry Point
    # --------------------------------------------------

    def _startPokedex(self):

        if not ConnectionManager.has_internet():
            self._showConnectionWarning("No se detectó conexión a internet. No es posible iniciar la Pokédex.")
            return

        # Leave start button
        self.is_welcome = False

        # Enable configuration button
        try:
            self.btn_settings.clicked.disconnect()
        except TypeError:
            pass

        self.btn_settings.clicked.connect(self._openConfig)

        self.is_initial_loading = True
        self._connection_error_shown = False

        # Load the first batch of Pokemon
        self._loadMorePokemon()

    # --------------------------------------------------
    # Pokédex – UI Feedback & Notifications
    # --------------------------------------------------

    def _showConnectionWarning(self, message: str):

        InfoBar.warning(
            parent=self,
            title="Sin conexión a internet",
            content=message,
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=4000
        ).show()

    def _showPokedexFlyout(self):

        icon_pixmap = QPixmap("resources/icons/buttons/icon_pokemon/pikachu.svg").scaled(
            28, 28,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        
        InfoBar.new(
            icon=icon_pixmap,
            title="Mensaje para el usuario",
            content="Espere unos minutos mientras \ncargan los primeros Pokémon...",
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=3500,
            parent=self
        ).show() 

    # --------------------------------------------------
    # Pokédex – Grid Layout Setup
    # --------------------------------------------------

    def _initPokedexLayout(self):

        self.pokedex_layout = QGridLayout()
        self.pokedex_layout.setContentsMargins(8, 8, 8, 8)
        self.pokedex_layout.setHorizontalSpacing(6)
        self.pokedex_layout.setVerticalSpacing(12)

        self.area_pokemon.setLayout(self.pokedex_layout)

        # Grid tracking state
        self._columns = 3
        self._current_row = 0
        self._current_col = 0

    # --------------------------------------------------
    # Pokédex – Pokémon Loading Logic
    # --------------------------------------------------

    def _loadMorePokemon(self):

        if self.is_initial_loading:
            self._showPokedexFlyout()

        # Reset batch counters
        self._pokemon_loaded = 0
        self._pokemon_to_load = self._batch_size

        # Create Pokemon widgets sequentially
        for _ in range(self._batch_size):
            self._addPokemonWidget(self._next_pokemon_id)
            self._next_pokemon_id += 1

    def _addPokemonWidget(self, pokemon_id: int):

        widget = WidgetPokemon(pokemon_id, self)
        self._all_pokemon_widgets.append(widget)

        # Connect widget lifecycle signals
        widget.loaded.connect(self._onPokemonLoaded)
        widget.failed.connect(self._onPokemonFailed)
        widget.selected.connect(self._openPokemonApiPage)

        self.pokedex_layout.addWidget(
            widget,
            self._current_row,
            self._current_col
        )


        self._loaded_pokemon_ids.add(pokemon_id)

        # Advance grid position
        self._current_col += 1
        if self._current_col >= self._columns:
            self._current_col = 0
            self._current_row += 1

    # --------------------------------------------------
    # Pokédex – Load Callbacks
    # --------------------------------------------------

    def _onPokemonLoaded(self):

        widget = self.sender()

        if not widget:
            return

        self._pokemon_loaded += 1
        self._updateRetryAndMoreButtons()

        # When the batch finishes loading
        if self._pokemon_loaded >= self._pokemon_to_load:
            self._onAllPokemonLoaded()

    def _onPokemonFailed(self, widget: WidgetPokemon):

        self._failed_widgets.add(widget)

        # ----- INITIAL LOAD ERROR -----
        if self.is_initial_loading:

            self.is_initial_loading = False
            self._showConnectionWarning("No fue posible cargar los Pokémon iniciales. Verifica tu conexión para poder continuar.")
            return

        # ----- POST-INITIAL ERROR -----
        if not self._connection_error_shown:
            self._connection_error_shown = True
            self._showConnectionWarning("Falta de conexión a internet para cargar los datos.")

        self._updateRetryAndMoreButtons()

    # --------------------------------------------------
    # Pokédex – Retry & Load State Controls
    # --------------------------------------------------

    def _updateRetryAndMoreButtons(self):

        if self._failed_widgets:
            self.btn_retry.setVisible(True)
            self.btn_more.setVisible(False)
            return

        self.btn_retry.setVisible(False)
        self.btn_more.setVisible(True)

    def _retryFailedPokemon(self):
        
        if not self._failed_widgets:
            return
        
        failed = list(self._failed_widgets)
        self._failed_widgets.clear()

        # Reset visual error flag
        self._connection_error_shown = False

        self.btn_retry.setVisible(True)
        self.btn_more.setVisible(False)

        for widget in failed:
            widget.retry_loading()

    # ---------------------------------------------------
    # Pokédex – Post Load & Navigation
    # ---------------------------------------------------

    def _onAllPokemonLoaded(self):

        if self.is_initial_loading:
            self.is_initial_loading = False

        self._refreshPokedexView()

        # Delay before showing Pokedex page
        QTimer.singleShot(800, self._showPokedexPage)
        
        # Activate Pokedex Icon
        icon = QIcon()
        icon.addPixmap(
            QPixmap("resources/icons/menu/pokedex.svg"),
            QIcon.Normal
        )
        icon.addPixmap(
            QPixmap("resources/icons/menu/pokedex.svg"),
            QIcon.Disabled
        )

        self.btn_pokedex.setIcon(icon)
        self.btn_pokedex.setEnabled(False)

    def _showPokedexPage(self):

        index = self.pages_app.indexOf(self.pokedex)
        self.pages_app.slideToWidgetIndex(index)

    # --------------------------------------------------
    # Pokédex – Grid Utilities
    # --------------------------------------------------

    def _clearPokedexGrid(self):

        self._cached_grid_widgets = self._getAllPokemonWidgets()

        while self.pokedex_layout.count():
            item = self.pokedex_layout.takeAt(0)

            if item.widget():
                item.widget().setParent(None)

    def _restorePokedexGrid(self):

        self._rebuildPokedexLayout(self._cached_grid_widgets)
        self._is_searching = False

    def _getAllPokemonWidgets(self):

        widgets_pokemon = []

        for i in range(self.pokedex_layout.count()):
            
            item = self.pokedex_layout.itemAt(i)
            widget = item.widget()

            if isinstance(widget, WidgetPokemon):
                widgets_pokemon.append(widget)

        return widgets_pokemon
    
    def _rebuildPokedexLayout(self, widgets:list):

        # Remove all widgets from the layout safely
        while self.pokedex_layout.count():
            item = self.pokedex_layout.takeAt(0)

            if item.widget():
                item.widget().setParent(None)

        # Reset grid positioning counters
        self._current_row = 0
        self._current_col = 0

        # Reinsert widgets row by row
        for widget in widgets:
            self.pokedex_layout.addWidget(widget, self._current_row, self._current_col)

            self._current_col += 1
            if self._current_col >= self._columns:
                self._current_col = 0
                self._current_row += 1

    # ==================================================
    # Pokemon Ordering Logic
    # ==================================================

    def _applyPokemonOrder(self):

        # Close order menu after applying changes
        self.menu_order.close()

        # ----- RESOLVE ORDERING KEY -----
        if self.cb_id.isChecked():
            key = lambda w: w.pokemon_id

        elif self.cb_alpha.isChecked():
            key = lambda w: w.pokemon_name

        elif self.cb_stats.isChecked():
            key = lambda w: sum(w.data["base_stats"].values())

        else:
            return

        # ----- RESOLVE ORDERING DIRECTION -----
        reverse = self.cb_desc.isChecked()

        # ----- PERSIST ACTIVE ORDERING STATE -----
        self.active_order["key"] = key
        self.active_order["reverse"] = reverse

        # ----- REFRESH VISUAL GRID -----
        self._refreshPokedexView()

    # ==================================================
    # Pokemon Filtering Logic
    # ==================================================

    def _applyPokemonFilters(self):

        self.menu_filter.close()

        # ----- RESOLVE SELECTED TYPE FILTER -----
        selected_type = self.cb_type.currentText()

        if selected_type == "Todos los tipos" or not selected_type:
            selected_type = None
        else:
            selected_type = selected_type.lower()

        # Persist active filter state
        self.active_filters["type_1"] = selected_type

        # Refresh grid after applying filters
        self._refreshPokedexView()

    def _refreshPokedexView(self):

        widgets = filtered_widgets = []

        selected_type = self.active_filters.get("type_1")

         # ----- FILTERING STAGE -----
        for w in self._all_pokemon_widgets:

            # Ignore widgets that are not fully loaded
            if w.state != WidgetState.READY:
                continue

            # Apply type filter if active
            if selected_type:
                if selected_type not in w.data.get("types", []):
                    continue

            filtered_widgets.append(w)

        # ----- ORDERING STAGE -----

        order_key = self.active_order["key"]
        reverse = self.active_order["reverse"]

        if order_key is not None:
            filtered_widgets.sort(key=order_key, reverse=reverse)

        # ----- EMPTY RESULT FEEDBACK -----
        if not filtered_widgets:
            self._showManagedInfoBar(
                title="Sin resultados",
                message="No se encontraron Pokémon que coincidan con los filtros aplicados."
            )
            return

        # Clear the grid visually
        self._rebuildPokedexLayout(filtered_widgets)

    # ==================================================
    # Pokémon Detail Page Navigation
    # ==================================================

    def _openPokemonApiPage(self, data: dict):

        self._fillPokemonApiPage(data)

        index = self.pages_app.indexOf(self.page_pokemon)
        self.pages_app.slideToWidgetIndex(index)

    def _fillPokemonApiPage(self, data: dict):

        style_manager = PokemonTypeStyle()

        # ----- Basic information -----
        self.label_page_name.setText(data["name"].capitalize())
        self.label_page_id.setText(f"N° {data['id']:03d}")

        # ----- Pokemon image -----
        pixmap = QPixmap(f"resources/images_pokemon/{data['id']:03d}.png")
        self.label_page_img.setPixmap(pixmap)

        types = data["types"]

        # ----- Primary type -----
        self.page_type_1.setText(types[0].capitalize())
        _apply_type_button(self.page_type_1, types[0], TypeButtonStyle.GRADIENT)
        self.page_type_1.show()

        # ----- Secondary type (optional) -----
        if len(types) > 1:

            self.page_type_2.setText(types[1].capitalize())
            _apply_type_button(self.page_type_2, types[1], TypeButtonStyle.GRADIENT)
            self.page_type_2.show()

        else:
            self.page_type_2.hide()

        # ----- Gender indicator ----
        self.gender_indicator.apply(data["gender_ratio"])

        # ----- Physical attributes -----
        height_m = data["height"] / 10
        weight_kg = data["weight"] / 10
        self.label_page_height.setText(f"Altura: {height_m} metros")
        self.label_page_weight.setText(f"Peso: {weight_kg} Kg")

        # ----- Abilities -----
        apply_abilities_buttons(
            data["abilities"],
            self.frame_54.layout(),
            types[0]
        )

        apply_abilities_buttons(
            data["hidden_ability"],
            self.frame_56.layout(),
            types[0]
        )

        # ==========================
        # Base Stats Setup
        # ==========================

        self.stats_bars = {
            "hp": self.bar_hp,
            "attack": self.bar_atk,
            "defense": self.bar_def,
            "special-attack": self.bar_atk_sp,
            "special-defense": self.bar_def_sp,
            "speed": self.bar_speed
        }

        style = style_manager.get(types[0].lower())
        
        if not style:
            return
        
        qss = style_manager.progressbar_qss(
            style["base_color"],
            style["accent_color"],
            style["text_color"]
        )

        self._current_base_stats = data["base_stats"]

        # Prepare all stat bars before animation
        for bar in self.stats_bars.values():
            self.stats_animator.prepare_bar(bar, qss, 255)

        self._total_stats_value = sum(self._current_base_stats.values())

        self.stats_animator.prepare_bar(self.bar_total, qss, 1530)

        # ----- Pokemon description -----
        self.page_description.setPlainText(get_spanish_description(data["description"]))

    def _animateStatsBars(self):

        self.stats_animator.clear()

        for stat, value in self._current_base_stats.items():
            bar = self.stats_bars.get(stat)

            if bar:
                self.stats_animator.animate_bar(bar, value)

        self.stats_animator.animate_bar(
            self.bar_total,
            self._total_stats_value,
            duration=1000,
            easing=QEasingCurve.OutQuart
        )

    # ==================================================
    # Navigation Helpers
    # ==================================================

    def _slideToHomePokedex(self):
        
        self.pages_app.slideToWidget(self.pokedex)
        self.page_api_pokemon.setCurrentWidget(self.show_info_basic)

    def _showInfoPage(self):

        self.page_api_pokemon.setTransitionDirection(Qt.RightToLeft)
        self.page_api_pokemon.setTransitionSpeed(600)
        self.page_api_pokemon.setFadeTransition(True)
        self.page_api_pokemon.setFadeCurve(QEasingCurve.InOutQuad)

        self.page_api_pokemon.slideToWidget(self.show_info_basic)

    def _showStatsPage(self):

        transition_time = 600

        # Reset all progress bars before animation
        for bar_stat in self._current_base_stats.keys():
            self.stats_bars[bar_stat].setValue(0)

        self.bar_total.setValue(0)

        # Configuracion de animacion
        self.page_api_pokemon.setTransitionDirection(Qt.LeftToRight)
        self.page_api_pokemon.setTransitionSpeed(transition_time)
        self.page_api_pokemon.setFadeTransition(True)
        self.page_api_pokemon.setFadeCurve(QEasingCurve.InOutQuad)

        self.page_api_pokemon.slideToWidget(self.show_stats_base)

        # Delay animation until transition ends
        QTimer.singleShot(transition_time + 50, self._animateStatsBars)

    # ==================================================
    # Pokémon Search Logic
    # ==================================================

    def _searchPokemon(self):

        # Normalize user input for consistent comparisons
        query = self.search_pokemon.text().strip().lower()

        # Abort search if input is empty
        if not query:
            return 
        
        # ==================================================
        # Search in Already Loaded Pokémon
        # ==================================================

        for widget in self._getAllPokemonWidgets():

            # ----- Search by numeric ID -----
            if query.isdigit() and widget.pokemon_id == int(query):
                self._openPokemonApiPage(widget.data)
                return

            # ----- Search by exact Pokemon name -----
            if widget.pokemon_name.lower() == query:
                self._openPokemonApiPage(widget.data)
                return

        # ==================================================
        # Pokemon Not Loaded → Fetch from API
        # ==================================================

        # Create a loader thread to fetch Pokemon data asynchronously
        self.search_loader = PokemonLoader(query)

        # Connect loader signals
        self.search_loader.finished.connect(self._onSearchPokemonLoaded)
        self.search_loader.error.connect(self._onSearchPokemonError)

        # Start background API requests
        self.search_loader.start()

    def _onSearchPokemonLoaded(self, data: dict):

        # Open Pokemon detail page with fetched data
        self._openPokemonApiPage(data)

    def _onSearchPokemonError(self, message: str):

        InfoBar.warning(
            parent=self,
            title="Pokemon no encontrado",
            content=message,
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=3500
        )

    def _onNumPokemonChanged(self, value: int):

        self._batch_size = value

    # ==================================================
    # Application Navigation
    # ==================================================

    def _openConfig(self):

        self.pages_app.slideToWidget(self.config_page)
        
    # ==================================================
    # Background Music Control
    # ==================================================

    def _playMusic(self):

        volume = self.config_page.cfg.musicVolume.value

        # Resume playback if a track is already running
        if self.sound_track and self.sound_track.isRunning():
            self.sound_track.resume()
            return

        # Create a new SoundTrack thread for background music
        self.sound_track = SoundTrack(
            self.current_track,
            loop=True,
            volume=volume
        )

        self.sound_track.start()
    
    def _onMusicSelected(self):

        action = self.sender()
        
        # Store selected track path
        if not isinstance(action, QAction):
            return

        # Update button label with selected song title
        self.current_track = action.data()
        self.music_button.setText(action.text())
        
        # Stop currently playing track (if any)
        if self.sound_track:
            self.sound_track.stop_sountrack()

        # Automatically play music if not muted
        if not self.is_muted:
            self._playMusic()

    def toggleMusic(self):

        # Prevent toggling if no music has been selected
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
        
        # ----- Enable music -----
        if self.is_muted:
            # Activar música
            self.is_muted = False
            self.btn_sound.setIcon(QIcon("resources/icons/buttons/volume_on.svg"))
            self._playMusic()

        # ----- Disable music -----
        else:
            # Desactivar música
            self.is_muted = True
            self.btn_sound.setIcon(QIcon("resources/icons/buttons/volume_mute.svg"))
            self.sound_track.pause()

    def _onConfigChanged(self, value):

        if self.sound_track:
            self.sound_track.set_volume(value)

    # ==================================================
    # Music Menu Construction
    # ==================================================

    def _createMusicMenu(self):

        main_menu = RoundMenu(parent=self.music_button)

        # Create a submenu for each game
        music_data = self.context["music_data"]

        for game in music_data.keys():

            sub_menu = RoundMenu(game, main_menu)

            # Create an action for each song
            for song in music_data[game]["songs"]:

                action = QAction(song["title"], self)
                action.setData(music_data[game]["path"] + "/" + song["file"])
                action.triggered.connect(self._onMusicSelected)
                sub_menu.addAction(action)

            main_menu.addMenu(sub_menu)

        self.music_button.setMenu(main_menu)


    # ==================================================
    # Global InfoBar Throttle Controller
    # ==================================================

    def _showManagedInfoBar(
        self,
        *,
        title: str,
        message: str,
        icon=InfoBarIcon.INFORMATION,
        duration: int = 3500,
    ):

        # Prevent multiple InfoBars at the same time
        if self._active_infobar is not None:
            return
        
        def _on_infobar_closed():
            self._active_infobar = None
        
        self._active_infobar = ManagedInfoBar(
            parent=self,
            title=title,
            content=message,
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            icon=icon,
            duration=duration,
            on_closed=_on_infobar_closed
        )

        self._active_infobar.show()

    def show_messagePokedex(self):

        self._showManagedInfoBar(
            title="Mensaje para el usuario",
            message="Para iniciar la Pokédex, haz clic en el botón 'Comenzar'.",
        )

    def show_messageNotification(self):

        self._showManagedInfoBar(
            title="Mensaje para el usuario",
            message="Antes de usar esta función, dale al botón de comenzar para empezar la aventura.",
        )

        
    def show_messageDevelopment(self):

        self._showManagedInfoBar(
            title="Función en desarollo",
            message="Estoy trabajando todavía en está función!",
            icon=FluentIcon.UPDATE
        )

    # ==================================================
    # Global Event Handling
    # ==================================================

    def eventFilter(self, obj, event):

        # ----- Pikachu image click -----
        if obj == self.img_pikachu and event.type() == QEvent.MouseButtonPress:
            if event.button() == Qt.LeftButton:

                self.sound_pikachu = SoundTrack("resources/sounds_effects/cry_pikachu.wav", loop=False)
                self.sound_pikachu.start()

                return True

        # ----- Hover icons enter -----
        if event.type() == QEvent.Enter and obj in self.hover_icons:
            obj.setIcon(QIcon(self.hover_icons[obj]["hover"]))

        # ----- Hover icon leave ------
        elif event.type() == QEvent.Leave and obj in self.hover_icons:
            obj.setIcon(QIcon(self.hover_icons[obj]["default"]))

        return super().eventFilter(obj, event)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Display splash screen before main window
    from structure.widgets.splash_screen import SplashScreen
    splash = SplashScreen()

    sys.exit(app.exec_())