#!/usr/bin/env python3
"""
Database initialization script for Coffee Shop Finder
Populates the SQLite database with Hawaii coffee shop data
"""

from services.database_service import CoffeeShopDatabaseService

def main():
    """Initialize the database with Hawaii coffee shop data"""
    print("Initializing Coffee Shop Database...")
    
    # Initialize database service
    db_service = CoffeeShopDatabaseService()
    
    # Check if database is empty
    stats = db_service.get_statistics()
    if stats['total_shops'] > 0:
        print(f"Database already contains {stats['total_shops']} coffee shops")
        print("Top rated shops:")
        for shop in stats['top_rated']:
            print(f"  - {shop['name']}: {shop['rating']} stars")
    else:
        # Populate with Hawaii data
        print("Populating database with Hawaii coffee shop data...")
        db_service.populate_hawaii_data()
        
        # Show statistics
        stats = db_service.get_statistics()
        print(f"Database now contains {stats['total_shops']} coffee shops")
        print(f"Average rating: {stats['avg_rating']}")
        print("Top rated shops:")
        for shop in stats['top_rated']:
            print(f"  - {shop['name']}: {shop['rating']} stars")
    
    print("\nDatabase initialization complete!")
    print("You can now run the Flask app with: python app.py")

if __name__ == "__main__":
    main() 