# Coffee Shop Finder - Dynamic Discovery

A web application that dynamically finds coffee shops near any location using real-time APIs. Built with Flask, Leaflet.js, and Yelp API.

## Features

- **Dynamic Coffee Shop Discovery**: Find real coffee shops near any zip code or location
- **Interactive Map**: View coffee shops on an interactive map using Leaflet.js
- **Radius Search**: Search within 1-15 miles of any location
- **Real-time Data**: Uses Yelp API for live business information
- **Rating Filtering**: Filter shops by rating (4.5+ stars)
- **Responsive Design**: Works on desktop and mobile devices

## How It Works

1. **Enter a Zip Code**: Type any US zip code (e.g., 96814 for Honolulu)
2. **Set Search Radius**: Choose how far to search (1-15 miles)
3. **Get Real Results**: App finds actual coffee shops in that area
4. **View Details**: See ratings, reviews, hours, and contact info

## Setup Instructions

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)
- Yelp API key (free tier available)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/BenjaminBoughton/coffee_viz.git
   cd coffee_viz
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Get Yelp API Key**
   - Go to [Yelp Developers](https://www.yelp.com/developers)
   - Create a free account
   - Create a new app to get your API key

4. **Set up environment variables**
   ```bash
   cp env_example.txt .env
   # Edit .env and add your Yelp API key
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Open your browser**
   Navigate to `http://localhost:8000`

## API Integration

### Yelp API
- **Purpose**: Find real coffee shops with ratings, reviews, and business info
- **Cost**: Free tier available (500 requests/day)
- **Data**: Business details, ratings, reviews, hours, photos

### Geocoding
- **Service**: OpenStreetMap Nominatim (free)
- **Purpose**: Convert zip codes to coordinates
- **Usage**: Automatic when searching by zip code

## Example Searches

Try these zip codes to test the app:
- **96814** (Honolulu) - Should find Try Coffee and others
- **10001** (New York) - Manhattan coffee shops
- **90210** (Beverly Hills) - LA coffee scene
- **94102** (San Francisco) - SF coffee culture

## API Endpoints

- `GET /api/coffee-shops?zip_code=96814&radius=5` - Get coffee shops by zip code
- `GET /api/coffee-shops?lat=21.3069&lng=-157.8583&radius=5` - Get shops by coordinates
- `GET /api/search?q=Honolulu` - Search by location name
- `GET /api/nearby?lat=21.3069&lng=-157.8583&radius=5` - Find shops near coordinates

## Technologies Used

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript
- **Map**: Leaflet.js with OpenStreetMap
- **Styling**: Bootstrap 5
- **APIs**: Yelp API, OpenStreetMap Geocoding
- **Data**: Real-time business data

## Development Phases

### Phase 1: Dynamic Discovery ✅
- [x] Yelp API integration
- [x] Zip code to coordinates conversion
- [x] Radius-based search
- [x] Real coffee shop data
- [x] Signature drink analyzer (basic)

### Phase 2: Enhanced Features (Planned)
- [ ] User reviews and ratings
- [ ] Photo galleries
- [ ] Directions and routing
- [ ] Advanced filtering (price, amenities)
- [ ] Save favorite locations

### Phase 3: Mobile App (Planned)
- [ ] React Native mobile app
- [ ] GPS location detection
- [ ] Push notifications for nearby shops

## TODO - Next Development Sprint

### 1. Better Coffee Shop Filtering 🔍 ✅ COMPLETED
- [x] Implement stricter filtering to show only dedicated coffee shops
- [x] Filter out restaurants, bakeries, and other businesses that happen to serve coffee
- [x] Focus on businesses with primary coffee/tea categories
- [x] Consider business name analysis for coffee-specific keywords

### 2. Minimum Rating Threshold ⭐ ✅ COMPLETED
- [x] Only show coffee shops with minimum 80 Yelp reviews
- [x] This ensures more reliable ratings and established businesses
- [x] Update search parameters to prioritize well-reviewed shops
- [x] Add review count display in the UI

### 3. Replace Signature Drink with NLP Review Summary 📝 ✅ COMPLETED
- [x] Remove signature drink analyzer (currently too generic)
- [x] Implement NLP analysis of Yelp reviews to generate shop summaries
- [x] Show top 3 coffee shops by rating in sidebar by default
- [x] Create intelligent summaries with proper sentence separation

### 4. Aesthetic Improvements 🎨
- [ ] Improve map styling and marker design
- [ ] Better responsive design for mobile devices
- [ ] Enhanced coffee shop cards with better typography
- [ ] Add loading states and better error handling
- [ ] Improve color scheme and overall visual appeal
- [ ] Add coffee-themed icons and graphics
- [ ] **Highlight top 3 shops in different color** 🎨

### 5. Enhanced API Integration 🔌
- [ ] Integrate other APIs for more details than Yelp can provide
- [ ] Research value propositions over existing Yelp (no sponsored results)
- [ ] Consider Google Places API, Foursquare, or other business data sources
- [ ] Evaluate cost-benefit of additional API integrations

### 6. Improved Location Search 📍
- [ ] Fix location geocoding - prevent "Kailua" from going to "Kailua-Kona" on Big Island
- [ ] Add dropdown of suggested location results as user types
- [ ] Implement location autocomplete with proper disambiguation
- [ ] Prioritize local results over distant matches
- [ ] Add state/city context to improve geocoding accuracy

## Contributing

Feel free to contribute to this project by submitting issues or pull requests.

## License

This project is open source and available under the MIT License. 