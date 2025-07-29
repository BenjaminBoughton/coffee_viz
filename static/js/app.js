// Global variables
let map;
let markers = [];
let coffeeShops = [];
let selectedShop = null;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeMap();
    loadCoffeeShops();
});

// Initialize Leaflet map
function initializeMap() {
    // Honolulu coordinates (centered on actual coffee shop locations)
    const honoluluCoords = [21.3069, -157.8583];
    
    // Create map
    map = L.map('map').setView(honoluluCoords, 13);
    
    // Add OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);
    
    // Add a marker for the search area
    L.marker(honoluluCoords)
        .addTo(map)
        .bindPopup('<b>Honolulu Coffee Area</b><br>Search for coffee shops')
        .openPopup();
}

// Load coffee shops data
async function loadCoffeeShops() {
    try {
        const zipCode = document.getElementById('zipCode').value;
        const radius = document.getElementById('searchRadius').value;
        console.log('Loading coffee shops for zip code:', zipCode, 'with radius:', radius, 'miles');
        
        let url = `/api/coffee-shops`;
        const params = new URLSearchParams();
        
        if (zipCode && zipCode.trim() !== '') {
            params.append('zip_code', zipCode);
        }
        if (radius) {
            params.append('radius', radius);
        }
        
        if (params.toString()) {
            url += `?${params.toString()}`;
        }
        
        const response = await fetch(url);
        const data = await response.json();
        
        console.log('API response:', data);
        console.log('Coffee shops found:', data.coffee_shops ? data.coffee_shops.length : 0);
        console.log('Top shops:', data.top_shops ? data.top_shops.length : 0);
        
        coffeeShops = data.coffee_shops || [];
        
        displayTopShops(data.top_shops || []);
        displayAllShopsSection(data.all_shops_count || 0);
        addMarkersToMap();
        
        // Center map on the search results using API coordinates
        centerMapOnResults(data.lat, data.lng);
        
    } catch (error) {
        console.error('Error loading coffee shops:', error);
        showError('Failed to load coffee shops data');
    }
}

// Display top 3 coffee shops with NLP summaries
function displayTopShops(topShops) {
    const container = document.getElementById('topShopsList');
    container.innerHTML = '';
    
    if (topShops.length === 0) {
        container.innerHTML = '<p class="text-muted">No coffee shops found in this area.</p>';
        return;
    }
    
    topShops.forEach((shop, index) => {
        const shopCard = createTopShopCard(shop, index + 1);
        container.appendChild(shopCard);
    });
}

// Display all shops section with dropdown
function displayAllShopsSection(allShopsCount) {
    const container = document.getElementById('allShopsSection');
    
    if (allShopsCount <= 3) {
        container.innerHTML = '';
        return;
    }
    
    container.innerHTML = `
        <button class="all-shops-toggle" onclick="toggleAllShops()">
            Show all remaining coffee shops
            <span class="toggle-icon">▼</span>
        </button>
        <div class="all-shops-list" id="allShopsList">
            <!-- All shops will be loaded here when expanded -->
        </div>
    `;
}

// Create a top coffee shop card with NLP summary
function createTopShopCard(shop, rank) {
    const card = document.createElement('div');
    card.className = 'coffee-shop-card top-shops-section';
    card.onclick = () => selectShop(shop);
    
    const stars = '★'.repeat(Math.floor(shop.rating)) + '☆'.repeat(5 - Math.floor(shop.rating));
    
    card.innerHTML = `
        <div class="d-flex justify-content-between align-items-start">
            <div class="flex-grow-1">
                <div class="shop-name">
                    <span class="badge bg-primary me-2">#${rank}</span>
                    ${shop.name}
                </div>
                <div class="shop-address">${shop.address}</div>
                <div class="rating-stars">${stars} (${shop.rating}) • ${shop.review_count} reviews</div>
            </div>
        </div>
        <div class="nlp-summary">
            ${shop.nlp_summary || 'A coffee shop with great reviews.'}
        </div>
        <div class="mt-2">
            <button class="btn btn-sm btn-outline-primary" onclick="event.stopPropagation(); openShopLink('${shop.yelp_url || ''}')">
                View Yelp Page
            </button>
        </div>
    `;
    
    return card;
}

// Create a simple shop item for the all shops list
function createShopItem(shop) {
    const item = document.createElement('div');
    item.className = 'all-shop-item';
    item.onclick = () => selectShop(shop);
    
    const stars = '★'.repeat(Math.floor(shop.rating)) + '☆'.repeat(5 - Math.floor(shop.rating));
    
    item.innerHTML = `
        <div class="d-flex justify-content-between align-items-center">
            <div>
                <div class="shop-name">${shop.name}</div>
                <div class="rating-stars">${stars} (${shop.rating})</div>
            </div>
            <small class="text-muted">${shop.review_count} reviews</small>
        </div>
    `;
    
    return item;
}

// Toggle the all shops dropdown
function toggleAllShops() {
    const toggle = document.querySelector('.all-shops-toggle');
    const list = document.getElementById('allShopsList');
    
    if (list.classList.contains('show')) {
        // Collapse
        list.classList.remove('show');
        toggle.classList.remove('expanded');
        list.innerHTML = '';
    } else {
        // Expand
        list.classList.add('show');
        toggle.classList.add('expanded');
        
        // Load all shops (excluding top 3)
        const allShops = coffeeShops.slice(3);
        allShops.forEach(shop => {
            const shopItem = createShopItem(shop);
            list.appendChild(shopItem);
        });
    }
}

