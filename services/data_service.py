import pandas as pd
import os
from typing import List, Dict, Optional
from geopy.distance import geodesic

class CoffeeShopDataService:
    def __init__(self, csv_path: str = "data/hawaii_coffee_shops.csv"):
        """Initialize the data service with CSV file path"""
        self.csv_path = csv_path
        self.data = None
        self.load_data()
    
    def load_data(self):
        """Load coffee shop data from CSV file"""
        try:
            if os.path.exists(self.csv_path):
                self.data = pd.read_csv(self.csv_path)
                # Convert lat/lng to float
                self.data['lat'] = pd.to_numeric(self.data['lat'], errors='coerce')
                self.data['lng'] = pd.to_numeric(self.data['lng'], errors='coerce')
                self.data['rating'] = pd.to_numeric(self.data['rating'], errors='coerce')
                print(f"Loaded {len(self.data)} coffee shops from {self.csv_path}")
            else:
                print(f"CSV file not found: {self.csv_path}")
                self.data = pd.DataFrame()
        except Exception as e:
            print(f"Error loading data: {e}")
            self.data = pd.DataFrame()
    
    def get_all_shops(self) -> List[Dict]:
        """Get all coffee shops"""
        if self.data.empty:
            return []
        return self.data.to_dict('records')
    
    def get_shops_by_zip(self, zip_code: str) -> List[Dict]:
        """Get coffee shops by zip code"""
        if self.data.empty:
            return []
        
        # Filter by zip code
        filtered_data = self.data[self.data['zip_code'] == zip_code]
        return filtered_data.to_dict('records')
    
    def get_shops_by_city(self, city: str) -> List[Dict]:
        """Get coffee shops by city"""
        if self.data.empty:
            return []
        
        # Filter by city (case insensitive)
        filtered_data = self.data[self.data['city'].str.lower() == city.lower()]
        return filtered_data.to_dict('records')
    
    def get_shops_by_rating(self, min_rating: float = 0.0) -> List[Dict]:
        """Get coffee shops with minimum rating"""
        if self.data.empty:
            return []
        
        filtered_data = self.data[self.data['rating'] >= min_rating]
        return filtered_data.to_dict('records')
    
    def get_shop_by_id(self, shop_id: int) -> Optional[Dict]:
        """Get a specific coffee shop by ID"""
        if self.data.empty:
            return None
        
        shop_data = self.data[self.data['id'] == shop_id]
        if not shop_data.empty:
            return shop_data.iloc[0].to_dict()
        return None
    
    def search_shops(self, query: str) -> List[Dict]:
        """Search coffee shops by name or description"""
        if self.data.empty:
            return []
        
        # Search in name and description columns
        mask = (
            self.data['name'].str.contains(query, case=False, na=False) |
            self.data['description'].str.contains(query, case=False, na=False) |
            self.data['city'].str.contains(query, case=False, na=False)
        )
        filtered_data = self.data[mask]
        return filtered_data.to_dict('records')
    
    def get_shops_near_location(self, lat: float, lng: float, radius_miles: float = 10.0) -> List[Dict]:
        """Get coffee shops within a certain radius of a location"""
        if self.data.empty:
            return []
        
        nearby_shops = []
        target_location = (lat, lng)
        
        for _, shop in self.data.iterrows():
            if pd.notna(shop['lat']) and pd.notna(shop['lng']):
                shop_location = (shop['lat'], shop['lng'])
                distance = geodesic(target_location, shop_location).miles
                
                if distance <= radius_miles:
                    shop_dict = shop.to_dict()
                    shop_dict['distance'] = round(distance, 2)
                    nearby_shops.append(shop_dict)
        
        # Sort by distance
        nearby_shops.sort(key=lambda x: x['distance'])
        return nearby_shops
    
    def get_island_shops(self, island: str) -> List[Dict]:
        """Get coffee shops by island (Hawaii, Maui, Oahu, Kauai)"""
        island_mapping = {
            'hawaii': ['Kailua-Kona', 'Hilo', 'Waimea', 'Holualoa'],
            'maui': ['Kahului', 'Wailuku', 'Lahaina', 'Kihei'],
            'oahu': ['Honolulu', 'Kailua', 'Haleiwa', 'Wahiawa'],
            'kauai': ['Kapaa', 'Lihue', 'Kalaheo', 'Hanalei']
        }
        
        if island.lower() not in island_mapping:
            return []
        
        cities = island_mapping[island.lower()]
        filtered_data = self.data[self.data['city'].isin(cities)]
        return filtered_data.to_dict('records')
    
    def get_statistics(self) -> Dict:
        """Get statistics about the coffee shop data"""
        if self.data.empty:
            return {}
        
        stats = {
            'total_shops': len(self.data),
            'islands': self.data['city'].value_counts().to_dict(),
            'avg_rating': round(self.data['rating'].mean(), 2),
            'top_rated': self.data.nlargest(3, 'rating')[['name', 'rating']].to_dict('records'),
            'cities': self.data['city'].unique().tolist()
        }
        return stats 