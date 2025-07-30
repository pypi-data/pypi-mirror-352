"""
Location detection and handling services
"""

import geocoder
from typing import Optional, Tuple
from .models import Location


class LocationService:
    """Service for handling location detection and operations"""
    
    def __init__(self):
        self.current_location: Optional[Location] = None
    
    def get_current_location(self) -> Optional[Location]:
        """
        Get the current location using IP geolocation
        
        Returns:
            Location object or None if detection fails
        """
        try:
            # Try IP-based geolocation first
            g = geocoder.ip('me')
            if g.ok:
                self.current_location = Location(
                    latitude=g.latlng[0],
                    longitude=g.latlng[1],
                    address=g.address,
                    city=g.city,
                    country=g.country
                )
                return self.current_location
        except Exception as e:
            print(f"Error detecting location: {e}")
        
        return None
    
    def get_location_from_address(self, address: str) -> Optional[Location]:
        """
        Get location coordinates from an address string
        
        Args:
            address: Address string to geocode
            
        Returns:
            Location object or None if geocoding fails
        """
        try:
            g = geocoder.osm(address)
            if g.ok:
                return Location(
                    latitude=g.latlng[0],
                    longitude=g.latlng[1],
                    address=g.address,
                    city=g.city,
                    country=g.country
                )
        except Exception as e:
            print(f"Error geocoding address '{address}': {e}")
        
        return None
    
    def calculate_distance(self, loc1: Location, loc2: Location) -> float:
        """
        Calculate distance between two locations using Haversine formula
        
        Args:
            loc1: First location
            loc2: Second location
            
        Returns:
            Distance in kilometers
        """
        import math
        
        # Convert latitude and longitude from degrees to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [
            loc1.latitude, loc1.longitude, 
            loc2.latitude, loc2.longitude
        ])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Radius of earth in kilometers
        r = 6371
        
        return c * r
    
    def format_location(self, location: Location) -> str:
        """
        Format location for display
        
        Args:
            location: Location to format
            
        Returns:
            Formatted location string
        """
        if location.address:
            return location.address
        elif location.city and location.country:
            return f"{location.city}, {location.country}"
        else:
            return f"{location.latitude:.4f}, {location.longitude:.4f}" 