#################################
# Custom Exceptions for Py-Dex  #
#################################

# Exception raised when a error connection to internet
class InternetConnectionError(Exception):
    """Raised when there is no internet connection."""
    pass

class PokemonNotFoundError(Exception):
    pass