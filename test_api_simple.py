import requests
import json

response = requests.get("http://localhost:8000/listings/latest?limit=5")
print(f"Status: {response.status_code}")

if response.status_code == 200:
    listings = response.json()
    print(f"\n✅ Successfully fetched {len(listings)} listings\n")
    
    for i, listing in enumerate(listings, 1):
        print(f"{i}. {listing['title']}")
        print(f"   Price: Rs {listing['price']:,}")
        print(f"   City: {listing['city']}")
        print(f"   Category: {listing['category']}")
        print(f"   Images: {len(listing.get('images', []))}")
        print()
else:
    print(f"❌ Error: {response.status_code}")
    print(response.text)
