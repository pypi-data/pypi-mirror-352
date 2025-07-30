"""
Core coffee shop finding functionality
"""

import requests
import os
import time
from typing import List, Optional, Set
from .models import CoffeeShop, Location, SearchResult
from .location import LocationService


class CoffeeShopFinder:
    """Main service for finding coffee shops"""
    
    # Common chain coffee shops to filter out
    CHAIN_COFFEE_SHOPS = {
        'starbucks', 'dunkin', 'dunkin donuts', 'mcdonalds', 'mcdonald\'s',
        'tim hortons', 'costa coffee', 'peet\'s coffee', 'caribou coffee',
        'panera bread', 'panera', 'subway', 'seven eleven', '7-eleven',
        'wawa', 'sheetz', 'circle k', 'speedway', 'shell', 'bp', 'exxon',
        'chevron', 'mobil', 'texaco', 'valero', 'marathon'
    }
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the coffee shop finder
        
        Args:
            api_key: Google Places API key (optional, can be set via environment)
        """
        self.api_key = api_key or os.getenv('GOOGLE_PLACES_API_KEY')
        self.location_service = LocationService()
        self.base_url = "https://places.googleapis.com/v1/places:searchText"
    
    def search_nearby(
        self, 
        location: Location, 
        radius_km: float = 2.0,
        max_results: int = 10,
        min_rating: Optional[float] = None,
        exclude_chains: bool = False,
        use_miles: bool = False,
        open_only: bool = False
    ) -> SearchResult:
        """
        Search for coffee shops near a location using pagination for comprehensive results
        
        Args:
            location: Location to search around
            radius_km: Search radius in kilometers (or miles if use_miles=True)
            max_results: Maximum number of results to return
            min_rating: Minimum rating filter (e.g., 4.0 for >4 stars)
            exclude_chains: Whether to exclude chain coffee shops
            use_miles: Whether radius is in miles instead of kilometers
            open_only: Whether to show only currently open coffee shops
            
        Returns:
            SearchResult containing found coffee shops
        """
        # Convert miles to km if needed
        search_radius_km = radius_km * 1.60934 if use_miles else radius_km
        
        coffee_shops = []
        
        if self.api_key:
            # Use pagination to get comprehensive results with larger search area
            # Search with 2x radius to ensure we don't miss edge cases, then filter precisely
            coffee_shops = self._search_with_pagination(location, search_radius_km * 2, max_results * 5)
        # If no API key, return empty results
        
        # Calculate distances first
        for shop in coffee_shops:
            shop.distance = self.location_service.calculate_distance(location, shop.location)
        
        # Filter by actual distance (this is the key fix!)
        coffee_shops = [shop for shop in coffee_shops if shop.distance and shop.distance <= search_radius_km]
        
        # Apply other filters
        if exclude_chains:
            coffee_shops = self._filter_chains(coffee_shops)
        
        if min_rating:
            coffee_shops = self._filter_by_rating(coffee_shops, min_rating)
        
        if open_only:
            coffee_shops = self._filter_open_only(coffee_shops)
        
        # Sort by rating (highest first), then by distance (closest first)
        # Handle None ratings by treating them as 0
        coffee_shops.sort(key=lambda x: (-(x.rating or 0), x.distance or float('inf')))
        
        return SearchResult(
            query_location=location,
            coffee_shops=coffee_shops[:max_results],
            total_results=len(coffee_shops),
            search_radius_km=radius_km,  # Keep original radius for display
            use_miles=use_miles
        )
    
    def _search_with_pagination(
        self, 
        location: Location, 
        radius_km: float, 
        target_results: int
    ) -> List[CoffeeShop]:
        """
        Search using pagination to get comprehensive results
        
        Args:
            location: Location to search around
            radius_km: Search radius in kilometers
            target_results: Target number of results to find
            
        Returns:
            Deduplicated list of CoffeeShop objects
        """
        all_shops = []
        seen_place_ids: Set[str] = set()
        next_page_token = None
        max_pages = 3  # Limit to prevent infinite loops (3 pages = up to 60 results)
        page_count = 0
        
        while page_count < max_pages and len(all_shops) < target_results:
            shops, next_page_token = self._search_google_places_page(
                location, radius_km, 20, next_page_token
            )
            
            # Add new unique shops
            for shop in shops:
                if shop.place_id and shop.place_id not in seen_place_ids:
                    all_shops.append(shop)
                    seen_place_ids.add(shop.place_id)
            
            page_count += 1
            
            # If no next page token, we've reached the end
            if not next_page_token:
                break
            
            # Small delay between requests to be respectful to the API
            if next_page_token:
                time.sleep(0.2)
        
        return all_shops
    
    def _filter_chains(self, coffee_shops: List[CoffeeShop]) -> List[CoffeeShop]:
        """
        Filter out chain coffee shops
        
        Args:
            coffee_shops: List of coffee shops to filter
            
        Returns:
            Filtered list without chain coffee shops
        """
        filtered_shops = []
        for shop in coffee_shops:
            shop_name_lower = shop.name.lower()
            is_chain = any(chain in shop_name_lower for chain in self.CHAIN_COFFEE_SHOPS)
            if not is_chain:
                filtered_shops.append(shop)
        return filtered_shops
    
    def _filter_by_rating(self, coffee_shops: List[CoffeeShop], min_rating: float) -> List[CoffeeShop]:
        """
        Filter coffee shops by minimum rating
        
        Args:
            coffee_shops: List of coffee shops to filter
            min_rating: Minimum rating threshold
            
        Returns:
            Filtered list with only highly-rated coffee shops
        """
        return [shop for shop in coffee_shops if shop.rating and shop.rating >= min_rating]
    
    def _filter_open_only(self, coffee_shops: List[CoffeeShop]) -> List[CoffeeShop]:
        """
        Filter to show only currently open coffee shops
        
        Args:
            coffee_shops: List of coffee shops to filter
            
        Returns:
            Filtered list with only currently open coffee shops
        """
        from datetime import datetime
        
        def is_shop_open(shop: CoffeeShop) -> bool:
            """Check if a coffee shop is currently open"""
            if not shop.opening_hours:
                return False  # If no hours info, assume closed
            
            # Get current day of week (0=Monday, 6=Sunday)
            current_day = datetime.now().weekday()
            day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            current_day_name = day_names[current_day]
            
            # Look for today's hours
            for hours in shop.opening_hours:
                if current_day_name.lower() in hours.lower():
                    # Extract just the hours part, removing the day name
                    hours_part = hours.split(": ", 1)
                    if len(hours_part) > 1:
                        hours_text = hours_part[1]
                    else:
                        hours_text = hours
                    
                    return self._is_currently_open(hours_text)
            
            # If no specific day found, check first entry
            if shop.opening_hours:
                return self._is_currently_open(shop.opening_hours[0])
            
            return False
        
        return [shop for shop in coffee_shops if is_shop_open(shop)]
    
    def _is_currently_open(self, hours_text: str) -> bool:
        """Check if a coffee shop is currently open based on hours text"""
        if not hours_text or hours_text.lower() in ['closed', 'hours n/a']:
            return False
        
        try:
            from datetime import datetime
            current_time = datetime.now()
            current_hour = current_time.hour
            current_minute = current_time.minute
            current_total_minutes = current_hour * 60 + current_minute
            
            # Handle common formats like "7:00 AM – 3:00 PM" or "7:30 AM – 2:30 PM"
            if '–' in hours_text or '-' in hours_text:
                # Split on either dash type
                separator = '–' if '–' in hours_text else '-'
                parts = hours_text.split(separator)
                if len(parts) == 2:
                    start_time_str = parts[0].strip()
                    end_time_str = parts[1].strip()
                    
                    # Parse start time
                    start_minutes = self._parse_time_to_minutes(start_time_str)
                    end_minutes = self._parse_time_to_minutes(end_time_str)
                    
                    if start_minutes is not None and end_minutes is not None:
                        # Handle overnight hours (like 10 PM - 2 AM)
                        if end_minutes < start_minutes:
                            # Overnight hours
                            return current_total_minutes >= start_minutes or current_total_minutes <= end_minutes
                        else:
                            # Normal hours
                            return start_minutes <= current_total_minutes <= end_minutes
            
            return False  # Default to closed if we can't parse
        except:
            return False  # Default to closed on any error
    
    def _parse_time_to_minutes(self, time_str: str) -> Optional[int]:
        """Parse time string like '7:30 AM' to minutes since midnight"""
        try:
            time_str = time_str.strip()
            
            # Handle AM/PM
            is_pm = 'PM' in time_str.upper()
            is_am = 'AM' in time_str.upper()
            
            # Remove AM/PM
            time_str = time_str.replace('AM', '').replace('PM', '').replace('am', '').replace('pm', '').strip()
            
            # Parse hour:minute
            if ':' in time_str:
                hour_str, minute_str = time_str.split(':')
                hour = int(hour_str)
                minute = int(minute_str)
            else:
                hour = int(time_str)
                minute = 0
            
            # Convert to 24-hour format
            if is_pm and hour != 12:
                hour += 12
            elif is_am and hour == 12:
                hour = 0
            
            return hour * 60 + minute
        except:
            return None
    
    def _search_google_places_page(
        self, 
        location: Location, 
        radius_km: float, 
        page_size: int,
        page_token: Optional[str] = None
    ) -> tuple[List[CoffeeShop], Optional[str]]:
        """
        Search a single page using Google Places API (New) Text Search
        
        Args:
            location: Location to search around
            radius_km: Search radius in kilometers
            page_size: Number of results per page
            page_token: Token for pagination
            
        Returns:
            Tuple of (list of CoffeeShop objects, next page token)
        """
        try:
            # Convert km to meters for Google Places API
            radius_m = int(radius_km * 1000)
            
            # Prepare request body for Text Search API
            request_body = {
                "textQuery": "coffee shops",
                "pageSize": min(page_size, 20),  # API limit is 20
                "locationBias": {
                    "circle": {
                        "center": {
                            "latitude": location.latitude,
                            "longitude": location.longitude
                        },
                        "radius": radius_m
                    }
                },
                "includedType": "cafe"
            }
            
            # Add page token if provided
            if page_token:
                request_body["pageToken"] = page_token
            
            # Prepare headers
            headers = {
                'Content-Type': 'application/json',
                'X-Goog-Api-Key': self.api_key,
                'X-Goog-FieldMask': 'places.displayName,places.formattedAddress,places.location,places.rating,places.priceLevel,places.nationalPhoneNumber,places.id,places.regularOpeningHours,nextPageToken'
            }
            
            response = requests.post(self.base_url, json=request_body, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            coffee_shops = []
            for place in data.get('places', []):
                shop = self._parse_google_place(place)
                if shop:
                    coffee_shops.append(shop)
            
            next_page_token = data.get('nextPageToken')
            return coffee_shops, next_page_token
            
        except Exception as e:
            print(f"Error searching Google Places: {e}")
            return [], None
    
    def _parse_google_place(self, place: dict) -> Optional[CoffeeShop]:
        """
        Parse a Google Places API (New) result into a CoffeeShop object
        
        Args:
            place: Google Places API place result
            
        Returns:
            CoffeeShop object or None if parsing fails
        """
        try:
            location_data = place.get('location', {})
            
            if not location_data:
                return None
            
            location = Location(
                latitude=location_data['latitude'],
                longitude=location_data['longitude']
            )
            
            # Extract display name
            display_name = place.get('displayName', {})
            name = display_name.get('text', 'Unknown') if display_name else 'Unknown'
            
            # Extract opening hours
            opening_hours = []
            regular_hours = place.get('regularOpeningHours', {})
            if regular_hours and 'weekdayDescriptions' in regular_hours:
                opening_hours = regular_hours['weekdayDescriptions']
            
            return CoffeeShop(
                name=name,
                address=place.get('formattedAddress', 'Address not available'),
                location=location,
                rating=place.get('rating'),
                price_level=self._convert_price_level(place.get('priceLevel')),
                phone=place.get('nationalPhoneNumber'),
                opening_hours=opening_hours,
                place_id=place.get('id')
            )
            
        except Exception as e:
            print(f"Error parsing place data: {e}")
            return None
    
    def _convert_price_level(self, price_level_str: Optional[str]) -> Optional[int]:
        """
        Convert new API price level string to integer
        
        Args:
            price_level_str: Price level string from new API
            
        Returns:
            Integer price level (1-4) or None
        """
        if not price_level_str:
            return None
        
        price_mapping = {
            'PRICE_LEVEL_INEXPENSIVE': 1,
            'PRICE_LEVEL_MODERATE': 2,
            'PRICE_LEVEL_EXPENSIVE': 3,
            'PRICE_LEVEL_VERY_EXPENSIVE': 4
        }
        
        return price_mapping.get(price_level_str) 