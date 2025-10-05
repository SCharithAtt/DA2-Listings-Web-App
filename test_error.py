import requests

try:
    response = requests.get("http://127.0.0.1:8000/listings/latest?limit=1")
    print(f"Status: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    print(f"\nFull Response:")
    print(response.text)
    
    if response.status_code == 500:
        print("\n🔍 Check the server console/window for the actual Python traceback!")
        
except Exception as e:
    print(f"Error: {e}")
