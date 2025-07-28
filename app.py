from flask import Flask, render_template, jsonify, request
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Sample coffee shop data for Honolulu (96814)
HONOLULU_COFFEE_SHOPS = [
    {
        "id": 1,
        "name": "Honolulu Coffee Company",
        "address": "1000 Bishop St, Honolulu, HI 96813",
        "lat": 21.3069,
        "lng": -157.8583,
        "signature_drink": "Hawaiian Latte",
        "rating": 4.5,
        "description": "Premium coffee with Hawaiian flavors"
    },
    {
        "id": 2,
        "name": "Island Vintage Coffee",
        "address": "2301 Kalakaua Ave, Honolulu, HI 96815",
        "lat": 21.2753,
        "lng": -157.8271,
        "signature_drink": "Island Mocha",
        "rating": 4.7,
        "description": "Organic coffee with island-inspired drinks"
    },
    {
        "id": 3,
        "name": "Morning Glass Coffee",
        "address": "2957 E Manoa Rd, Honolulu, HI 96822",
        "lat": 21.2989,
        "lng": -157.8167,
        "signature_drink": "Manu Manu",
        "rating": 4.6,
        "description": "Artisanal coffee in a relaxed atmosphere"
    },
    {
        "id": 4,
        "name": "The Curb Kaimuki",
        "address": "1045 Koko Head Ave, Honolulu, HI 96816",
        "lat": 21.2847,
        "lng": -157.8025,
        "signature_drink": "Kaimuki Cold Brew",
        "rating": 4.4,
        "description": "Local favorite with great breakfast options"
    },
    {
        "id": 5,
        "name": "Coffee Gallery",
        "address": "1132 Bishop St, Honolulu, HI 96813",
        "lat": 21.3075,
        "lng": -157.8589,
        "signature_drink": "Gallery Blend",
        "rating": 4.3,
        "description": "Downtown coffee spot with art gallery"
    }
]

@app.route('/')
def index():
    """Main page with the coffee shop map"""
    return render_template('index.html')

@app.route('/api/coffee-shops')
def get_coffee_shops():
    """API endpoint to get coffee shops data"""
    zip_code = request.args.get('zip_code', '96814')
    
    # For now, return Honolulu data regardless of zip code
    # In Phase 2, we'll implement actual zip code filtering
    return jsonify({
        'zip_code': zip_code,
        'coffee_shops': HONOLULU_COFFEE_SHOPS
    })

@app.route('/api/coffee-shop/<int:shop_id>')
def get_coffee_shop_detail(shop_id):
    """API endpoint to get detailed information about a specific coffee shop"""
    shop = next((shop for shop in HONOLULU_COFFEE_SHOPS if shop['id'] == shop_id), None)
    
    if shop:
        # Add more detailed information
        shop_detail = shop.copy()
        shop_detail.update({
            'hours': '7:00 AM - 6:00 PM',
            'phone': '(808) 555-0123',
            'website': 'https://example.com',
            'reviews': [
                {'user': 'CoffeeLover', 'rating': 5, 'comment': 'Amazing signature drinks!'},
                {'user': 'LocalGuy', 'rating': 4, 'comment': 'Great atmosphere and friendly staff.'}
            ]
        })
        return jsonify(shop_detail)
    else:
        return jsonify({'error': 'Coffee shop not found'}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 