// Add markers to the map
function addMarkersToMap() {
    // Clear existing markers
    markers.forEach(marker => map.removeLayer(marker));
    markers = [];
    
    coffeeShops.forEach((shop, index) => {
        const marker = L.marker([shop.lat, shop.lng])
            .addTo(map)
            .bindPopup(`
                <div style="min-width: 200px;">
                    <h6>${shop.name}</h6>
                    <p><strong>Rating:</strong> ${shop.rating} ⭐ (${shop.review_count} reviews)</p>
                    <p><small>${shop.address}</small></p>
                    <button class="btn btn-sm btn-primary" onclick="openShopLink('${shop.yelp_url || ''}')">
                        ${shop.yelp_url ? 'View Yelp Page' : 'No Link'}
                    </button>
                </div>
            `);
        
        markers.push(marker);
    });
}

// Center map on search results
function centerMapOnResults(lat, lng) {
    if (coffeeShops.length === 0) {
        // If no results, center on the searched location coordinates
        if (lat && lng) {
            map.setView([lat, lng], 10);
        } else {
            // Fallback to Honolulu if no coordinates provided
            map.setView([21.3069, -157.8583], 10);
        }
        return;
    }
    
    // If we have results, fit the map to show all markers
    if (markers.length > 0) {
        const group = new L.featureGroup(markers);
        map.fitBounds(group.getBounds().pad(0.1)); // Add 10% padding
    } else if (coffeeShops.length === 1) {
        // If only one result, center on it with zoom
        const shop = coffeeShops[0];
        map.setView([shop.lat, shop.lng], 14);
    }
}

// Select a coffee shop
function selectShop(shop) {
    // Remove previous selection
    document.querySelectorAll('.coffee-shop-card').forEach(card => {
        card.classList.remove('selected');
    });
    
    // Add selection to clicked card
    event.currentTarget.classList.add('selected');
    
    // Center map on selected shop
    map.setView([shop.lat, shop.lng], 15);
    
    // Open popup for the corresponding marker
    const markerIndex = coffeeShops.findIndex(s => s.id === shop.id);
    if (markerIndex !== -1 && markers[markerIndex]) {
        markers[markerIndex].openPopup();
    }
    
    selectedShop = shop;
}

// Show shop details in modal (legacy function - now using direct links)
async function showShopDetails(shopId) {
    console.log('showShopDetails is deprecated - using direct links instead');
}

// Display shop details in modal
function displayShopModal(shop) {
    const modal = new bootstrap.Modal(document.getElementById('shopDetailModal'));
    const modalTitle = document.getElementById('modalTitle');
    const modalBody = document.getElementById('modalBody');
    
    modalTitle.textContent = shop.name;
    
    const stars = '★'.repeat(Math.floor(shop.rating)) + '☆'.repeat(5 - Math.floor(shop.rating));
    
    modalBody.innerHTML = `
        <div class="row">
            <div class="col-md-6">
                <h6>Basic Information</h6>
                <p><strong>Address:</strong> ${shop.address}</p>
                <p><strong>Rating:</strong> ${stars} (${shop.rating})</p>
                <p><strong>Review Count:</strong> ${shop.review_count}</p>
                <p><strong>Hours:</strong> ${shop.hours}</p>
                <p><strong>Phone:</strong> ${shop.phone}</p>
                <p><strong>Website:</strong> <a href="${shop.website}" target="_blank">${shop.website}</a></p>
            </div>
            <div class="col-md-6">
                <h6>Summary</h6>
                <div class="nlp-summary">${shop.nlp_summary || 'A coffee shop with great reviews.'}</div>
                <p class="mt-2"><strong>Description:</strong> ${shop.description}</p>
            </div>
        </div>
        
        <hr>
        
        <h6>Reviews</h6>
        <div id="reviewsContainer">
            ${shop.reviews ? shop.reviews.map(review => `
                <div class="review-item">
                    <div class="review-user">${review.user}</div>
                    <div class="rating-stars">${'★'.repeat(review.rating)}</div>
                    <div class="review-comment">"${review.comment}"</div>
                </div>
            `).join('') : '<p class="text-muted">No reviews available.</p>'}
        </div>
    `;
    
    modal.show();
}

// Search coffee shops by zip code
function searchCoffeeShops() {
    loadCoffeeShops();
}

// Filter shops by rating
function filterShops() {
    const showOnlyRated = document.getElementById('showOnlyRated').checked;
    
    if (showOnlyRated) {
        const filteredShops = coffeeShops.filter(shop => shop.rating >= 4.5);
        const topShopsData = { top_shops: filteredShops.slice(0, 3), all_shops_count: filteredShops.length };
        displayTopShops(topShopsData.top_shops);
        displayAllShopsSection(topShopsData.all_shops_count);
    } else {
        // Reload the original data
        loadCoffeeShops();
    }
}

// Open shop website or Yelp page
function openShopLink(url) {
    if (url && url.trim() !== '') {
        window.open(url, '_blank');
    } else {
        showError('No website or Yelp page available for this coffee shop.');
    }
}

// Show error message
function showError(message) {
    // You can implement a proper error notification system here
    alert(message);
} 