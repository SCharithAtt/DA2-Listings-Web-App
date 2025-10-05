import requests

print("Testing /test-simple...")
try:
    r = requests.get("http://127.0.0.1:8000/listings/test-simple")
    print(f"Status: {r.status_code}, Response: {r.text}")
except Exception as e:
    print(f"Error: {e}")

print("\nTesting /categories...")
try:
    r = requests.get("http://127.0.0.1:8000/listings/categories")
    print(f"Status: {r.status_code}, Response: {r.text[:100]}")
except Exception as e:
    print(f"Error: {e}")

print("\nTesting /latest...")
try:
    r = requests.get("http://127.0.0.1:8000/listings/latest?limit=1")
    print(f"Status: {r.status_code}, Response: {r.text[:200]}")
except Exception as e:
    print(f"Error: {e}")
