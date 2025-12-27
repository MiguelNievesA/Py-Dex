from PyQt5.QtWidgets import QPushButton, QLayout
from PyQt5.QtCore import Qt
from pathlib import Path
from enum import Enum
import json


# ==================================================
# Styles Configuration
# ==================================================

# Path to the JSON file containing Pokémon type styles
STYLE_PATH = Path("structure/styles/types_styles_v2.json")


# ==================================================
# Style Mode Enum
# ==================================================

class TypeButtonStyle(Enum):
    """
    Defines the available visual styles
    for Pokémon type buttons.
    """
    FLAT = 1
    GRADIENT = 2


# ==================================================
# Pokémon Type Style Manager
# ==================================================

class PokemonTypeStyle:
    """
    Loads, stores and generates QSS styles
    based on Pokémon types.
    """

    def __init__(self):

        with open(STYLE_PATH, encoding="utf-8") as f:
            self._styles = json.load(f)

    def get(self, type_name: str) -> dict:
        return self._styles.get(type_name.lower(), {})


    # ==================================================
    # QSS Generators
    # ==================================================

    @staticmethod
    def widget_qss(base: str, accent: str) -> str:

        return f"""
        #pokemon {{
            border-radius: 18px;
            background-color: qlineargradient(
                x1:0, y1:0, x2:0, y2:1,
                stop:0 {accent},
                stop:1 {base}
            );
        }}
        """

    @staticmethod
    def button_qss(base: str, object_name: str) -> str:

        return f"""
        #{object_name} {{
            background-color: {base};
            color: white;
            border-radius: 5px;
            padding: 4px;
        }}
        """

    @staticmethod
    def button_gradient_qss(base: str, accent: str, object_name: str) -> str:

        return f"""
        #{object_name} {{
            color: white;
            border: none;
            border-radius: 8px;
            padding: 5px;
            background-color: qlineargradient(
                x1:0, y1:0, x2:0, y2:1,
                stop:0 {accent},
                stop:1 {base}
            );
        }}
        """

    @staticmethod
    def progressbar_qss(base: str, accent: str, text: str) -> str:

        return f"""
        QProgressBar {{
            border-style: none;
            text-align: center;
            background-color: white;
            border-radius: 5px;
            color: {text};
        }}

        QProgressBar::chunk {{
            border-radius: 5px;
            background-color: qlineargradient(
                spread:pad,
                x1:0, y1:0,
                x2:1, y2:0,
                stop:0 {base},
                stop:1 {accent}
            );
        }}
        """


# ==================================================
# Singleton Style Manager Instance
# ==================================================

_style_manager = PokemonTypeStyle()


# ==================================================
# Public Style Application Helpers
# ==================================================

def apply_type(widget, types: list[str]):

    primary = types[0].lower()
    primary_style = _style_manager.get(primary)

    if not primary_style:
        return

    # Apply main widget background style
    widget.pokemon.setStyleSheet(
        _style_manager.widget_qss(
            primary_style["base_color"],
            primary_style["accent_color"]
        )
    )

    # Force style refresh
    widget.pokemon.style().unpolish(widget.pokemon)
    widget.pokemon.style().polish(widget.pokemon)
    widget.pokemon.update()

    # Apply primary type button style
    _apply_type_button(widget.type_1, types[0], TypeButtonStyle.FLAT)

    # Apply secondary type button style if available
    if len(types) > 1:
        _apply_type_button(widget.type_2, types[1], TypeButtonStyle.FLAT)


def _apply_type_button(
    button: QPushButton,
    type_name: str,
    style_mode: TypeButtonStyle = TypeButtonStyle.FLAT
):

    style = _style_manager.get(type_name.lower())

    if not style:
        return

    # Select style mode
    if style_mode is TypeButtonStyle.GRADIENT:
        qss = _style_manager.button_gradient_qss(
            style["base_color"],
            style["accent_color"],
            button.objectName()
        )
    else:
        qss = _style_manager.button_qss(
            style["base_color"],
            button.objectName()
        )

    button.setStyleSheet(qss)

    # Force repaint
    button.style().unpolish(button)
    button.style().polish(button)
    button.update()


# ==================================================
# Abilities Buttons Styling
# ==================================================

def apply_abilities_buttons(
    abilities: list[str],
    target_layout: QLayout,
    primary_type: str
):

    style = _style_manager.get(primary_type.lower())

    if not style:
        return

    text_color = style["text_color"]

    # Clear existing buttons
    while target_layout.count():
        item = target_layout.takeAt(0)
        if item.widget():
            item.widget().deleteLater()

    # Align buttons to the top
    target_layout.setAlignment(Qt.AlignTop)

    # Create ability buttons
    for ability in abilities:
        btn = QPushButton(ability.title())
        btn.setStyleSheet(f"""
        QPushButton {{
            background-color: white;
            color: {text_color};
            border-radius: 6px;
            padding: 4px 8px;
        }}
        """)
        target_layout.addWidget(btn)