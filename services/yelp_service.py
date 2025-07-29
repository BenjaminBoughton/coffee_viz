import requests
import os
import re
from typing import List, Dict, Optional
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
import time
from .nlp_summary_service import NLPSummaryService

class YelpCoffeeShopService:
    def __init__(self):
        """Initialize Yelp service with API key"""
        self.api_key = os.getenv('YELP_API_KEY')
        self.base_url = "https://api.yelp.com/v3"
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        # Initialize NLP summary service
        self.nlp_service = NLPSummaryService()
        
        # Improved filtering criteria based on analysis
        self.filtering_config = {
            'primary_categories': ['coffee', 'coffeeroasteries', 'cafes'],
            'excluded_categories': ['restaurants', 'bakeries', 'breakfast_brunch', 'sandwiches', 'pizza', 'burgers', 'food'],
            'name_keywords': ['coffee', 'cafe', 'brew', 'drip', 'roast', 'espresso', 'latte', 'speciality', 'specialty'],
            'min_review_count': 80,  # Updated to 80 reviews minimum
            'min_rating': 4.2,  # Based on target shops analysis
            'price_range': ['$', '$$', '$$$'],  # Exclude $$$$ (too expensive)
            'business_name_patterns': [
                r'\bcoffee\b',
                r'\bcafe\b',
                r'\bbrew\b',
                r'\bdrip\b',
                r'\broast\b',
                r'\bespresso\b',
                r'\blatte\b',
                r'\bspeciality\b',
                r'\bspecialty\b'
            ]
        }
    
    def get_coffee_shops_by_zip(self, zip_code: str, radius_miles: int = 5) -> List[Dict]:
        """Get coffee shops near a zip code using Yelp API with improved filtering"""
        if not self.api_key:
            return self._get_fallback_data(zip_code)
        
        try:
            # Convert location to coordinates
            coords = self._location_to_coordinates(zip_code)
            if not coords:
                return []
            
            lat, lng = coords
            
            # Search for coffee shops with improved criteria
            url = f"{self.base_url}/businesses/search"
            params = {
                'latitude': lat,
                'longitude': lng,
                'radius': radius_miles * 1609,  # Convert miles to meters
                'categories': ','.join(self.filtering_config['primary_categories']),
                'term': 'coffee',
                'limit': 50,  # Increased limit to get more candidates for filtering
                'sort_by': 'rating'  # Sort by rating to prioritize better shops
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            businesses = data.get('businesses', [])
            
            
            
            # Apply improved filtering
            filtered_businesses = self._apply_improved_filtering(businesses, lat, lng, radius_miles)
            
            return self._format_yelp_results(filtered_businesses)
            
        except Exception as e:
            print(f"Error fetching from Yelp API: {e}")
            return self._get_fallback_data(zip_code)
    
    def get_coffee_shops_by_location_query(self, location_query: str, radius_miles: int = 5) -> List[Dict]:
        """Get coffee shops near a location (zip code or place name) using Yelp API with improved filtering"""
        if not self.api_key:
            return self._get_fallback_data(location_query)
        
        try:
            # First try to geocode the location
            coords = self._location_to_coordinates(location_query)
            if coords:
                lat, lng = coords
                return self.get_coffee_shops_by_location(lat, lng, radius_miles)
            else:
                print(f"Could not geocode location: {location_query}")
                return []
            
        except Exception as e:
            print(f"Error fetching from Yelp API: {e}")
            return self._get_fallback_data(location_query)
    
    def get_coffee_shops_by_location(self, lat: float, lng: float, radius_miles: int = 5) -> List[Dict]:
        """Get coffee shops near coordinates using Yelp API with improved filtering"""
        if not self.api_key:
            return self._get_fallback_data_by_coords(lat, lng)
        
        try:
            url = f"{self.base_url}/businesses/search"
            params = {
                'latitude': lat,
                'longitude': lng,
                'radius': radius_miles * 1609,
                'categories': ','.join(self.filtering_config['primary_categories']),
                'term': 'coffee',
                'limit': 50,  # Increased limit to get more candidates for filtering
                'sort_by': 'rating'  # Sort by rating to prioritize better shops
            }
            

            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            businesses = data.get('businesses', [])
            

            
            # Apply improved filtering
            filtered_businesses = self._apply_improved_filtering(businesses, lat, lng, radius_miles)
            
            return self._format_yelp_results(filtered_businesses)
            
        except Exception as e:
            print(f"Error fetching from Yelp API: {e}")
            return self._get_fallback_data_by_coords(lat, lng)
    
    def _apply_improved_filtering(self, businesses: List[Dict], search_lat: float = None, search_lng: float = None, radius_miles: int = 5) -> List[Dict]:
        """Apply improved filtering criteria to Yelp results"""
        filtered_businesses = []
        
        for business in businesses:
            # Skip if doesn't meet minimum thresholds
            if business.get('review_count', 0) < self.filtering_config['min_review_count']:
                continue
                
            if business.get('rating', 0) < self.filtering_config['min_rating']:
                continue
            
            # Calculate distance from search center to business location
            # This is more reliable than relying on Yelp's distance field
            business_lat = business.get('coordinates', {}).get('latitude')
            business_lng = business.get('coordinates', {}).get('longitude')
            
            if business_lat and business_lng and search_lat and search_lng:
                # Calculate distance using Haversine formula
                from math import radians, cos, sin, asin, sqrt
                
                # Convert to radians
                lat1, lon1 = radians(search_lat), radians(search_lng)
                lat2, lon2 = radians(business_lat), radians(business_lng)
                
                # Haversine formula
                dlat = lat2 - lat1
                dlon = lon2 - lon1
                a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
                c = 2 * asin(sqrt(a))
                distance_miles = 3956 * c  # Earth's radius in miles
                
                if distance_miles > radius_miles:
                    continue
            
            # Skip if price is too expensive
            price = business.get('price', '')
            if price and price not in self.filtering_config['price_range']:
                continue
            
            # Check categories - exclude unwanted categories
            categories = business.get('categories', [])
            category_aliases = [cat.get('alias', '') for cat in categories]
            
            # Skip if has excluded categories
            has_excluded_category = any(cat in self.filtering_config['excluded_categories'] 
                                      for cat in category_aliases)
            if has_excluded_category:
                continue
            
            # Check if has at least one primary category
            has_primary_category = any(cat in self.filtering_config['primary_categories'] 
                                     for cat in category_aliases)
            if not has_primary_category:
                continue
            
            # Name-based filtering - prioritize businesses with coffee-related keywords
            business_name = business.get('name', '').lower()
            has_coffee_keyword = any(keyword in business_name 
                                   for keyword in self.filtering_config['name_keywords'])
            
            # If no coffee keywords in name, check if it's still a good match
            if not has_coffee_keyword:
                # Only include if it has strong coffee-related categories
                strong_coffee_categories = ['coffeeroasteries', 'coffee']
                has_strong_category = any(cat in strong_coffee_categories 
                                        for cat in category_aliases)
                if not has_strong_category:
                    continue
            
            # Additional filtering: check for specific patterns in name
            name_patterns = self.filtering_config['business_name_patterns']
            has_name_pattern = any(re.search(pattern, business_name, re.IGNORECASE) 
                                 for pattern in name_patterns)
            
            # If no name pattern but has good categories and rating, still include
            if not has_name_pattern and not has_coffee_keyword:
                # Only include if it has very high rating and good review count
                if (business.get('rating', 0) < 4.5 or 
                    business.get('review_count', 0) < 150):
                    continue
            
            filtered_businesses.append(business)
        
        # Sort by rating (highest first) and limit to top 20
        filtered_businesses.sort(key=lambda x: (x.get('rating', 0), x.get('review_count', 0)), reverse=True)
        return filtered_businesses[:20]
    
    def _location_to_coordinates(self, location_query: str) -> Optional[tuple]:
        """Convert location query (zip code or place name) to latitude/longitude coordinates"""
        try:
            geolocator = Nominatim(user_agent="coffee_shop_finder")
            
            # Try different geocoding strategies
            location = None
            
            # First try as-is
            location = geolocator.geocode(location_query)
            
            # If that fails and it looks like a zip code, try with USA
            if not location and location_query.isdigit() and len(location_query) == 5:
                location = geolocator.geocode(f"{location_query}, USA")
            
            # If still no result, try with common location suffixes
            if not location:
                for suffix in [", HI", ", Hawaii", ", USA"]:
                    location = geolocator.geocode(f"{location_query}{suffix}")
                    if location:
                        break
            
            if location:
                print(f"Geocoded '{location_query}' to: {location.latitude}, {location.longitude}")
                return (location.latitude, location.longitude)
            
            print(f"Could not geocode location: {location_query}")
            return None
            
        except (GeocoderTimedOut, GeocoderUnavailable) as e:
            print(f"Geocoding error: {e}")
            return None
    
    def _zip_to_coordinates(self, zip_code: str) -> Optional[tuple]:
        """Convert zip code to latitude/longitude coordinates (legacy method)"""
        return self._location_to_coordinates(zip_code)
    
    def _format_yelp_results(self, businesses: List[Dict]) -> List[Dict]:
        """Format Yelp API results to match our app's data structure"""
        formatted_shops = []
        
        for business in businesses:
            # Get coordinates from location
            location = business.get('location', {})
            coordinates = business.get('coordinates', {})
            
            # Generate NLP summary for the shop
            nlp_summary = self.nlp_service.generate_shop_summary(business)
            
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
                'website': business.get('website_url', ''),  # Business's own website
                'yelp_url': business.get('url', ''),  # Yelp page URL
                'nlp_summary': nlp_summary,
                'review_count': business.get('review_count', 0),
                'price': business.get('price', ''),
                'image_url': business.get('image_url', '')
            }
            
            formatted_shops.append(shop)
        
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
    
    def _get_fallback_data_by_coords(self, lat: float, lng: float) -> List[Dict]:
        """Fallback data when Yelp API is not available"""
        print(f"Yelp API not configured. Using fallback data for coordinates: {lat}, {lng}")
        return [] 