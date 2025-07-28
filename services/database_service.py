import sqlite3
import os
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import json

class CoffeeShopDatabaseService:
    def __init__(self, db_path: str = "database/coffee_shops.db"):
        """Initialize the database service"""
        self.db_path = db_path
        self.ensure_database_exists()
    
    def ensure_database_exists(self):
        """Create database and tables if they don't exist"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            # Read and execute schema
            schema_path = "database/schema.sql"
            if os.path.exists(schema_path):
                with open(schema_path, 'r') as f:
                    schema = f.read()
                    conn.executescript(schema)
                print(f"Database initialized: {self.db_path}")
            else:
                print(f"Schema file not found: {schema_path}")
    
    def get_connection(self):
        """Get a database connection with proper row factory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # This allows accessing columns by name
        return conn
    
    def insert_coffee_shop(self, shop_data: Dict) -> int:
        """Insert a new coffee shop and return its ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO coffee_shops 
                (name, address, city, state, zip_code, lat, lng, signature_drink, 
                 rating, description, phone, hours, website)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                shop_data['name'], shop_data['address'], shop_data['city'],
                shop_data.get('state', 'HI'), shop_data['zip_code'],
                shop_data['lat'], shop_data['lng'], shop_data.get('signature_drink'),
                shop_data.get('rating', 0.0), shop_data.get('description'),
                shop_data.get('phone'), shop_data.get('hours'), shop_data.get('website')
            ))
            return cursor.lastrowid
    
    def get_all_shops(self) -> List[Dict]:
        """Get all coffee shops"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM coffee_shops ORDER BY name")
            return [dict(row) for row in cursor.fetchall()]
    
    def get_shop_by_id(self, shop_id: int) -> Optional[Dict]:
        """Get a specific coffee shop by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM coffee_shops WHERE id = ?", (shop_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_shops_by_zip(self, zip_code: str) -> List[Dict]:
        """Get coffee shops by zip code"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM coffee_shops WHERE zip_code = ? ORDER BY rating DESC", (zip_code,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_shops_by_city(self, city: str) -> List[Dict]:
        """Get coffee shops by city"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM coffee_shops WHERE city LIKE ? ORDER BY rating DESC", (f"%{city}%",))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_shops_by_state(self, state: str) -> List[Dict]:
        """Get coffee shops by state"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM coffee_shops WHERE state = ? ORDER BY rating DESC", (state,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_shops_by_rating(self, min_rating: float = 0.0) -> List[Dict]:
        """Get coffee shops with minimum rating"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM coffee_shops WHERE rating >= ? ORDER BY rating DESC", (min_rating,))
            return [dict(row) for row in cursor.fetchall()]
    
    def search_shops(self, query: str) -> List[Dict]:
        """Search coffee shops by name, description, or city"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            search_term = f"%{query}%"
            cursor.execute("""
                SELECT * FROM coffee_shops 
                WHERE name LIKE ? OR description LIKE ? OR city LIKE ?
                ORDER BY rating DESC
            """, (search_term, search_term, search_term))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_shops_near_location(self, lat: float, lng: float, radius_miles: float = 10.0) -> List[Dict]:
        """Get coffee shops within a certain radius (approximate using bounding box)"""
        # Simple bounding box approximation (1 degree ≈ 69 miles)
        lat_range = radius_miles / 69.0
        lng_range = radius_miles / (69.0 * abs(lat) / 90.0)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT *, 
                       ((lat - ?) * (lat - ?) + (lng - ?) * (lng - ?)) as distance_sq
                FROM coffee_shops 
                WHERE lat BETWEEN ? AND ? AND lng BETWEEN ? AND ?
                ORDER BY distance_sq
            """, (lat, lat, lng, lng, lat - lat_range, lat + lat_range, lng - lng_range, lng + lng_range))
            
            shops = [dict(row) for row in cursor.fetchall()]
            # Filter by actual distance (more accurate)
            from geopy.distance import geodesic
            target_location = (lat, lng)
            
            for shop in shops:
                shop_location = (shop['lat'], shop['lng'])
                shop['distance'] = round(geodesic(target_location, shop_location).miles, 2)
            
            # Filter by actual radius and sort
            shops = [shop for shop in shops if shop['distance'] <= radius_miles]
            shops.sort(key=lambda x: x['distance'])
            
            return shops
    
    def get_statistics(self) -> Dict:
        """Get statistics about the coffee shop data"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Total shops
            cursor.execute("SELECT COUNT(*) FROM coffee_shops")
            total_shops = cursor.fetchone()[0]
            
            # Average rating
            cursor.execute("SELECT AVG(rating) FROM coffee_shops WHERE rating > 0")
            avg_rating = cursor.fetchone()[0] or 0.0
            
            # Top rated shops
            cursor.execute("SELECT name, rating FROM coffee_shops ORDER BY rating DESC LIMIT 3")
            top_rated = [dict(row) for row in cursor.fetchall()]
            
            # Shops by state
            cursor.execute("SELECT state, COUNT(*) FROM coffee_shops GROUP BY state")
            shops_by_state = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Shops by city
            cursor.execute("SELECT city, COUNT(*) FROM coffee_shops GROUP BY city ORDER BY COUNT(*) DESC LIMIT 10")
            shops_by_city = {row[0]: row[1] for row in cursor.fetchall()}
            
            return {
                'total_shops': total_shops,
                'avg_rating': round(avg_rating, 2),
                'top_rated': top_rated,
                'shops_by_state': shops_by_state,
                'shops_by_city': shops_by_city
            }
    
    def populate_hawaii_data(self):
        """Populate the database with Hawaii coffee shop data"""
        hawaii_shops = [
            {
                'name': 'Honolulu Coffee Company',
                'address': '1000 Bishop St',
                'city': 'Honolulu',
                'state': 'HI',
                'zip_code': '96813',
                'lat': 21.3069,
                'lng': -157.8583,
                'signature_drink': 'Hawaiian Latte',
                'rating': 4.5,
                'description': 'Premium coffee with Hawaiian flavors',
                'phone': '(808) 555-0101',
                'hours': '7:00 AM - 6:00 PM',
                'website': 'https://honolulucoffee.com'
            },
            {
                'name': 'Island Vintage Coffee',
                'address': '2301 Kalakaua Ave',
                'city': 'Honolulu',
                'state': 'HI',
                'zip_code': '96815',
                'lat': 21.2753,
                'lng': -157.8271,
                'signature_drink': 'Island Mocha',
                'rating': 4.7,
                'description': 'Organic coffee with island-inspired drinks',
                'phone': '(808) 555-0102',
                'hours': '6:00 AM - 8:00 PM',
                'website': 'https://islandvintagecoffee.com'
            },
            {
                'name': 'Morning Glass Coffee',
                'address': '2957 E Manoa Rd',
                'city': 'Honolulu',
                'state': 'HI',
                'zip_code': '96822',
                'lat': 21.2989,
                'lng': -157.8167,
                'signature_drink': 'Manu Manu',
                'rating': 4.6,
                'description': 'Artisanal coffee in a relaxed atmosphere',
                'phone': '(808) 555-0103',
                'hours': '6:30 AM - 5:00 PM',
                'website': 'https://morningglasscoffee.com'
            },
            {
                'name': 'Kona Coffee & Tea',
                'address': '74-5588 Palani Rd',
                'city': 'Kailua-Kona',
                'state': 'HI',
                'zip_code': '96740',
                'lat': 19.6345,
                'lng': -155.9889,
                'signature_drink': 'Kona Classic',
                'rating': 4.9,
                'description': 'Premium Kona coffee experience',
                'phone': '(808) 555-0109',
                'hours': '6:00 AM - 6:00 PM',
                'website': 'https://konacoffeeandtea.com'
            },
            {
                'name': 'Maui Coffee Roasters',
                'address': '444 Hana Hwy',
                'city': 'Kahului',
                'state': 'HI',
                'zip_code': '96732',
                'lat': 20.8847,
                'lng': -156.4543,
                'signature_drink': 'Maui Mokka',
                'rating': 4.5,
                'description': 'Local Maui coffee roaster',
                'phone': '(808) 555-0111',
                'hours': '6:00 AM - 6:00 PM',
                'website': 'https://mauicoffeeroasters.com'
            }
        ]
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            for shop in hawaii_shops:
                cursor.execute("""
                    INSERT OR REPLACE INTO coffee_shops 
                    (name, address, city, state, zip_code, lat, lng, signature_drink, 
                     rating, description, phone, hours, website)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    shop['name'], shop['address'], shop['city'], shop['state'],
                    shop['zip_code'], shop['lat'], shop['lng'], shop['signature_drink'],
                    shop['rating'], shop['description'], shop['phone'], shop['hours'], shop['website']
                ))
            
            print(f"Populated database with {len(hawaii_shops)} Hawaii coffee shops") 