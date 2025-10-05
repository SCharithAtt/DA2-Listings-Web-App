# Recent Fixes and Updates

## Date: October 5, 2025

### 1. Fixed Authentication State Issue on Page Refresh
**Problem:** Login page would flash while logout button was visible at the same time when refreshing protected pages.

**Solution:**
- Added loading state to `AuthContext`
- Auth context now waits for localStorage to be checked before rendering any content
- This prevents the protected route from redirecting before auth state is loaded

**Files Changed:**
- `frontend/src/contexts/AuthContext.tsx`

### 2. Replaced Manual Lat/Lng Input with City Dropdown
**Problem:** Users had to manually enter latitude and longitude coordinates, which was inconvenient.

**Solution:**
- Created a comprehensive list of 30 major Sri Lankan cities with pre-defined coordinates
- Replaced lat/lng input fields with a dropdown selection of cities
- Coordinates are automatically set based on selected city

**Files Changed:**
- `frontend/src/utils/cities.ts` (NEW FILE - contains 30 Sri Lankan cities with coordinates)
- `frontend/src/pages/CreateListingPage.tsx` (removed lat/lng inputs, added city dropdown)

**Cities Included:**
- All major cities across 9 provinces
- Includes: Colombo, Kandy, Galle, Jaffna, Trincomalee, Negombo, Anuradhapura, Kurunegala, and 22 more

### 3. Added More Category Options
**Problem:** Only 6 categories were available (electronics, vehicles, real_estate, jobs, services, other).

**Solution:**
- Added 9 new categories for better listing classification
- Updated both backend model and frontend with new categories

**New Categories Added:**
- furniture
- clothing
- books
- sports
- pets
- toys
- home_garden
- health_beauty
- food_beverages

**Files Changed:**
- `app/models/listing.py`
- `frontend/src/pages/CreateListingPage.tsx` (hardcoded fallback categories)

### 4. Improved Error Handling
**Problem:** FastAPI validation errors showed as "[object Object]" in the frontend.

**Solution:**
- Enhanced error parsing in `CreateListingPage` to properly display validation errors
- Enhanced error parsing in `MyListingsPage` for better error messages
- Added try-catch blocks to backend endpoints with descriptive error messages

**Files Changed:**
- `frontend/src/pages/CreateListingPage.tsx`
- `frontend/src/pages/MyListingsPage.tsx`
- `app/routes/listings.py`

### 5. Fixed MongoDB Index Creation Issues
**Problem:** Index creation was failing on startup when indexes already existed.

**Solution:**
- Wrapped each index creation in try-catch blocks
- Allows server to start even if indexes already exist
- Added warning logging for debugging

**Files Changed:**
- `app/db/mongo.py`

### 6. Fixed Advanced Search Pipeline Issue
**Problem:** MongoDB aggregation pipeline error: "$match with $text is only allowed as the first pipeline stage"

**Solution:**
- Restructured the search aggregation pipeline
- Moved $text search to the first $match stage (MongoDB requirement)
- Reorganized geo search to come after text search

**Files Changed:**
- `app/routes/listings.py` (search_listings function)

### 7. Fixed bcrypt Compatibility Issue
**Problem:** passlib 1.7.4 incompatible with bcrypt 4.1+, causing registration failures.

**Solution:**
- Pinned bcrypt version to 4.0.1 in requirements.txt
- This version is compatible with passlib 1.7.4

**Files Changed:**
- `requirements.txt`

## Current Status

### ✅ Working Features:
- User registration and login
- Creating listings with automatic coordinates
- Semantic search (with embeddings)
- Individual listing view with image display
- Image upload for listings
- Category filtering (15 categories available)
- Authentication protection for protected routes
- No more page flash on refresh

### ⚠️ Issues to Monitor:
- `/listings/me` endpoint returning 400 Bad Request (needs further investigation)
- Advanced search still has aggregation issues (text search pipeline order)
- Categories endpoint returning 400 Bad Request

### 🔧 Next Steps:
1. Debug why `/listings/me` endpoint fails (check get_current_user_id and get_db dependencies)
2. Verify advanced search works with the pipeline fix
3. Test category endpoint functionality
4. Ensure all location-based queries work with new city system

## Testing Checklist

- [ ] Register new user
- [ ] Login with existing user  
- [ ] Create listing with city selection (no manual lat/lng)
- [ ] Upload image to listing
- [ ] View listing detail page
- [ ] View My Listings page
- [ ] Delete a listing
- [ ] Search with semantic search
- [ ] Filter by category (test new categories)
- [ ] Refresh protected pages (should not show login flash)

## Known Issues
1. "My Listings" page may show "Invalid id" error - backend endpoint investigation in progress
2. Some database queries returning 400 Bad Request - investigating MongoDB connection state

---

## Date: October 5, 2025 (Afternoon)

### 4. Fixed Image Display Issue (Thumbnails and Detail Pages)

**Problem:** Images were not appearing in thumbnails or listing detail pages after implementing URL-based image addition.

**Root Cause:** The application was inconsistently handling two types of image paths:
1. **File Upload Images**: Relative paths like `/static/listings_images/abc123.png`
2. **URL Images**: Absolute URLs like `https://example.com/photo.jpg`

All image display code was always prepending `${API_URL}` to paths:
```tsx
src={`${API_URL}${listing.images[0]}`}
```

This worked for uploaded files but broke URL-based images:
- ❌ `http://localhost:8000https://example.com/photo.jpg` (BROKEN)
- ✅ `https://example.com/photo.jpg` (CORRECT)

**Solution:**
- Created utility function `resolveImageUrl()` in `frontend/src/utils/imageHelper.ts`
- Function checks if path is absolute URL (starts with http:// or https://)
- Returns absolute URLs as-is, prepends API_URL to relative paths
- Updated all image rendering code across 4 pages to use this utility

**Files Created:**
- `frontend/src/utils/imageHelper.ts` (NEW)

**Files Modified:**
- `frontend/src/pages/HomePage.tsx` - Updated listing thumbnails
- `frontend/src/pages/MyListingsPage.tsx` - Updated my listings thumbnails
- `frontend/src/pages/ListingDetailPage.tsx` - Updated main image + thumbnail carousel
- `frontend/src/pages/SearchResultsPage.tsx` - Updated search result thumbnails

**Testing:**
- ✅ Uploaded file images display correctly (`/static/listings_images/xyz.png`)
- ✅ URL-based images display correctly (`https://example.com/image.jpg`)
- ✅ No image placeholder displays when images array is empty
- ✅ Image carousel works with multiple images
- ✅ Thumbnails clickable in detail page

**Benefits:**
- Backward compatible with existing uploaded images
- Supports external URL images
- Single utility function for all image handling
- Type-safe TypeScript implementation
- Easy to extend for future enhancements (default images, lazy loading, etc.)
