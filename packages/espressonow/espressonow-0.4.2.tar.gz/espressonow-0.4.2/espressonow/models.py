"""
Data models for EspressoNow
"""

from typing import Optional, List
from pydantic import BaseModel, Field


class Location(BaseModel):
    """Represents a geographic location"""
    latitude: float = Field(..., description="Latitude coordinate")
    longitude: float = Field(..., description="Longitude coordinate")
    address: Optional[str] = Field(None, description="Human-readable address")
    city: Optional[str] = Field(None, description="City name")
    country: Optional[str] = Field(None, description="Country name")


class CoffeeShop(BaseModel):
    """Represents a coffee shop"""
    name: str = Field(..., description="Name of the coffee shop")
    address: str = Field(..., description="Street address")
    location: Location = Field(..., description="Geographic location")
    rating: Optional[float] = Field(None, description="Rating (0-5)")
    price_level: Optional[int] = Field(None, description="Price level (1-4)")
    phone: Optional[str] = Field(None, description="Phone number")
    website: Optional[str] = Field(None, description="Website URL")
    opening_hours: Optional[List[str]] = Field(None, description="Opening hours")
    distance: Optional[float] = Field(None, description="Distance from user in km")
    place_id: Optional[str] = Field(None, description="Unique place identifier")
    
    class Config:
        json_encoders = {
            float: lambda v: round(v, 2) if v else None
        }


class SearchResult(BaseModel):
    """Represents search results"""
    query_location: Location = Field(..., description="Location that was searched")
    coffee_shops: List[CoffeeShop] = Field(..., description="List of found coffee shops")
    total_results: int = Field(..., description="Total number of results")
    search_radius_km: float = Field(..., description="Search radius in kilometers")
    use_miles: bool = Field(default=False, description="Whether to display distances in miles") 