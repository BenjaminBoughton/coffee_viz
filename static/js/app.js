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
    // Honolulu coordinates (96814 area)
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
        .bindPopup('<b>Honolulu (96814)</b><br>Search area for coffee shops')
        .openPopup();
}

// Load coffee shops data
async function loadCoffeeShops() {
    try {
        const zipCode = document.getElementById('zipCode').value;
        const response = await fetch(`/api/coffee-shops?zip_code=${zipCode}`);
        const data = await response.json();
        
        coffeeShops = data.coffee_shops;
        displayCoffeeShops();
        addMarkersToMap();
        
    } catch (error) {
        console.error('Error loading coffee shops:', error);
        showError('Failed to load coffee shops data');
    }
}

// Display coffee shops in the sidebar
function displayCoffeeShops() {
    const container = document.getElementById('coffeeShopsList');
    container.innerHTML = '';
    
    coffeeShops.forEach(shop => {
        const shopCard = createShopCard(shop);
        container.appendChild(shopCard);
    });
}

// Create a coffee shop card
function createShopCard(shop) {
    const card = document.createElement('div');
    card.className = 'coffee-shop-card';
    card.onclick = () => selectShop(shop);
    
    const stars = '★'.repeat(Math.floor(shop.rating)) + '☆'.repeat(5 - Math.floor(shop.rating));
    
    card.innerHTML = `
        <div class="d-flex justify-content-between align-items-start">
            <div class="flex-grow-1">
                <div class="shop-name">${shop.name}</div>
                <div class="shop-address">${shop.address}</div>
                <div class="rating-stars">${stars} (${shop.rating})</div>
            </div>
            <div class="signature-drink">${shop.signature_drink}</div>
        </div>
        <div class="mt-2">
            <small class="text-muted">${shop.description}</small>
        </div>
    `;
    
    return card;
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
                    <p><strong>Signature Drink:</strong> ${shop.signature_drink}</p>
                    <p><strong>Rating:</strong> ${shop.rating} ⭐</p>
                    <p><small>${shop.address}</small></p>
                    <button class="btn btn-sm btn-primary" onclick="showShopDetails(${shop.id})">
                        View Details
                    </button>
                </div>
            `);
        
        markers.push(marker);
    });
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

// Show shop details in modal
async function showShopDetails(shopId) {
    try {
        const response = await fetch(`/api/coffee-shop/${shopId}`);
        const shop = await response.json();
        
        if (shop.error) {
            showError('Shop details not found');
            return;
        }
        
        displayShopModal(shop);
        
    } catch (error) {
        console.error('Error loading shop details:', error);
        showError('Failed to load shop details');
    }
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
                <p><strong>Hours:</strong> ${shop.hours}</p>
                <p><strong>Phone:</strong> ${shop.phone}</p>
                <p><strong>Website:</strong> <a href="${shop.website}" target="_blank">${shop.website}</a></p>
            </div>
            <div class="col-md-6">
                <h6>Signature Drink</h6>
                <div class="signature-drink">${shop.signature_drink}</div>
                <p class="mt-2"><strong>Description:</strong> ${shop.description}</p>
            </div>
        </div>
        
        <hr>
        
        <h6>Reviews</h6>
        <div id="reviewsContainer">
            ${shop.reviews.map(review => `
                <div class="review-item">
                    <div class="review-user">${review.user}</div>
                    <div class="rating-stars">${'★'.repeat(review.rating)}</div>
                    <div class="review-comment">"${review.comment}"</div>
                </div>
            `).join('')}
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
    const container = document.getElementById('coffeeShopsList');
    
    if (showOnlyRated) {
        const filteredShops = coffeeShops.filter(shop => shop.rating >= 4.5);
        displayFilteredShops(filteredShops);
    } else {
        displayCoffeeShops();
    }
}

// Display filtered shops
function displayFilteredShops(shops) {
    const container = document.getElementById('coffeeShopsList');
    container.innerHTML = '';
    
    if (shops.length === 0) {
        container.innerHTML = '<p class="text-muted">No highly rated coffee shops found.</p>';
        return;
    }
    
    shops.forEach(shop => {
        const shopCard = createShopCard(shop);
        container.appendChild(shopCard);
    });
}

// Show error message
function showError(message) {
    // You can implement a proper error notification system here
    alert(message);
} 