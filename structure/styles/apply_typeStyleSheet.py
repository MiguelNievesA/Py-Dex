from PyQt5.QtWidgets import QPushButton
import json
from pathlib import Path

STYLE_PATH = Path("structure/styles/types_styles_v2.json")

class PokemonTypeStyle(object):
    def __init__(self):

        with open(STYLE_PATH, encoding="utf-8") as f:
            self._styles = json.load(f)

    def get(self, type_name:str) -> dict:
        return self._styles.get(type_name.lower(), {})
    
    @staticmethod
    def widget_qss(base:str, accent:str) -> str:

        return f""" 
        #pokemon {{
            border-radius: 18px;
            background-color: qlineargradient(
                x1:0, y1:0, x2:0, y2:1, stop:0 {accent},
                stop:1 {base}
            )
        }}

        """
    
    @staticmethod
    def button_qss(base:str, object_name:str) -> str:

        return f"""
        #{object_name} {{
        background-color: {base};
        color: white;
        border-radius: 5px;
        padding: 4px;
        }}

        """
    

_style_manager = PokemonTypeStyle()

def apply_type(widget, types: list[str]):

    primary = types[0].lower()
    primary_style = _style_manager.get(primary)

    if not primary_style:
        return

    # Estilo del widget principal
    widget.pokemon.setStyleSheet(
        _style_manager.widget_qss(
            primary_style["base_color"],
            primary_style["accent_color"]
        )
    )

    widget.pokemon.style().unpolish(widget.pokemon)
    widget.pokemon.style().polish(widget.pokemon)
    widget.pokemon.update()

    # Botón tipo 1
    _apply_type_button(widget.type_1, types[0])

    # Botón tipo 2 (si existe)
    if len(types) > 1:
        _apply_type_button(widget.type_2, types[1])

    

def _apply_type_button (button, type_name:str):
    
    style = _style_manager.get(type_name.lower())

    if not style:
        return
    
    button.setStyleSheet(
        _style_manager.button_qss(
            style["base_color"],
            button.objectName()
        )
    )

    button.style().unpolish(button)
    button.style().polish(button)
    button.update()
     