"""
Create Listing API Test Script (Python)
Run: python test_create_listing.py
"""

import requests
import json
from datetime import datetime

# Configuration
API_URL = "http://localhost:8000"
EMAIL = "admin@listings.app"
PASSWORD = "admin123"

print("=== Create Listing API Test ===\n")

# Step 1: Login
print("Step 1: Logging in...")
try:
    login_response = requests.post(
        f"{API_URL}/auth/login",
        json={"email": EMAIL, "password": PASSWORD}
    )
    login_response.raise_for_status()
    token = login_response.json()["access_token"]
    print(f"✓ Login successful!")
    print(f"  Token: {token[:20]}...\n")
except Exception as e:
    print(f"✗ Login failed: {e}")
    exit(1)

# Step 2: Create Listing
print("Step 2: Creating listing...")
listing_data = {
    "title": "iPhone 13 Pro - 128GB (Test Listing)",
    "description": "Brand new iPhone 13 Pro in Sierra Blue color. 128GB storage, unlocked, with original box and accessories. Never used, still in sealed packaging. Created via Python API test.",
    "price": 285000,
    "city": "Colombo",
    "category": "electronics",
    "lat": 6.9271,
    "lng": 79.8612,
    "tags": ["iphone", "smartphone", "apple", "unlocked", "test"],
    "features": ["5G", "128GB", "Sierra Blue", "Unlocked", "Face ID"],
    "expiry_days": 30
}

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {token}"
}

try:
    listing_response = requests.post(
        f"{API_URL}/listings",
        json=listing_data,
        headers=headers
    )
    listing_response.raise_for_status()
    listing = listing_response.json()
    
    print("✓ Listing created successfully!\n")
    print("Listing Details:")
    print(f"  ID: {listing['_id']}")
    print(f"  Title: {listing['title']}")
    print(f"  Price: Rs {listing['price']:,}")
    print(f"  City: {listing['city']}")
    print(f"  Category: {listing['category']}")
    print(f"  Posted: {listing['posted_date']}")
    print(f"  Expires: {listing['expires_at']}\n")
    
    listing_id = listing['_id']
    
    # Step 3: Add image via URL
    print("Step 3: Adding image via URL...")
    image_url = "https://picsum.photos/400/300"
    
    try:
        image_response = requests.post(
            f"{API_URL}/listings/{listing_id}/images/url",
            params={"image_url": image_url},
            headers={"Authorization": f"Bearer {token}"}
        )
        image_response.raise_for_status()
        print("✓ Image added successfully!")
        print(f"  Image URL: {image_url}\n")
    except Exception as e:
        print(f"✗ Image addition failed: {e}\n")
    
    print("=== Test Complete ===\n")
    print(f"View listing: http://localhost:5173/listing/{listing_id}")
    print(f"My Listings: http://localhost:5173/my-listings")
    
except requests.exceptions.HTTPError as e:
    print(f"✗ Listing creation failed!")
    print(f"Status: {e.response.status_code}")
    print(f"Error: {e.response.text}")
except Exception as e:
    print(f"✗ Unexpected error: {e}")
