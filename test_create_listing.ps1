# Create Listing API Test Script
# Run this in PowerShell after logging in

Write-Host "=== Create Listing API Test ===" -ForegroundColor Cyan
Write-Host ""

# Configuration
$API_URL = "http://localhost:8000"
$EMAIL = "admin@listings.app"
$PASSWORD = "admin123"

# Step 1: Login to get token
Write-Host "Step 1: Logging in..." -ForegroundColor Yellow
$loginBody = @{
    email = $EMAIL
    password = $PASSWORD
} | ConvertTo-Json

try {
    $loginResponse = Invoke-RestMethod -Uri "$API_URL/auth/login" -Method POST -Body $loginBody -ContentType "application/json"
    $TOKEN = $loginResponse.access_token
    Write-Host "✓ Login successful!" -ForegroundColor Green
    Write-Host "  Token: $($TOKEN.Substring(0, 20))..." -ForegroundColor Gray
} catch {
    Write-Host "✗ Login failed: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Step 2: Create Listing
Write-Host "Step 2: Creating listing..." -ForegroundColor Yellow

$listingBody = @{
    title = "iPhone 13 Pro - 128GB (Test Listing)"
    description = "Brand new iPhone 13 Pro in Sierra Blue color. 128GB storage, unlocked, with original box and accessories. Never used, still in sealed packaging. This is a test listing created via API."
    price = 285000
    city = "Colombo"
    category = "electronics"
    lat = 6.9271
    lng = 79.8612
    tags = @("iphone", "smartphone", "apple", "unlocked", "test")
    features = @("5G", "128GB", "Sierra Blue", "Unlocked", "Face ID")
    expiry_days = 30
} | ConvertTo-Json

$headers = @{
    "Content-Type" = "application/json"
    "Authorization" = "Bearer $TOKEN"
}

try {
    $listingResponse = Invoke-RestMethod -Uri "$API_URL/listings" -Method POST -Body $listingBody -Headers $headers
    Write-Host "✓ Listing created successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Listing Details:" -ForegroundColor Cyan
    Write-Host "  ID: $($listingResponse._id)" -ForegroundColor White
    Write-Host "  Title: $($listingResponse.title)" -ForegroundColor White
    Write-Host "  Price: Rs $($listingResponse.price.ToString('N0'))" -ForegroundColor White
    Write-Host "  City: $($listingResponse.city)" -ForegroundColor White
    Write-Host "  Category: $($listingResponse.category)" -ForegroundColor White
    Write-Host "  Posted: $($listingResponse.posted_date)" -ForegroundColor White
    Write-Host "  Expires: $($listingResponse.expires_at)" -ForegroundColor White
    Write-Host ""
    
    $LISTING_ID = $listingResponse._id
    
    # Step 3: Add image via URL (optional)
    Write-Host "Step 3: Adding image via URL..." -ForegroundColor Yellow
    $imageUrl = "https://picsum.photos/400/300"
    
    try {
        $imageResponse = Invoke-RestMethod -Uri "$API_URL/listings/$LISTING_ID/images/url?image_url=$imageUrl" -Method POST -Headers $headers
        Write-Host "✓ Image added successfully!" -ForegroundColor Green
        Write-Host "  Image URL: $imageUrl" -ForegroundColor White
    } catch {
        Write-Host "✗ Image addition failed: $_" -ForegroundColor Red
    }
    
    Write-Host ""
    Write-Host "=== Test Complete ===" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "View your listing at: http://localhost:5173/listing/$LISTING_ID" -ForegroundColor Green
    Write-Host "Or view in My Listings: http://localhost:5173/my-listings" -ForegroundColor Green
    
} catch {
    Write-Host "✗ Listing creation failed!" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
    
    if ($_.ErrorDetails) {
        Write-Host ""
        Write-Host "Details:" -ForegroundColor Yellow
        Write-Host $_.ErrorDetails.Message -ForegroundColor Gray
    }
}
