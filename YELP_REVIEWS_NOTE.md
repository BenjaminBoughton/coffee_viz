# Yelp Reviews Integration Note

## Current State
The current NLP summary service generates intelligent summaries based on:
- Shop name analysis
- Rating and review count
- Price level
- Category information
- Basic business data

## Potential Enhancement: Yelp Reviews Integration

### Why Reviews Would Help
- **More Specific Information**: Instead of generic summaries, we could mention specific drinks, atmosphere details, or service highlights mentioned in reviews
- **Customer Insights**: Real feedback about what customers love about each shop
- **Dynamic Content**: Reviews change over time, keeping summaries current

### Yelp API Review Endpoint
```python
# Example of how to fetch reviews
def get_business_reviews(self, business_id: str) -> List[Dict]:
    """Get reviews for a specific business"""
    try:
        url = f"{self.base_url}/businesses/{business_id}/reviews"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json().get('reviews', [])
    except Exception as e:
        print(f"Error fetching reviews: {e}")
        return []
```

### Enhanced NLP Summary with Reviews
```python
def generate_shop_summary_with_reviews(self, shop_data: Dict, reviews: List[Dict]) -> str:
    """Generate summary using actual review content"""
    
    # Extract common themes from reviews
    review_text = " ".join([review.get('text', '') for review in reviews])
    
    # Look for specific mentions
    if 'latte' in review_text.lower():
        summary_parts.append("known for their excellent lattes")
    if 'pour-over' in review_text.lower():
        summary_parts.append("praised for their pour-over coffee")
    if 'friendly' in review_text.lower():
        summary_parts.append("appreciated for their friendly service")
    
    return " ".join(summary_parts)
```

### Implementation Considerations
1. **API Rate Limits**: Yelp has rate limits (500 requests/day for free tier)
2. **Performance**: Additional API calls would slow down response time
3. **Caching**: Could cache reviews to avoid repeated API calls
4. **Selective Loading**: Only fetch reviews for top 3 shops to minimize API usage

### Example Enhanced Summary
**Current**: "Highly rated with 4.8 stars and a large following. This premium coffee shop specializes in artisanal coffee roasting."

**With Reviews**: "Highly rated with 4.8 stars and a large following. This premium coffee shop specializes in artisanal coffee roasting. Customers rave about their pour-over coffee and friendly baristas. Many mention the cozy atmosphere perfect for work or meetings."

## Recommendation
For now, the current implementation provides good value with the data we have. If we want to add review integration later, we could:
1. Start with top 3 shops only
2. Cache reviews for 24 hours
3. Add review analysis as an optional enhancement
4. Monitor API usage to stay within limits 