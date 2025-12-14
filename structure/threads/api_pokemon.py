import aiohttp
import asyncio
import sys
from structure.custom_exceptions import InternetConnectionError

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

class APIPokemon:
    async def fetch_data(self, session, url):
        """Makes a GET request to a given URL and returns the JSON data."""

        try:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                
                else:
                    return {"error": f"{response.status}"}
        
        except aiohttp.ClientConnectionError:
            raise InternetConnectionError("No internet connection available.")


    async def fetch_pokemon(self, session, pokemon):
        """Fetches basic data about a Pokémon """

        url = f"https://pokeapi.co/api/v2/pokemon/{pokemon}/"

        pokemon_data = await self.fetch_data(session, url)
        
        # Types
        types_urls = [type_["type"]["url"] for type_ in pokemon_data["types"]]
        types_tasks = [self.fetch_data(session, type_url) for type_url in types_urls]
        types_data = await asyncio.gather(*types_tasks)
        types = [type_data["name"] for type_data in types_data]

        # Description
        specie_url = pokemon_data["species"]["url"]
        descriptions = await self.fetch_data(session, specie_url)

        # Gender
        gender_task = self.fetch_data(session, specie_url)
        gender = await asyncio.gather(gender_task)

        # Stats base
        stats_task = self.fetch_data(session, url)
        stats = await asyncio.gather(stats_task)
        stats_dict = {stat["stat"]["name"]: stat["base_stat"] for stat in stats[0]["stats"]}

        # Abilities

        hidden_abilities_urls = [
            ability["ability"]["url"] for ability in pokemon_data["abilities"] if ability["is_hidden"]
        ]

        hidden_abilities_tasks = [self.fetch_data(session, hidden_ability_url) for hidden_ability_url in hidden_abilities_urls]
        hidden_abilities = await asyncio.gather(*hidden_abilities_tasks)

        abilities_urls = [abilitie["ability"]["url"] for abilitie in pokemon_data["abilities"] if abilitie["is_hidden"] == False]
        ability_tasks = [self.fetch_data(session, ability_url) for ability_url in abilities_urls]
        abilities = await asyncio.gather(*ability_tasks)

        return {

            "name": pokemon_data["name"],
            "id": pokemon_data["id"],
            "height": pokemon_data["height"],
            "weight": pokemon_data["weight"],
            "types": [type_url["names"][5]["name"].lower() for type_url in types_data],
            "abilities": [ability["names"][5]["name"] for ability in abilities],
            "hidden_ability": [hidden_ability["names"][5]["name"] for hidden_ability in hidden_abilities],
            "description": (descriptions["flavor_text_entries"][26]["flavor_text"], descriptions["flavor_text_entries"][34]["flavor_text"]),
            "gender_ratio": gender[0]["gender_rate"],
            "base_stats": stats_dict
        }
    

