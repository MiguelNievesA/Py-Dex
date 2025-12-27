from PyQt5.QtCore import QThread, pyqtSignal
import asyncio
import aiohttp
from structure.threads.api_pokemon import APIPokemon
from structure.custom_exceptions import InternetConnectionError
from structure.custom_exceptions import PokemonNotFoundError

class PokemonLoader(QThread):

    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, query: int | str):
        super().__init__()
        self.query = query

    def run(self):

        try:
            asyncio.run(self._load())

        except InternetConnectionError as e:
            self.error.emit("Error de conexión al cargar el Pokémon")

        except PokemonNotFoundError as e:
            self.error.emit("No se encontró ningún Pokémon con ese nombre o ID")

    async def _load(self):

        async with aiohttp.ClientSession() as session:
            api = APIPokemon()
            data = await api.fetch_pokemon(session, self.query)

            self.finished.emit(data)