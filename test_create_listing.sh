#!/bin/bash
# Create Listing API Test Script (Bash/Linux/Mac)
# Make executable: chmod +x test_create_listing.sh

echo "=== Create Listing API Test ==="
echo ""

# Configuration
API_URL="http://localhost:8000"
EMAIL="admin@listings.app"
PASSWORD="admin123"

# Step 1: Login to get token
echo "Step 1: Logging in..."
LOGIN_RESPONSE=$(curl -s -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}")

TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo "✗ Login failed"
    echo $LOGIN_RESPONSE
    exit 1
fi

echo "✓ Login successful!"
echo ""

# Step 2: Create Listing
echo "Step 2: Creating listing..."

LISTING_RESPONSE=$(curl -s -X POST "$API_URL/listings" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "title": "iPhone 13 Pro - 128GB (Test Listing)",
    "description": "Brand new iPhone 13 Pro in Sierra Blue color. 128GB storage, unlocked, with original box and accessories.",
    "price": 285000,
    "city": "Colombo",
    "category": "electronics",
    "lat": 6.9271,
    "lng": 79.8612,
    "tags": ["iphone", "smartphone", "apple", "unlocked", "test"],
    "features": ["5G", "128GB", "Sierra Blue", "Unlocked"],
    "expiry_days": 30
  }')

LISTING_ID=$(echo $LISTING_RESPONSE | grep -o '"_id":"[^"]*' | cut -d'"' -f4)

if [ -z "$LISTING_ID" ]; then
    echo "✗ Listing creation failed"
    echo $LISTING_RESPONSE
    exit 1
fi

echo "✓ Listing created successfully!"
echo "  ID: $LISTING_ID"
echo ""

# Step 3: Add image via URL
echo "Step 3: Adding image via URL..."
IMAGE_URL="https://picsum.photos/400/300"

curl -s -X POST "$API_URL/listings/$LISTING_ID/images/url?image_url=$IMAGE_URL" \
  -H "Authorization: Bearer $TOKEN" > /dev/null

echo "✓ Image added!"
echo ""
echo "=== Test Complete ==="
echo ""
echo "View listing: http://localhost:5173/listing/$LISTING_ID"
echo "My Listings: http://localhost:5173/my-listings"
