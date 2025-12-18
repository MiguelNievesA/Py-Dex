from PyQt5.QtCore import QThread, pyqtSignal
import asyncio
import aiohttp
from structure.threads.api_pokemon import APIPokemon
from structure.custom_exceptions import InternetConnectionError

class PokemonLoader(QThread):

    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, pokemon_id:int):
        super().__init__()
        self.pokemon_id = pokemon_id

    def run(self):

        try:
            asyncio.run(self._load())

        except InternetConnectionError as e:
            self.error.emit("Error de conexión al cargar el Pokémon")

    async def _load(self):

        async with aiohttp.ClientSession() as session:
            api = APIPokemon()
            data = await api.fetch_pokemon(session, self.pokemon_id)
            self.finished.emit(data)