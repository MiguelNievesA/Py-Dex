############################################
# Py-Dex: A Simple Application to Explore  #
#          the Pokémon Universe            #
#                                          #
############################################
#                BETA 2.1                  #
############################################

###########################################
#            Modulo PyQt6                 #
###########################################
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
from PyQt6.uic import loadUi

###########################################
#         Modulos Secundarios             #
###########################################
import sys
import asyncio
import os
import aiohttp

###########################################
#           Modulos Internos              #
###########################################
from structure.threads.api_pokemon import APIPokemon

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

if __name__ == "__main__":
    
    # Depuremos si funciona APIPokemon
    async def main():
        async with aiohttp.ClientSession() as session:
            api_pokemon = APIPokemon()
            pokemon_data = await api_pokemon.fetch_pokemon(session, 1)  # Fetch data for Bulbasaur
            print(pokemon_data)

    asyncio.run(main())

