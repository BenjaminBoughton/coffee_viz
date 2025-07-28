import re
import json
from typing import Dict, List, Optional, Tuple
from collections import Counter
import requests
import os
from dotenv import load_dotenv

load_dotenv()

class SignatureDrinkAnalyzer:
    def __init__(self):
        """Initialize the signature drink analyzer"""
        self.api_key = os.getenv('YELP_API_KEY')
        self.base_url = "https://api.yelp.com/v3"
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        # Common coffee drink keywords and their variations
        self.drink_keywords = {
            'latte': ['latte', 'cafe latte', 'vanilla latte', 'caramel latte'],
            'cappuccino': ['cappuccino', 'cap', 'capp'],
            'espresso': ['espresso', 'shot', 'double shot'],
            'americano': ['americano', 'long black'],
            'mocha': ['mocha', 'chocolate mocha'],
            'macchiato': ['macchiato', 'caramel macchiato'],
            'cold brew': ['cold brew', 'cold brew coffee'],
            'pour over': ['pour over', 'pour-over', 'drip coffee'],
            'flat white': ['flat white'],
            'cortado': ['cortado'],
            'ristretto': ['ristretto'],
            'lungo': ['lungo'],
            'affogato': ['affogato'],
            'frappuccino': ['frappuccino', 'frappe'],
            'iced coffee': ['iced coffee', 'cold coffee'],
            'nitro': ['nitro', 'nitro cold brew'],
            'bulletproof': ['bulletproof', 'butter coffee'],
            'dalgona': ['dalgona', 'whipped coffee'],
            'vietnamese': ['vietnamese coffee', 'ca phe sua da'],
            'turkish': ['turkish coffee'],
            'greek': ['greek coffee'],
            'ethiopian': ['ethiopian coffee'],
            'colombian': ['colombian coffee'],
            'guatemalan': ['guatemalan coffee'],
            'sumatra': ['sumatra coffee'],
            'kenya': ['kenya coffee'],
            'ethiopia': ['ethiopia coffee'],
            'house blend': ['house blend', 'house coffee'],
            'signature': ['signature', 'signature drink', 'specialty']
        }
        
        # Cache for business details to avoid repeated API calls
        self.business_cache = {}
    
    def get_signature_drink(self, business_id: str, business_name: str = "") -> str:
        """
        Determine the signature drink for a coffee shop
        Uses multiple strategies to find the most likely signature drink
        """
        try:
            print(f"Analyzing signature drink for: {business_name} (ID: {business_id})")
            
            # Strategy 1: Check business details (cheapest - no additional API call)
            drink_from_details = self._analyze_business_details(business_id)
            if drink_from_details:
                print(f"Found drink from details: {drink_from_details}")
                return drink_from_details
            
            # Strategy 2: Check if we have cached business info
            if business_id in self.business_cache:
                drink_from_cache = self._analyze_cached_business(business_id)
                if drink_from_cache:
                    print(f"Found drink from cache: {drink_from_cache}")
                    return drink_from_cache
            
            # Strategy 3: Get business details from Yelp API (1 request)
            business_details = self._get_business_details(business_id)
            if business_details:
                drink_from_api = self._analyze_business_data(business_details)
                if drink_from_api:
                    print(f"Found drink from API: {drink_from_api}")
                    return drink_from_api
            
            # Strategy 4: Analyze reviews (most expensive - 1 additional request)
            # Only do this for highly-rated shops to conserve API calls
            if self._should_analyze_reviews(business_details):
                drink_from_reviews = self._analyze_reviews(business_id)
                if drink_from_reviews:
                    print(f"Found drink from reviews: {drink_from_reviews}")
                    return drink_from_reviews
            
            # Fallback based on business name
            fallback_drink = self._get_fallback_drink(business_name)
            print(f"Using fallback drink: {fallback_drink}")
            return fallback_drink
            
        except Exception as e:
            print(f"Error analyzing signature drink for {business_id}: {e}")
            fallback_drink = self._get_fallback_drink(business_name)
            print(f"Using error fallback drink: {fallback_drink}")
            return fallback_drink
    
    def _analyze_business_details(self, business_id: str) -> Optional[str]:
        """Analyze business details from the search results (no additional API call)"""
        # This would be called with business data we already have
        # For now, return None to try other strategies
        return None
    
    def _analyze_cached_business(self, business_id: str) -> Optional[str]:
        """Analyze cached business data"""
        business_data = self.business_cache.get(business_id, {})
        
        # Check business name for drink indicators
        name = business_data.get('name', '').lower()
        for drink_type, keywords in self.drink_keywords.items():
            for keyword in keywords:
                if keyword in name:
                    return self._format_drink_name(drink_type)
        
        # Check categories
        categories = business_data.get('categories', [])
        for category in categories:
            title = category.get('title', '').lower()
            if 'espresso' in title or 'coffee' in title:
                return "House Espresso"
        
        return None
    
    def _get_business_details(self, business_id: str) -> Optional[Dict]:
        """Get detailed business information from Yelp API"""
        try:
            url = f"{self.base_url}/businesses/{business_id}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            business_data = response.json()
            # Cache the business data
            self.business_cache[business_id] = business_data
            return business_data
            
        except Exception as e:
            print(f"Error getting business details: {e}")
            return None
    
    def _analyze_business_data(self, business_data: Dict) -> Optional[str]:
        """Analyze business data for signature drink indicators"""
        name = business_data.get('name', '').lower()
        
        # Check business name for drink indicators
        for drink_type, keywords in self.drink_keywords.items():
            for keyword in keywords:
                if keyword in name:
                    return self._format_drink_name(drink_type)
        
        # Check categories
        categories = business_data.get('categories', [])
        for category in categories:
            title = category.get('title', '').lower()
            if 'espresso' in title:
                return "House Espresso"
            elif 'pour over' in title or 'drip' in title:
                return "Pour Over Coffee"
        
        # Check if it's a specialty coffee shop
        if any('coffee' in cat.get('title', '').lower() for cat in categories):
            return "House Blend Coffee"
        
        return None
    
    def _should_analyze_reviews(self, business_data: Optional[Dict]) -> bool:
        """Determine if we should analyze reviews (conserves API calls)"""
        if not business_data:
            return False
        
        # Only analyze reviews for highly-rated shops
        rating = business_data.get('rating', 0)
        review_count = business_data.get('review_count', 0)
        
        # Analyze reviews if: high rating (4.0+) AND many reviews (50+)
        return rating >= 4.0 and review_count >= 50
    
    def _analyze_reviews(self, business_id: str) -> Optional[str]:
        """Analyze reviews to find most mentioned drinks"""
        try:
            url = f"{self.base_url}/businesses/{business_id}/reviews"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            reviews_data = response.json()
            reviews = reviews_data.get('reviews', [])
            
            # Extract text from all reviews
            all_text = ' '.join([review.get('text', '') for review in reviews])
            all_text = all_text.lower()
            
            # Count mentions of different drinks
            drink_counts = Counter()
            
            for drink_type, keywords in self.drink_keywords.items():
                for keyword in keywords:
                    count = len(re.findall(r'\b' + re.escape(keyword) + r'\b', all_text))
                    if count > 0:
                        drink_counts[drink_type] += count
            
            # Find the most mentioned drink
            if drink_counts:
                most_common_drink = drink_counts.most_common(1)[0][0]
                return self._format_drink_name(most_common_drink)
            
            return None
            
        except Exception as e:
            print(f"Error analyzing reviews: {e}")
            return None
    
    def _get_fallback_drink(self, business_name: str) -> str:
        """Get a creative fallback signature drink based on business name"""
        name_lower = business_name.lower()
        
        # Check for specific drink types in the name
        for drink_type, keywords in self.drink_keywords.items():
            for keyword in keywords:
                if keyword in name_lower:
                    return self._format_drink_name(drink_type)
        
        # Creative fallbacks based on business name patterns
        if 'downtown' in name_lower:
            return "Downtown Special Blend"
        elif 'espresso' in name_lower:
            return "House Espresso"
        elif 'latte' in name_lower:
            return "Signature Latte"
        elif 'cold' in name_lower or 'iced' in name_lower:
            return "Cold Brew Coffee"
        elif 'pour' in name_lower or 'drip' in name_lower:
            return "Pour Over Coffee"
        elif 'honolulu' in name_lower:
            return "Honolulu Sunrise Blend"
        elif 'coffee' in name_lower:
            return "Signature Coffee Blend"
        elif 'roast' in name_lower:
            return "House Roast"
        elif 'brew' in name_lower:
            return "Craft Brew"
        elif 'bean' in name_lower:
            return "Fresh Bean Blend"
        elif 'cafe' in name_lower:
            return "Cafe Special"
        elif 'java' in name_lower:
            return "Java House Blend"
        elif 'mocha' in name_lower:
            return "Rich Mocha"
        elif 'cappuccino' in name_lower:
            return "House Cappuccino"
        elif 'americano' in name_lower:
            return "Classic Americano"
        elif 'macchiato' in name_lower:
            return "Caramel Macchiato"
        else:
            # Generate a creative drink name based on the business name
            import random
            creative_drinks = [
                "Signature House Blend",
                "Artisan Coffee",
                "Craft Espresso",
                "Premium Roast",
                "Barista's Choice",
                "Local Favorite",
                "Fresh Ground Blend",
                "Daily Special",
                "Morning Brew",
                "Perfect Cup"
            ]
            return random.choice(creative_drinks)
    
    def _format_drink_name(self, drink_type: str) -> str:
        """Format drink type into a proper signature drink name"""
        if drink_type == 'latte':
            return "Signature Latte"
        elif drink_type == 'cappuccino':
            return "House Cappuccino"
        elif drink_type == 'espresso':
            return "House Espresso"
        elif drink_type == 'americano':
            return "Classic Americano"
        elif drink_type == 'mocha':
            return "Rich Mocha"
        elif drink_type == 'macchiato':
            return "Caramel Macchiato"
        elif drink_type == 'cold brew':
            return "Cold Brew Coffee"
        elif drink_type == 'pour over':
            return "Pour Over Coffee"
        elif drink_type == 'flat white':
            return "Flat White"
        elif drink_type == 'cortado':
            return "Cortado"
        elif drink_type == 'nitro':
            return "Nitro Cold Brew"
        elif drink_type == 'bulletproof':
            return "Bulletproof Coffee"
        elif drink_type == 'dalgona':
            return "Dalgona Coffee"
        elif drink_type == 'vietnamese':
            return "Vietnamese Coffee"
        elif drink_type == 'turkish':
            return "Turkish Coffee"
        elif drink_type == 'greek':
            return "Greek Coffee"
        elif drink_type == 'ethiopian':
            return "Ethiopian Coffee"
        elif drink_type == 'colombian':
            return "Colombian Coffee"
        elif drink_type == 'guatemalan':
            return "Guatemalan Coffee"
        elif drink_type == 'sumatra':
            return "Sumatra Coffee"
        elif drink_type == 'kenya':
            return "Kenya Coffee"
        elif drink_type == 'ethiopia':
            return "Ethiopian Coffee"
        elif drink_type == 'house blend':
            return "House Blend Coffee"
        elif drink_type == 'signature':
            return "Signature Coffee"
        else:
            return f"{drink_type.title()} Coffee" 