"""
EspressoNow - Find specialty coffee shops near you.
"""

__version__ = "0.4.1"
__author__ = "Ethan Carter"
__email__ = "ethanqcarter@gmail.com"

from .core import CoffeeShopFinder
from .location import LocationService
from .models import CoffeeShop, Location, SearchResult

__all__ = [
    "CoffeeShopFinder",
    "LocationService", 
    "CoffeeShop",
    "Location",
    "SearchResult"
]
