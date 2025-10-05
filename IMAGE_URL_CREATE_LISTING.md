# Image URL Support in Create Listing Page

## Summary
Added the ability to add images via URL during listing creation, in addition to the existing file upload option.

## Changes Made

### CreateListingPage.tsx

**New State Variables:**
```typescript
const [imageUrl, setImageUrl] = useState('')
const [imageUrlPreview, setImageUrlPreview] = useState<string | null>(null)
```

**New Handler Function:**
```typescript
const handleImageUrlChange = (e: React.ChangeEvent<HTMLInputElement>) => {
  const url = e.target.value
  setImageUrl(url)
  
  // Clear file input if URL is entered
  if (url.trim()) {
    setImageFile(null)
    setImagePreview(null)
  }
  
  // Show preview if it's a valid URL
  if (url.startsWith('http://') || url.startsWith('https://')) {
    setImageUrlPreview(url)
  } else {
    setImageUrlPreview(null)
  }
}
```

**Updated handleImageChange:**
- Clears URL input when file is selected
- Ensures only one image method is active at a time

**Updated Submit Handler:**
- Uploads file if provided (existing functionality)
- Adds URL if provided (new functionality)
- Calls both `/images/upload` and `/images/url` endpoints as needed

**New UI Elements:**
```tsx
<div className="form-group">
  <label htmlFor="imageUrl">Or Add Image via URL</label>
  <input
    id="imageUrl"
    type="url"
    className="input"
    placeholder="https://example.com/image.jpg"
    value={imageUrl}
    onChange={handleImageUrlChange}
  />
  <small>Enter a direct image URL (must start with http:// or https://)</small>
  {imageUrlPreview && (
    <div className="image-preview">
      <img src={imageUrlPreview} alt="URL Preview" onError={() => setImageUrlPreview(null)} />
    </div>
  )}
</div>
```

---

## Features

### ✅ Mutually Exclusive Input
- Selecting a file clears the URL input
- Entering a URL clears the file input
- Only one image source active at a time

### ✅ Live Preview
- File upload: Shows preview after file selection
- URL input: Shows preview when valid URL entered
- Preview updates in real-time
- Error handling: Invalid image URLs won't break the UI

### ✅ Validation
- URL must start with `http://` or `https://`
- Preview only shows for valid URLs
- Form submits successfully even if preview fails
- Backend validates URL format as well

### ✅ User Experience
- Clear label: "Or Add Image via URL"
- Helper text explains URL requirements
- Placeholder shows example URL format
- Seamless integration with existing file upload

---

## User Workflow

### Option 1: File Upload (Existing)
1. Click "Choose File" button
2. Select image from computer
3. Preview appears
4. Submit creates listing with uploaded image

### Option 2: Image URL (New)
1. Enter image URL in text field
2. Preview appears if URL is valid
3. Submit creates listing with image URL

### Option 3: No Image (Existing)
1. Leave both fields empty
2. Submit creates listing without image
3. Can add images later from My Listings

---

## Backend Integration

**File Upload:**
```typescript
if (imageFile) {
  const formData = new FormData()
  formData.append('file', imageFile)
  
  await fetch(`${API_URL}/listings/${listingId}/images/upload`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}` },
    body: formData
  })
}
```

**URL Addition:**
```typescript
if (imageUrl.trim() && (imageUrl.startsWith('http://') || imageUrl.startsWith('https://'))) {
  await fetch(
    `${API_URL}/listings/${listingId}/images/url?image_url=${encodeURIComponent(imageUrl)}`,
    {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` }
    }
  )
}
```

---

## Testing Checklist

- [ ] **Test File Upload Only**
  - Select file, leave URL empty
  - Preview appears for file
  - Submit successful
  - Image displays in listing

- [ ] **Test URL Only**
  - Enter URL: `https://picsum.photos/400/300`
  - Preview appears
  - Submit successful
  - Image displays in listing

- [ ] **Test File Then URL**
  - Select file (preview appears)
  - Enter URL (file clears, URL preview appears)
  - Submit uses URL

- [ ] **Test URL Then File**
  - Enter URL (preview appears)
  - Select file (URL clears, file preview appears)
  - Submit uses file

- [ ] **Test No Image**
  - Leave both empty
  - Submit successful
  - Listing created without image

- [ ] **Test Invalid URL**
  - Enter: `not-a-url`
  - No preview appears
  - Form still submits (no image added)

- [ ] **Test Image Error**
  - Enter URL of non-existent image
  - Preview fails gracefully
  - Form still submits

---

## Benefits

✅ **Flexibility**: Users can choose file upload OR URL
✅ **Convenience**: No need to download images to upload them
✅ **Speed**: URL addition is faster than file upload
✅ **Bandwidth**: Saves upload bandwidth for URL images
✅ **User-Friendly**: Clear separation between two input methods
✅ **Error-Tolerant**: Invalid URLs don't break the form
✅ **Backward Compatible**: Existing file upload still works perfectly

---

## Example URLs for Testing

**Valid Image URLs:**
```
https://picsum.photos/400/300
https://images.unsplash.com/photo-1234567890/photo.jpg
https://via.placeholder.com/400x300
```

**Test Cases:**
- Large image URL
- Small image URL
- Image with special characters in URL
- Image from different domain
- HTTPS vs HTTP URLs

---

## Future Enhancements (Optional)

- [ ] Allow multiple URL inputs
- [ ] Add URL validation check before submit
- [ ] Show loading indicator while preview loads
- [ ] Add "Test URL" button to verify image exists
- [ ] Support image URLs from specific platforms (Instagram, etc.)
- [ ] Add image size/dimension validation
