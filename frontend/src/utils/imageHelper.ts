const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

/**
 * Resolves an image path to a full URL.
 * Handles both:
 * - Relative paths from file uploads (e.g., "/static/listings_images/xyz.png")
 * - Absolute URLs from URL input (e.g., "https://example.com/image.jpg")
 */
export function resolveImageUrl(imagePath: string): string {
  if (!imagePath) {
    return ''
  }
  
  // If it's already an absolute URL (starts with http:// or https://), return as-is
  if (imagePath.startsWith('http://') || imagePath.startsWith('https://')) {
    return imagePath
  }
  
  // If it's a relative path, prepend the API URL
  return `${API_URL}${imagePath}`
}

/**
 * Formats a price value with Sri Lankan Rupee (LKR) currency
 * @param price - The numeric price value
 * @returns Formatted price string with "Rs" prefix and thousand separators
 * @example formatPrice(1500) => "Rs 1,500"
 * @example formatPrice(150000) => "Rs 150,000"
 */
export function formatPrice(price: number): string {
  if (price === 0) {
    return 'Rs 0'
  }
  
  // Format with thousand separators (Sri Lankan style)
  return `Rs ${price.toLocaleString('en-LK')}`
}
