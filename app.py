from flask import Flask, render_template, jsonify, request
import json
import os
from dotenv import load_dotenv
from services.yelp_service import YelpCoffeeShopService

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize Yelp service
yelp_service = YelpCoffeeShopService()

@app.route('/')
def index():
    """Main page with the coffee shop map"""
    return render_template('index.html')

@app.route('/api/coffee-shops')
def get_coffee_shops():
    """API endpoint to get coffee shops data dynamically"""
    zip_code = request.args.get('zip_code', '')
    lat = request.args.get('lat', type=float)
    lng = request.args.get('lng', type=float)
    radius_miles = request.args.get('radius', 5, type=int)
    min_rating = request.args.get('min_rating', 0.0, type=float)
    
    # Get shops based on location
    if lat and lng:
        # Search by coordinates
        shops = yelp_service.get_coffee_shops_by_location(lat, lng, radius_miles)
    elif zip_code:
        # Search by zip code
        shops = yelp_service.get_coffee_shops_by_zip(zip_code, radius_miles)
    else:
        # Default to Honolulu area if no location specified
        shops = yelp_service.get_coffee_shops_by_location(21.3069, -157.8583, radius_miles)
    
    # Apply rating filter
    if min_rating > 0:
        shops = [shop for shop in shops if shop.get('rating', 0) >= min_rating]
    
    return jsonify({
        'zip_code': zip_code,
        'lat': lat,
        'lng': lng,
        'radius_miles': radius_miles,
        'min_rating': min_rating,
        'coffee_shops': shops,
        'total_count': len(shops)
    })

@app.route('/api/coffee-shop/<shop_id>')
def get_coffee_shop_detail(shop_id):
    """API endpoint to get detailed information about a specific coffee shop"""
    # For now, return basic info. In Phase 2, we'd fetch from Yelp API
    return jsonify({
        'id': shop_id,
        'name': 'Coffee Shop Details',
        'description': 'Detailed information would be fetched from Yelp API',
        'reviews': [
            {'user': 'CoffeeLover', 'rating': 5, 'comment': 'Great coffee!'},
            {'user': 'LocalGuy', 'rating': 4, 'comment': 'Nice atmosphere.'}
        ]
    })

@app.route('/api/search')
def search_coffee_shops():
    """API endpoint to search coffee shops by location"""
    query = request.args.get('q', '')
    if not query:
        return jsonify({'coffee_shops': [], 'total_count': 0})
    
    # Try to interpret query as zip code or location
    try:
        # If it looks like a zip code, search by zip
        if query.isdigit() and len(query) == 5:
            shops = yelp_service.get_coffee_shops_by_zip(query)
        else:
            # Otherwise, try to geocode the query
            from geopy.geocoders import Nominatim
            geolocator = Nominatim(user_agent="coffee_shop_finder")
            location = geolocator.geocode(f"{query}, USA")
            
            if location:
                shops = yelp_service.get_coffee_shops_by_location(location.latitude, location.longitude)
            else:
                shops = []
    except Exception as e:
        print(f"Search error: {e}")
        shops = []
    
    return jsonify({
        'query': query,
        'coffee_shops': shops,
        'total_count': len(shops)
    })

@app.route('/api/nearby')
def get_nearby_shops():
    """API endpoint to get shops near a location"""
    lat = request.args.get('lat', type=float)
    lng = request.args.get('lng', type=float)
    radius = request.args.get('radius', 5, type=int)
    
    if lat is None or lng is None:
        return jsonify({'error': 'Latitude and longitude required'}), 400
    
    shops = yelp_service.get_coffee_shops_by_location(lat, lng, radius)
    return jsonify({
        'lat': lat,
        'lng': lng,
        'radius': radius,
        'coffee_shops': shops,
        'total_count': len(shops)
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000) 