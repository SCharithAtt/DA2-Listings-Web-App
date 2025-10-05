import requests
import time

print("Waiting 2 seconds for server to start...")
time.sleep(2)

print("\n testing /listings/latest endpoint...")
try:
    response = requests.get("http://127.0.0.1:8000/listings/latest?limit=3", timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Response Length: {len(response.text)} characters")
    
    if response.status_code == 200:
        listings = response.json()
        print(f"\n✅ SUCCESS! Got {len(listings)} listings\n")
        for i, listing in enumerate(listings, 1):
            print(f"{i}. {listing.get('title', 'NO TITLE')}")
            print(f"   Price: Rs {listing.get('price', 0):,}")
            print(f"   City: {listing.get('city', 'N/A')}")
            print(f"   Images: {len(listing.get('images', []))}")
    else:
        print(f"\n❌ ERROR Response:")
        print(response.text[:500])
        
except requests.exceptions.Timeout:
    print("❌ Request timed out!")
except requests.exceptions.ConnectionError:
    print("❌ Cannot connect to server!")
except Exception as e:
    print(f"❌ Error: {e}")
