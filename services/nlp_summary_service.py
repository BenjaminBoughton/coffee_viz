import re
import json
from typing import List, Dict, Optional
from collections import Counter

class NLPSummaryService:
    def __init__(self):
        """Initialize NLP summary service"""
        # Common coffee-related keywords and phrases
        self.coffee_keywords = [
            'coffee', 'espresso', 'latte', 'cappuccino', 'americano', 'mocha',
            'pour-over', 'drip', 'cold brew', 'nitro', 'roast', 'roastery',
            'artisan', 'specialty', 'premium', 'organic', 'fair trade',
            'single origin', 'blend', 'house blend', 'signature'
        ]
        
        # Atmosphere and experience keywords
        self.atmosphere_keywords = [
            'atmosphere', 'ambiance', 'cozy', 'welcoming', 'friendly',
            'relaxing', 'quiet', 'lively', 'modern', 'rustic', 'industrial',
            'outdoor', 'patio', 'seating', 'wifi', 'laptop', 'work',
            'meeting', 'study', 'hangout', 'social'
        ]
        
        # Service and quality keywords
        self.service_keywords = [
            'service', 'friendly', 'helpful', 'knowledgeable', 'barista',
            'quality', 'fresh', 'delicious', 'amazing', 'best', 'favorite',
            'recommend', 'love', 'great', 'excellent', 'outstanding'
        ]
        
        # Food and menu keywords
        self.food_keywords = [
            'pastry', 'sandwich', 'breakfast', 'lunch', 'snack',
            'dessert', 'cake', 'cookie', 'muffin', 'croissant',
            'avocado toast', 'acai bowl', 'smoothie', 'tea'
        ]
    
    def generate_shop_summary(self, shop_data: Dict) -> str:
        """Generate a natural language summary for a coffee shop"""
        try:
            # Extract key information
            name = shop_data.get('name', '')
            rating = shop_data.get('rating', 0)
            review_count = shop_data.get('review_count', 0)
            description = shop_data.get('description', '')
            price = shop_data.get('price', '')
            
            # Analyze the shop name for characteristics
            name_analysis = self._analyze_shop_name(name)
            
            # Create a structured summary
            summary_parts = []
            
            # Rating and popularity
            if rating >= 4.5:
                summary_parts.append(f"Highly rated with {rating} stars")
            elif rating >= 4.0:
                summary_parts.append(f"Well-rated with {rating} stars")
            else:
                summary_parts.append(f"Rated {rating} stars")
            
            if review_count >= 200:
                summary_parts.append("and a large following")
            elif review_count >= 100:
                summary_parts.append("with many positive reviews")
            
            # Add period after rating/popularity section
            if summary_parts:
                summary_parts[-1] += "."
            
            # Price level
            if price == '$$$':
                summary_parts.append("This premium coffee shop")
            elif price == '$$':
                summary_parts.append("This mid-range coffee shop")
            else:
                summary_parts.append("This coffee shop")
            
            # Name-based characteristics
            if name_analysis['is_roastery']:
                summary_parts.append("specializes in artisanal coffee roasting")
            elif name_analysis['is_cafe']:
                summary_parts.append("offers a cozy cafe experience")
            elif name_analysis['is_specialty']:
                summary_parts.append("focuses on specialty coffee drinks")
            elif name_analysis['is_brew']:
                summary_parts.append("features craft brewing methods")
            elif name_analysis['is_coffee']:
                summary_parts.append("serves quality coffee and beverages")
            else:
                summary_parts.append("provides excellent coffee and drinks")
            
            # Add atmosphere and service notes
            atmosphere_notes = self._generate_atmosphere_notes(name, description)
            if atmosphere_notes:
                summary_parts.append(f"Known for {atmosphere_notes}")
            
            # Add food offerings if mentioned
            food_notes = self._generate_food_notes(name, description)
            if food_notes:
                summary_parts.append(f"Also offers {food_notes}.")
            
            # Add period after main description if not already present
            if summary_parts and not summary_parts[-1].endswith('.'):
                summary_parts[-1] += "."
            
            # Combine all parts
            summary = " ".join(summary_parts)
            
            # Remove double periods and ensure proper ending
            summary = summary.replace("..", ".")
            if not summary.endswith('.'):
                summary += "."
            
            # Ensure the summary is not too long
            if len(summary) > 200:
                summary = summary[:197] + "..."
            
            return summary
            
        except Exception as e:
            print(f"Error generating summary: {e}")
            return f"A coffee shop with a {rating} star rating based on {review_count} reviews."
    
    def _analyze_shop_name(self, name: str) -> Dict:
        """Analyze shop name for characteristics"""
        name_lower = name.lower()
        
        return {
            'is_roastery': any(word in name_lower for word in ['roast', 'roastery', 'roaster']),
            'is_cafe': any(word in name_lower for word in ['cafe', 'café']),
            'is_specialty': any(word in name_lower for word in ['specialty', 'speciality', 'artisan', 'premium']),
            'is_brew': 'brew' in name_lower,
            'is_coffee': 'coffee' in name_lower,
            'has_location': any(word in name_lower for word in ['honolulu', 'hawaii', 'hi', 'oahu'])
        }
    
    def _generate_atmosphere_notes(self, name: str, description: str) -> str:
        """Generate notes about atmosphere based on name and description"""
        text = f"{name} {description}".lower()
        
        atmosphere_indicators = []
        
        if any(word in text for word in ['cozy', 'welcoming', 'friendly']):
            atmosphere_indicators.append("its welcoming atmosphere")
        elif any(word in text for word in ['modern', 'industrial']):
            atmosphere_indicators.append("its modern setting")
        elif any(word in text for word in ['rustic', 'charming']):
            atmosphere_indicators.append("its charming ambiance")
        
        if any(word in text for word in ['wifi', 'laptop', 'work']):
            atmosphere_indicators.append("being a great spot for work")
        elif any(word in text for word in ['meeting', 'social', 'hangout']):
            atmosphere_indicators.append("being a popular gathering spot")
        
        if atmosphere_indicators:
            return " and ".join(atmosphere_indicators)
        
        return ""
    
    def _generate_food_notes(self, name: str, description: str) -> str:
        """Generate notes about food offerings"""
        text = f"{name} {description}".lower()
        
        food_offerings = []
        
        if any(word in text for word in ['pastry', 'baked', 'dessert']):
            food_offerings.append("fresh pastries")
        elif any(word in text for word in ['sandwich', 'breakfast', 'lunch']):
            food_offerings.append("light meals")
        elif any(word in text for word in ['smoothie', 'juice', 'tea']):
            food_offerings.append("refreshing beverages")
        
        if food_offerings:
            return ", ".join(food_offerings)
        
        return ""
    
    def generate_top_shops_summary(self, shops: List[Dict], top_count: int = 3) -> Dict:
        """Generate summaries for the top-rated coffee shops"""
        if not shops:
            return {
                'top_shops': [],
                'all_shops_count': 0
            }
        
        # Sort shops by rating (highest first), then by review count
        sorted_shops = sorted(shops, key=lambda x: (x.get('rating', 0), x.get('review_count', 0)), reverse=True)
        
        # Get top shops
        top_shops = sorted_shops[:top_count]
        
        # Generate summaries for top shops
        for shop in top_shops:
            shop['nlp_summary'] = self.generate_shop_summary(shop)
        
        return {
            'top_shops': top_shops,
            'all_shops_count': len(shops)
        }
    
    def analyze_reviews_for_summary(self, reviews: List[Dict]) -> str:
        """Analyze reviews to generate a more detailed summary"""
        if not reviews:
            return ""
        
        # Extract common themes from reviews
        all_text = " ".join([review.get('text', '') for review in reviews]).lower()
        
        themes = []
        
        # Coffee quality
        coffee_quality_words = ['amazing', 'delicious', 'best', 'great', 'excellent', 'outstanding']
        coffee_quality_count = sum(1 for word in coffee_quality_words if word in all_text)
        if coffee_quality_count >= 3:
            themes.append("exceptional coffee quality")
        
        # Service
        service_words = ['friendly', 'helpful', 'knowledgeable', 'attentive']
        service_count = sum(1 for word in service_words if word in all_text)
        if service_count >= 2:
            themes.append("excellent service")
        
        # Atmosphere
        atmosphere_words = ['cozy', 'welcoming', 'relaxing', 'beautiful']
        atmosphere_count = sum(1 for word in atmosphere_words if word in all_text)
        if atmosphere_count >= 2:
            themes.append("great atmosphere")
        
        # Value
        value_words = ['worth', 'reasonable', 'fair', 'good value']
        value_count = sum(1 for word in value_words if word in all_text)
        if value_count >= 2:
            themes.append("good value")
        
        if themes:
            return f"Customers particularly praise: {', '.join(themes)}."
        
        return "" 