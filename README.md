# Coffee Shop Finder - Honolulu

A web application that maps coffee shops in Honolulu with reviews and signature drinks. Built with Flask, Leaflet.js, and Bootstrap.

## Features

- **Interactive Map**: View coffee shops on an interactive map using Leaflet.js
- **Search by Zip Code**: Find coffee shops in specific zip codes (currently focused on Honolulu 96814)
- **Shop Details**: View detailed information including signature drinks, ratings, and reviews
- **Filtering**: Filter shops by rating (4.5+ stars)
- **Responsive Design**: Works on desktop and mobile devices

## Project Structure

```
coffee_viz/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── app/
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css # Custom styles
│   │   └── js/
│   │       └── app.js    # Frontend JavaScript
│   └── templates/
│       └── index.html    # Main HTML template
├── api/
│   ├── routes/           # API route handlers
│   └── services/         # Business logic services
└── data/                 # Data files
```

## Setup Instructions

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

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

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Open your browser**
   Navigate to `http://localhost:5000`

## Current Coffee Shops (Phase 1)

The application currently includes sample data for popular Honolulu coffee shops:

- **Honolulu Coffee Company** - Hawaiian Latte
- **Island Vintage Coffee** - Island Mocha  
- **Morning Glass Coffee** - Manu Manu
- **The Curb Kaimuki** - Kaimuki Cold Brew
- **Coffee Gallery** - Gallery Blend

## API Endpoints

- `GET /` - Main application page
- `GET /api/coffee-shops?zip_code=96814` - Get coffee shops by zip code
- `GET /api/coffee-shop/<id>` - Get detailed information about a specific shop

## Technologies Used

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript
- **Map**: Leaflet.js with OpenStreetMap
- **Styling**: Bootstrap 5
- **Data**: Static JSON data (Phase 1)

## Development Phases

### Phase 1: Basic Map with Static Data ✅
- [x] Flask application setup
- [x] Interactive map with Leaflet.js
- [x] Sample coffee shop data for Honolulu
- [x] Basic search and filtering functionality

### Phase 2: API Integration (Planned)
- [ ] Integrate Yelp API for real coffee shop data
- [ ] Implement actual zip code filtering
- [ ] Add real-time reviews and ratings

### Phase 3: Enhanced Features (Planned)
- [ ] User authentication
- [ ] User reviews and ratings
- [ ] Photo galleries
- [ ] Directions and routing
- [ ] Advanced filtering options

## Contributing

Feel free to contribute to this project by submitting issues or pull requests.

## License

This project is open source and available under the MIT License. 