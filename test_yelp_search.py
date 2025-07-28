import requests
import os
from dotenv import load_dotenv
from geopy.geocoders import Nominatim

load_dotenv()

def test_yelp_search():
    """Test Yelp search to debug why Downtown Coffee isn't showing up"""
    
    api_key = os.getenv('YELP_API_KEY')
    base_url = "https://api.yelp.com/v3"
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    # Get coordinates for Downtown Honolulu (Fort Street Mall area)
    geolocator = Nominatim(user_agent="coffee_shop_finder")
    location = geolocator.geocode("Fort Street Mall, Honolulu, HI")
    
    if location:
        lat, lng = location.latitude, location.longitude
        print(f"Searching around: {lat}, {lng}")
        print(f"Address: {location.address}")
        
        # Test different search strategies
        search_strategies = [
            {
                'name': 'Coffee category search',
                'params': {
                    'latitude': lat,
                    'longitude': lng,
                    'radius': 5000,  # 5km radius
                    'categories': 'coffee,coffeeroasteries,cafes',
                    'term': 'coffee',
                    'limit': 20,
                    'sort_by': 'rating'
                }
            },
            {
                'name': 'Broad search with coffee term',
                'params': {
                    'latitude': lat,
                    'longitude': lng,
                    'radius': 5000,
                    'term': 'coffee',
                    'limit': 20,
                    'sort_by': 'rating'
                }
            },
            {
                'name': 'Search for "Downtown Coffee" specifically',
                'params': {
                    'latitude': lat,
                    'longitude': lng,
                    'radius': 5000,
                    'term': 'Downtown Coffee',
                    'limit': 20
                }
            },
            {
                'name': 'Search for "downtown" in name',
                'params': {
                    'latitude': lat,
                    'longitude': lng,
                    'radius': 5000,
                    'term': 'downtown',
                    'limit': 20
                }
            },
            {
                'name': 'Restaurants and cafes',
                'params': {
                    'latitude': lat,
                    'longitude': lng,
                    'radius': 5000,
                    'categories': 'restaurants,cafes',
                    'limit': 20
                }
            }
        ]
        
        for strategy in search_strategies:
            print(f"\n=== Testing: {strategy['name']} ===")
            
            try:
                url = f"{base_url}/businesses/search"
                response = requests.get(url, headers=headers, params=strategy['params'])
                response.raise_for_status()
                
                data = response.json()
                businesses = data.get('businesses', [])
                
                print(f"Found {len(businesses)} businesses:")
                
                for i, business in enumerate(businesses[:10]):  # Show first 10
                    name = business.get('name', 'Unknown')
                    categories = [cat.get('title', '') for cat in business.get('categories', [])]
                    rating = business.get('rating', 0)
                    review_count = business.get('review_count', 0)
                    distance = business.get('distance', 0)
                    
                    print(f"  {i+1}. {name}")
                    print(f"     Categories: {', '.join(categories)}")
                    print(f"     Rating: {rating}, Reviews: {review_count}")
                    print(f"     Distance: {distance}m")
                    
                    # Check if this is Downtown Coffee
                    if 'downtown' in name.lower() and 'coffee' in name.lower():
                        print(f"     *** POTENTIAL MATCH: {name} ***")
                    
                    print()
                
            except Exception as e:
                print(f"Error with {strategy['name']}: {e}")
    
    else:
        print("Could not geocode Fort Street Mall")

if __name__ == "__main__":
    test_yelp_search() 