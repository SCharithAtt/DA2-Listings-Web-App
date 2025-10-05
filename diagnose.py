"""
Diagnostic script to check API connectivity
"""
import requests
import json

API_URL = "http://localhost:8000"

print("=" * 70)
print("LISTINGS WEB APP - DIAGNOSTIC CHECK")
print("=" * 70)

# Test 1: Check if backend is running
print("\n1️⃣  Testing backend connectivity...")
try:
    response = requests.get(f"{API_URL}/listings/latest?limit=3", timeout=5)
    print(f"   ✅ Backend is responding (Status: {response.status_code})")
    
    if response.status_code == 200:
        listings = response.json()
        print(f"   ✅ Fetched {len(listings)} listings")
        
        if len(listings) > 0:
            print("\n   Sample listing:")
            first = listings[0]
            print(f"      Title: {first.get('title', 'N/A')}")
            print(f"      Price: Rs {first.get('price', 0):,}")
            print(f"      City: {first.get('city', 'N/A')}")
            print(f"      Category: {first.get('category', 'N/A')}")
            print(f"      Images: {len(first.get('images', []))} image(s)")
    else:
        print(f"   ❌ Error: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
        
except requests.exceptions.ConnectionError:
    print("   ❌ Cannot connect to backend!")
    print("   ℹ️  Make sure the server is running:")
    print("      .\.venv\Scripts\python.exe -m uvicorn main:app --reload --host 127.0.0.1 --port 8000")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 2: Check categories endpoint
print("\n2️⃣  Testing categories endpoint...")
try:
    response = requests.get(f"{API_URL}/listings/categories", timeout=5)
    if response.status_code == 200:
        categories = response.json()
        print(f"   ✅ Found {len(categories)} categories")
        print(f"   Categories: {', '.join(categories[:5])}...")
    else:
        print(f"   ❌ Error: {response.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 3: Check CORS headers
print("\n3️⃣  Testing CORS headers...")
try:
    response = requests.options(f"{API_URL}/listings/latest")
    cors_header = response.headers.get('Access-Control-Allow-Origin', 'Not set')
    print(f"   Access-Control-Allow-Origin: {cors_header}")
    if cors_header == '*' or 'localhost' in cors_header:
        print("   ✅ CORS is configured correctly")
    else:
        print("   ⚠️  CORS might be an issue for frontend")
except Exception as e:
    print(f"   ⚠️  Could not check CORS: {e}")

print("\n" + "=" * 70)
print("DIAGNOSTIC COMPLETE")
print("=" * 70)
print("\nℹ️  Frontend should be accessible at: http://localhost:5173")
print("ℹ️  Backend API should be running at: http://localhost:8000")
print("\nIf backend is not responding, start it with:")
print("   .\.venv\Scripts\python.exe -m uvicorn main:app --reload --host 127.0.0.1 --port 8000")
