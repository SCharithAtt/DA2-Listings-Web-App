# Quick cURL Commands - Copy & Paste

## 1. Login First (Get Token)
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"admin@listings.app\",\"password\":\"admin123\"}"
```

**Copy the access_token from response and use it below**

---

## 2. Create Listing (Replace YOUR_TOKEN_HERE)

### Example 1: iPhone Listing
```bash
curl -X POST http://localhost:8000/listings \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "title": "iPhone 13 Pro - 128GB",
    "description": "Brand new iPhone 13 Pro in Sierra Blue color. 128GB storage, unlocked.",
    "price": 285000,
    "city": "Colombo",
    "category": "electronics",
    "lat": 6.9271,
    "lng": 79.8612,
    "tags": ["iphone", "smartphone", "apple"],
    "features": ["5G", "128GB", "Unlocked"],
    "expiry_days": 30
  }'
```

### Example 2: Car Listing
```bash
curl -X POST http://localhost:8000/listings \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "title": "Toyota Aqua 2019",
    "description": "Well-maintained hybrid vehicle. Single owner, 45000km.",
    "price": 4250000,
    "city": "Gampaha",
    "category": "vehicles",
    "lat": 7.0873,
    "lng": 80.0175,
    "tags": ["toyota", "aqua", "hybrid"],
    "features": ["Hybrid", "45000km", "Single Owner"],
    "expiry_days": 90
  }'
```

### Example 3: House Listing
```bash
curl -X POST http://localhost:8000/listings \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "title": "3 Bedroom House - Kandy",
    "description": "Spacious house in prime location. 1500 sqft, modern kitchen.",
    "price": 15000000,
    "city": "Kandy",
    "category": "real_estate",
    "lat": 7.2906,
    "lng": 80.6337,
    "tags": ["house", "3-bedroom", "kandy"],
    "features": ["3 Bedrooms", "1500 sqft", "Parking"],
    "expiry_days": 90
  }'
```

### Example 4: Minimal Listing
```bash
curl -X POST http://localhost:8000/listings \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "title": "Mountain Bike",
    "description": "Good condition mountain bike",
    "price": 15000,
    "city": "Colombo",
    "category": "sports",
    "lat": 6.9271,
    "lng": 79.8612
  }'
```

---

## 3. Add Image (After Creating - Replace LISTING_ID and YOUR_TOKEN)

### Via URL
```bash
curl -X POST "http://localhost:8000/listings/LISTING_ID/images/url?image_url=https://picsum.photos/400/300" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Via File Upload
```bash
curl -X POST http://localhost:8000/listings/LISTING_ID/images/upload \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -F "file=@/path/to/image.jpg"
```

---

## Quick Test (One-Liner with Login)

**PowerShell:**
```powershell
$token = (Invoke-RestMethod -Uri "http://localhost:8000/auth/login" -Method POST -Body '{"email":"admin@listings.app","password":"admin123"}' -ContentType "application/json").access_token; Invoke-RestMethod -Uri "http://localhost:8000/listings" -Method POST -Headers @{"Authorization"="Bearer $token"; "Content-Type"="application/json"} -Body '{"title":"Test Item","description":"Quick test","price":10000,"city":"Colombo","category":"other","lat":6.9271,"lng":79.8612}'
```

**Bash:**
```bash
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login -H "Content-Type: application/json" -d '{"email":"admin@listings.app","password":"admin123"}' | grep -o '"access_token":"[^"]*' | cut -d'"' -f4) && curl -X POST http://localhost:8000/listings -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN" -d '{"title":"Test Item","description":"Quick test","price":10000,"city":"Colombo","category":"other","lat":6.9271,"lng":79.8612}'
```

---

## Valid Categories
```
electronics, vehicles, real_estate, jobs, services,
furniture, clothing, books, sports, pets, toys,
home_garden, health_beauty, food_beverages, other
```

## Valid Cities (Sample)
```
Colombo, Gampaha, Kalutara, Kandy, Matale, Galle,
Matara, Jaffna, Kurunegala, Anuradhapura, Ratnapura
```

---

## Using in Postman

1. **Import as cURL**: Copy any curl command above
2. **Postman** → Import → Raw Text → Paste
3. Click Import
4. Replace `YOUR_TOKEN_HERE` with actual token
5. Send!
