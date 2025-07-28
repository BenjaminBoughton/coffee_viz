from flask import Flask, render_template, jsonify, request
import json
import os
from dotenv import load_dotenv
from services.database_service import CoffeeShopDatabaseService

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize database service
db_service = CoffeeShopDatabaseService()

# Populate with Hawaii data on first run
@app.before_first_request
def initialize_data():
    """Initialize database with Hawaii data if empty"""
    stats = db_service.get_statistics()
    if stats['total_shops'] == 0:
        db_service.populate_hawaii_data()

@app.route('/')
def index():
    """Main page with the coffee shop map"""
    return render_template('index.html')

@app.route('/api/coffee-shops')
def get_coffee_shops():
    """API endpoint to get coffee shops data"""
    zip_code = request.args.get('zip_code', '')
    city = request.args.get('city', '')
    state = request.args.get('state', 'HI')  # Default to Hawaii for POC
    min_rating = request.args.get('min_rating', 0.0, type=float)
    search_query = request.args.get('search', '')
    
    # Get shops based on filters
    if search_query:
        shops = db_service.search_shops(search_query)
    elif city:
        shops = db_service.get_shops_by_city(city)
    elif zip_code:
        shops = db_service.get_shops_by_zip(zip_code)
    elif state:
        shops = db_service.get_shops_by_state(state)
    else:
        shops = db_service.get_all_shops()
    
    # Apply rating filter
    if min_rating > 0:
        shops = [shop for shop in shops if shop.get('rating', 0) >= min_rating]
    
    return jsonify({
        'zip_code': zip_code,
        'city': city,
        'state': state,
        'min_rating': min_rating,
        'search_query': search_query,
        'coffee_shops': shops,
        'total_count': len(shops)
    })

@app.route('/api/coffee-shop/<int:shop_id>')
def get_coffee_shop_detail(shop_id):
    """API endpoint to get detailed information about a specific coffee shop"""
    shop = db_service.get_shop_by_id(shop_id)
    
    if shop:
        # Add sample reviews (in Phase 2, these would come from a real API)
        shop['reviews'] = [
            {'user': 'CoffeeLover', 'rating': 5, 'comment': 'Amazing signature drinks!'},
            {'user': 'LocalGuy', 'rating': 4, 'comment': 'Great atmosphere and friendly staff.'},
            {'user': 'Tourist123', 'rating': 5, 'comment': 'Best coffee I had in Hawaii!'}
        ]
        return jsonify(shop)
    else:
        return jsonify({'error': 'Coffee shop not found'}), 404

@app.route('/api/statistics')
def get_statistics():
    """API endpoint to get coffee shop statistics"""
    stats = db_service.get_statistics()
    return jsonify(stats)

@app.route('/api/states')
def get_states():
    """API endpoint to get available states"""
    # For POC, focus on Hawaii but structure supports expansion
    states = [
        {'code': 'HI', 'name': 'Hawaii', 'cities': ['Honolulu', 'Kailua-Kona', 'Kahului']}
    ]
    return jsonify(states)

@app.route('/api/search')
def search_coffee_shops():
    """API endpoint to search coffee shops"""
    query = request.args.get('q', '')
    if not query:
        return jsonify({'coffee_shops': [], 'total_count': 0})
    
    shops = db_service.search_shops(query)
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
    radius = request.args.get('radius', 10.0, type=float)
    
    if lat is None or lng is None:
        return jsonify({'error': 'Latitude and longitude required'}), 400
    
    shops = db_service.get_shops_near_location(lat, lng, radius)
    return jsonify({
        'lat': lat,
        'lng': lng,
        'radius': radius,
        'coffee_shops': shops,
        'total_count': len(shops)
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000) 