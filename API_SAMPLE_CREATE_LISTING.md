# API Sample: Create Listing

## Endpoint
```
POST http://localhost:8000/listings
```

## Authentication
**Required**: Yes (Bearer Token)

```
Authorization: Bearer YOUR_JWT_TOKEN_HERE
```

## Request Headers
```
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## Request Body Schema

```json
{
  "title": "string (required)",
  "description": "string (required)",
  "price": "number (required, >= 0)",
  "city": "string (required)",
  "category": "string (required, enum)",
  "lat": "number (required, -90 to 90)",
  "lng": "number (required, -180 to 180)",
  "tags": ["array of strings (optional)"],
  "features": ["array of strings (optional)"],
  "expiry_days": "number (optional, 7|14|30|90, default: 30)"
}
```

### Required Fields
- `title` - Listing title
- `description` - Detailed description
- `price` - Price in LKR (must be >= 0)
- `city` - City name (must be valid Sri Lankan city)
- `category` - Category from allowed list
- `lat` - Latitude coordinate
- `lng` - Longitude coordinate

### Optional Fields
- `tags` - Array of tag strings (e.g., ["smartphone", "android"])
- `features` - Array of feature strings (e.g., ["WiFi", "Bluetooth"])
- `expiry_days` - Listing expiry (7, 14, 30, or 90 days)

### Valid Categories
```
electronics, vehicles, real_estate, jobs, services,
furniture, clothing, books, sports, pets, toys,
home_garden, health_beauty, food_beverages, other
```

### Valid Cities (Sample)
```
Colombo, Gampaha, Kalutara, Kandy, Matale, Nuwara Eliya,
Galle, Matara, Hambantota, Jaffna, Kilinochchi, Mannar,
Vavuniya, Mullaitivu, Batticaloa, Ampara, Trincomalee,
Kurunegala, Puttalam, Anuradhapura, Polonnaruwa,
Badulla, Monaragala, Ratnapura, Kegalle
```

---

## Sample Request 1: Basic Listing (Electronics)

### cURL
```bash
curl -X POST http://localhost:8000/listings \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "title": "iPhone 13 Pro - 128GB",
    "description": "Brand new iPhone 13 Pro in Sierra Blue color. 128GB storage, unlocked, with original box and accessories. Never used, still in sealed packaging.",
    "price": 285000,
    "city": "Colombo",
    "category": "electronics",
    "lat": 6.9271,
    "lng": 79.8612,
    "tags": ["iphone", "smartphone", "apple", "unlocked"],
    "features": ["5G", "128GB", "Sierra Blue", "Unlocked"],
    "expiry_days": 30
  }'
```

### JavaScript (Fetch)
```javascript
const response = await fetch('http://localhost:8000/listings', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({
    title: "iPhone 13 Pro - 128GB",
    description: "Brand new iPhone 13 Pro in Sierra Blue color. 128GB storage, unlocked, with original box and accessories.",
    price: 285000,
    city: "Colombo",
    category: "electronics",
    lat: 6.9271,
    lng: 79.8612,
    tags: ["iphone", "smartphone", "apple", "unlocked"],
    features: ["5G", "128GB", "Sierra Blue", "Unlocked"],
    expiry_days: 30
  })
});

const data = await response.json();
console.log('Listing created:', data);
```

### Python (requests)
```python
import requests

url = "http://localhost:8000/listings"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {token}"
}
payload = {
    "title": "iPhone 13 Pro - 128GB",
    "description": "Brand new iPhone 13 Pro in Sierra Blue color.",
    "price": 285000,
    "city": "Colombo",
    "category": "electronics",
    "lat": 6.9271,
    "lng": 79.8612,
    "tags": ["iphone", "smartphone", "apple", "unlocked"],
    "features": ["5G", "128GB", "Sierra Blue", "Unlocked"],
    "expiry_days": 30
}

