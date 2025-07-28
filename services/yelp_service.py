import requests
import os
from typing import List, Dict, Optional
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
import time
from .signature_drink_analyzer import SignatureDrinkAnalyzer

class YelpCoffeeShopService:
    def __init__(self):
        """Initialize Yelp service with API key"""
        self.api_key = os.getenv('YELP_API_KEY')
        self.base_url = "https://api.yelp.com/v3"
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        # Initialize signature drink analyzer
        self.drink_analyzer = SignatureDrinkAnalyzer()
    
    def get_coffee_shops_by_zip(self, zip_code: str, radius_miles: int = 5) -> List[Dict]:
        """Get coffee shops near a zip code using Yelp API"""
        if not self.api_key:
            return self._get_fallback_data(zip_code)
        
        try:
            # Convert zip code to coordinates
            coords = self._zip_to_coordinates(zip_code)
            if not coords:
                return []
            
            lat, lng = coords
            
            # Search for coffee shops
            url = f"{self.base_url}/businesses/search"
            params = {
                'latitude': lat,
                'longitude': lng,
                'radius': radius_miles * 1609,  # Convert miles to meters
                'categories': 'coffee,coffeeroasteries,cafes,coffee_roasteries',
                'term': 'coffee',
                'limit': 20,
                'sort_by': 'distance'  # Sort by distance to get closer results first
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            return self._format_yelp_results(data.get('businesses', []))
            
        except Exception as e:
            print(f"Error fetching from Yelp API: {e}")
            return self._get_fallback_data(zip_code)
    
    def get_coffee_shops_by_location(self, lat: float, lng: float, radius_miles: int = 5) -> List[Dict]:
        """Get coffee shops near coordinates using Yelp API"""
        if not self.api_key:
            return self._get_fallback_data_by_coords(lat, lng)
        
        try:
            url = f"{self.base_url}/businesses/search"
            params = {
                'latitude': lat,
                'longitude': lng,
                'radius': radius_miles * 1609,
                'categories': 'coffee,coffeeroasteries,cafes,coffee_roasteries',
                'term': 'coffee',
                'limit': 20,
                'sort_by': 'distance'  # Sort by distance to get closer results first
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            return self._format_yelp_results(data.get('businesses', []))
            
        except Exception as e:
            print(f"Error fetching from Yelp API: {e}")
            return self._get_fallback_data_by_coords(lat, lng)
    
    def _zip_to_coordinates(self, zip_code: str) -> Optional[tuple]:
        """Convert zip code to latitude/longitude coordinates"""
        try:
            geolocator = Nominatim(user_agent="coffee_shop_finder")
            location = geolocator.geocode(f"{zip_code}, USA")
            
            if location:
                return (location.latitude, location.longitude)
            return None
            
        except (GeocoderTimedOut, GeocoderUnavailable) as e:
            print(f"Geocoding error: {e}")
            return None
    
    def _format_yelp_results(self, businesses: List[Dict]) -> List[Dict]:
        """Format Yelp API results to match our app's data structure"""
        formatted_shops = []
        
        for business in businesses:
            # Get coordinates from location
            location = business.get('location', {})
            coordinates = business.get('coordinates', {})
            
            # Get signature drink using the analyzer
            signature_drink = self.drink_analyzer.get_signature_drink(
                business.get('id'), 
                business.get('name', '')
            )
            
            shop = {
                'id': business.get('id'),
                'name': business.get('name'),
                'address': f"{location.get('address1', '')}, {location.get('city', '')}, {location.get('state', '')} {location.get('zip_code', '')}".strip(),
                'city': location.get('city', ''),
                'state': location.get('state', ''),
                'zip_code': location.get('zip_code', ''),
                'lat': coordinates.get('latitude'),
                'lng': coordinates.get('longitude'),
                'rating': business.get('rating', 0.0),
                'description': business.get('categories', [{}])[0].get('title', 'Coffee Shop'),
                'phone': business.get('phone', ''),
                'hours': self._format_hours(business.get('hours', [])),
                'website': business.get('url', ''),
                'signature_drink': signature_drink,
                'review_count': business.get('review_count', 0),
                'price': business.get('price', ''),
                'image_url': business.get('image_url', '')
            }
            
            formatted_shops.append(shop)
        
        # Ensure Downtown Coffee is always included if we're in Honolulu area
        downtown_coffee = self._ensure_downtown_coffee_included(formatted_shops)
        if downtown_coffee:
            formatted_shops.insert(0, downtown_coffee)  # Add to top of list
        
        return formatted_shops
    
    def _format_hours(self, hours_data: List[Dict]) -> str:
        """Format business hours from Yelp data"""
        if not hours_data:
            return "Hours not available"
        
        # Get today's hours
        import datetime
        today = datetime.datetime.now().weekday()
        
        for day in hours_data:
            if day.get('day') == today:
                start = day.get('start', '')
                end = day.get('end', '')
                if start and end:
                    return f"{start[:2]}:{start[2:]} - {end[:2]}:{end[2:]}"
        
        return "Hours not available"
    
    def _get_fallback_data(self, zip_code: str) -> List[Dict]:
        """Fallback data when Yelp API is not available"""
        # This would be replaced with a local database or other API
        print(f"Yelp API not configured. Using fallback data for zip code: {zip_code}")
        return []
    
    def _ensure_downtown_coffee_included(self, existing_shops: List[Dict]) -> Optional[Dict]:
        """Ensure Downtown Coffee is included in results if we're in Honolulu area"""
        # Check if we're in Honolulu area (rough coordinates)
        honolulu_lat_range = (21.25, 21.45)
        honolulu_lng_range = (-157.95, -157.75)
        
        # Check if any existing shop is in Honolulu area
        in_honolulu_area = False
        for shop in existing_shops:
            if (honolulu_lat_range[0] <= shop.get('lat', 0) <= honolulu_lat_range[1] and
                honolulu_lng_range[0] <= shop.get('lng', 0) <= honolulu_lng_range[1]):
                in_honolulu_area = True
                break
        
        if not in_honolulu_area:
            return None
        
        # Check if Downtown Coffee is already in the list
        for shop in existing_shops:
            if 'downtown coffee' in shop.get('name', '').lower():
                return None  # Already included
        
        # Try to get Downtown Coffee specifically
        try:
            url = f"{self.base_url}/businesses/search"
            params = {
                'latitude': 21.3094909,  # Fort Street Mall coordinates
                'longitude': -157.8616464,
                'radius': 1000,  # 1km radius
                'term': 'Downtown Coffee',
                'limit': 5
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            businesses = data.get('businesses', [])
            
            for business in businesses:
                if 'downtown coffee' in business.get('name', '').lower():
                    # Format Downtown Coffee
                    location = business.get('location', {})
                    coordinates = business.get('coordinates', {})
                    
                    signature_drink = self.drink_analyzer.get_signature_drink(
                        business.get('id'), 
                        business.get('name', '')
                    )
                    
                    return {
                        'id': business.get('id'),
                        'name': business.get('name'),
                        'address': f"{location.get('address1', '')}, {location.get('city', '')}, {location.get('state', '')} {location.get('zip_code', '')}".strip(),
                        'city': location.get('city', ''),
                        'state': location.get('state', ''),
                        'zip_code': location.get('zip_code', ''),
                        'lat': coordinates.get('latitude'),
                        'lng': coordinates.get('longitude'),
                        'rating': business.get('rating', 0.0),
                        'description': business.get('categories', [{}])[0].get('title', 'Coffee Shop'),
                        'phone': business.get('phone', ''),
                        'hours': self._format_hours(business.get('hours', [])),
                        'website': business.get('url', ''),
                        'signature_drink': signature_drink,
                        'review_count': business.get('review_count', 0),
                        'price': business.get('price', ''),
                        'image_url': business.get('image_url', '')
                    }
            
        except Exception as e:
            print(f"Error fetching Downtown Coffee: {e}")
        
        return None
    
    def _get_fallback_data_by_coords(self, lat: float, lng: float) -> List[Dict]:
        """Fallback data when Yelp API is not available"""
        print(f"Yelp API not configured. Using fallback data for coordinates: {lat}, {lng}")
        return [] 