response = requests.post(url, json=payload, headers=headers)
listing = response.json()
print(f"Created listing ID: {listing['_id']}")
```

---

## Sample Request 2: Vehicle Listing

```json
{
  "title": "Toyota Aqua 2019 - Excellent Condition",
  "description": "Well-maintained Toyota Aqua hybrid vehicle. Single owner, full service history available. 45,000 km driven. Excellent fuel efficiency.",
  "price": 4250000,
  "city": "Gampaha",
  "category": "vehicles",
  "lat": 7.0873,
  "lng": 80.0175,
  "tags": ["toyota", "aqua", "hybrid", "low-mileage"],
  "features": ["Hybrid", "45000km", "Single Owner", "Full Service History"],
  "expiry_days": 90
}
```

---

## Sample Request 3: Real Estate Listing

```json
{
  "title": "3 Bedroom House for Sale - Kandy",
  "description": "Spacious 3-bedroom house in prime location in Kandy. 1500 sq ft, modern kitchen, 2 bathrooms, parking for 2 vehicles. Close to schools and hospitals.",
  "price": 15000000,
  "city": "Kandy",
  "category": "real_estate",
  "lat": 7.2906,
  "lng": 80.6337,
  "tags": ["house", "3-bedroom", "kandy", "parking"],
  "features": ["3 Bedrooms", "2 Bathrooms", "1500 sqft", "Parking"],
  "expiry_days": 90
}
```

---

## Sample Request 4: Job Listing

```json
{
  "title": "Software Engineer - Full Stack",
  "description": "We are hiring a full-stack software engineer with 3+ years experience. Must be proficient in React, Node.js, and MongoDB. Competitive salary and benefits package.",
  "price": 150000,
  "city": "Colombo",
  "category": "jobs",
  "lat": 6.9271,
  "lng": 79.8612,
  "tags": ["software", "engineer", "full-stack", "react", "nodejs"],
  "features": ["Remote Work", "Health Insurance", "Annual Bonus"],
  "expiry_days": 30
}
```

---

## Sample Request 5: Minimal Listing (Required Fields Only)

```json
{
  "title": "Used Bicycle for Sale",
  "description": "Mountain bike in good condition. Suitable for adults.",
  "price": 15000,
  "city": "Kandy",
  "category": "sports",
  "lat": 7.2906,
  "lng": 80.6337
}
```

---

## Sample Response (Success)

**Status Code**: `200 OK`

```json
{
  "_id": "671234567890abcdef123456",
  "title": "iPhone 13 Pro - 128GB",
  "description": "Brand new iPhone 13 Pro in Sierra Blue color. 128GB storage, unlocked, with original box and accessories.",
  "price": 285000,
  "city": "Colombo",
  "category": "electronics",
  "tags": ["iphone", "smartphone", "apple", "unlocked"],
  "features": ["5G", "128GB", "Sierra Blue", "Unlocked"],
  "userId": "670987654321abcdef654321",
  "location": {
    "type": "Point",
    "coordinates": [79.8612, 6.9271]
  },
  "posted_date": "2025-10-05T14:30:00.000Z",
  "expires_at": "2025-11-04T14:30:00.000Z",
  "images": []
}
```

---

## Error Responses

### 401 Unauthorized (No/Invalid Token)
```json
{
  "detail": "Not authenticated"
}
```

### 422 Validation Error (Missing Required Fields)
```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "field required",
      "type": "value_error.missing"
    },
    {
      "loc": ["body", "price"],
      "msg": "ensure this value is greater than or equal to 0",
      "type": "value_error.number.not_ge"
    }
  ]
}
```

### 422 Invalid Category
```json
{
  "detail": [
    {
      "loc": ["body", "category"],
      "msg": "value is not a valid enumeration member; permitted: 'electronics', 'vehicles', 'real_estate', ...",
      "type": "type_error.enum"
    }
  ]
}
```

---

## Adding Images After Creation

After creating a listing, you can add images using the listing ID:

### Option 1: Upload Image File
```bash
curl -X POST http://localhost:8000/listings/{listing_id}/images/upload \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@/path/to/image.jpg"
```

### Option 2: Add Image via URL
```bash
curl -X POST "http://localhost:8000/listings/{listing_id}/images/url?image_url=https://example.com/image.jpg" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## Complete Workflow Example

### 1. Login to Get Token
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 2. Create Listing
```bash
curl -X POST http://localhost:8000/listings \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -d '{
    "title": "Samsung Galaxy S23",
    "description": "Latest Samsung flagship phone",
    "price": 195000,
    "city": "Colombo",
    "category": "electronics",
    "lat": 6.9271,
    "lng": 79.8612,
    "tags": ["samsung", "smartphone", "android"]
  }'
```

**Response:**
```json
{
  "_id": "671234567890abcdef123456",
  ...
}
```

### 3. Add Image (Optional)
```bash
curl -X POST "http://localhost:8000/listings/671234567890abcdef123456/images/url?image_url=https://picsum.photos/400/300" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

## Testing with Postman

1. **Create New Request**
   - Method: `POST`
   - URL: `http://localhost:8000/listings`

2. **Add Headers**
   - `Content-Type`: `application/json`
   - `Authorization`: `Bearer YOUR_TOKEN_HERE`

3. **Add Body (raw JSON)**
   ```json
   {
     "title": "Test Listing",
     "description": "This is a test listing",
     "price": 50000,
     "city": "Colombo",
     "category": "electronics",
     "lat": 6.9271,
     "lng": 79.8612
   }
   ```

4. **Send Request**

---

## Notes

- **Authentication Required**: You must be logged in to create listings
- **Coordinates**: Use valid lat/lng for the selected city
- **Price**: Enter amount in Sri Lankan Rupees (LKR)
- **Expiry**: Listings auto-expire after specified days (default 30)
- **Images**: Add images after listing creation using separate endpoints
- **Embedding**: Semantic search embeddings computed automatically in background
- **Validation**: All fields validated server-side

---

## Quick Reference

| Field | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| title | string | ✅ | - | Listing title |
| description | string | ✅ | - | Full description |
| price | number | ✅ | - | Must be >= 0 |
| city | string | ✅ | - | Valid Sri Lankan city |
| category | enum | ✅ | - | See category list |
| lat | number | ✅ | - | -90 to 90 |
| lng | number | ✅ | - | -180 to 180 |
| tags | array | ❌ | [] | Search tags |
| features | array | ❌ | [] | Feature list |
| expiry_days | number | ❌ | 30 | 7, 14, 30, or 90 |
