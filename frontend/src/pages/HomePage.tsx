import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { resolveImageUrl, formatPrice } from '../utils/imageHelper'
import { getCityNames, getCityCoordinates } from '../utils/cities'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

type SortOption = 'date_desc' | 'date_asc' | 'price_asc' | 'price_desc'

interface Listing {
  _id: string
  title: string
  description: string
  price: number
  city: string
  category: string
  tags: string[]
  images: string[]
  posted_date: string
}

export const HomePage: React.FC = () => {
  const [latestListings, setLatestListings] = useState<Listing[]>([])
  const [categories, setCategories] = useState<string[]>([])
  const [selectedCategory, setSelectedCategory] = useState<string>('')
  const [sortBy, setSortBy] = useState<SortOption>('date_desc')
  const [minPrice, setMinPrice] = useState<string>('')
  const [maxPrice, setMaxPrice] = useState<string>('')
  const [selectedCity, setSelectedCity] = useState<string>('')
  const [radius, setRadius] = useState<string>('10')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
  }, [selectedCategory, sortBy, minPrice, maxPrice, selectedCity, radius])

  const loadData = async () => {
    setLoading(true)
    try {
      // Build URL with filters
      const params = new URLSearchParams()
      params.append('limit', '12')
      params.append('sort_by', sortBy)
      if (selectedCategory) params.append('category', selectedCategory)
      if (minPrice) params.append('min_price', minPrice)
      if (maxPrice) params.append('max_price', maxPrice)
      
      // Add location filter if city is selected
      if (selectedCity) {
        const coords = getCityCoordinates(selectedCity)
        if (coords) {
          params.append('lat', coords.lat.toString())
          params.append('lng', coords.lng.toString())
          params.append('radius', (parseFloat(radius) * 1000).toString()) // Convert km to meters
        }
      }

      // Load latest listings with sorting and filtering
      const listingsUrl = selectedCategory 
        ? `${API_URL}/listings?${params.toString()}`
        : `${API_URL}/listings/latest?${params.toString()}`
      
      const listingsRes = await fetch(listingsUrl)
      const listingsData = await listingsRes.json()
      setLatestListings(Array.isArray(listingsData) ? listingsData : [])

      // Load categories (only once)
      if (categories.length === 0) {
        const categoriesRes = await fetch(`${API_URL}/listings/categories`)
        const categoriesData = await categoriesRes.json()
        setCategories(Array.isArray(categoriesData) ? categoriesData : [])
      }
    } catch (error) {
      console.error('Failed to load data:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page">
      <div className="hero">
        <h1>Find What You Need</h1>
        <p className="hero-subtitle">Browse the latest listings in your area</p>
      </div>

      <div className="categories-section">
        <h3>Browse by Category</h3>
        <div className="categories-grid">
          <button
            className={`category-chip ${!selectedCategory ? 'active' : ''}`}
            onClick={() => setSelectedCategory('')}
          >
            All
          </button>
          {categories.map((cat) => (
            <button
              key={cat}
              className={`category-chip ${selectedCategory === cat ? 'active' : ''}`}
              onClick={() => setSelectedCategory(cat)}
            >
              {cat.replace('_', ' ')}
            </button>
          ))}
        </div>
      </div>

      <div className="price-filter-section">
        <h3>💰 Filter by Price</h3>
        <div className="price-filter-controls">
          <div className="price-input-group">
            <label htmlFor="min-price">Min Price (Rs)</label>
            <input
              id="min-price"
              type="number"
              className="input price-input"
              placeholder="0"
              value={minPrice}
              onChange={(e) => setMinPrice(e.target.value)}
              min="0"
            />
          </div>
          <span className="price-separator">—</span>
          <div className="price-input-group">
            <label htmlFor="max-price">Max Price (Rs)</label>
            <input
              id="max-price"
              type="number"
              className="input price-input"
              placeholder="Any"
              value={maxPrice}
              onChange={(e) => setMaxPrice(e.target.value)}
              min="0"
            />
          </div>
          {(minPrice || maxPrice) && (
            <button
              className="btn btn-secondary btn-clear-filter"
              onClick={() => {
                setMinPrice('')
                setMaxPrice('')
              }}
            >
              Clear
            </button>
          )}
        </div>
      </div>

      <div className="location-filter-section">
        <h3>📍 Filter by Location & Distance</h3>
        <div className="location-filter-controls">
          <div className="location-input-group">
            <label htmlFor="city-select">City</label>
            <select
              id="city-select"
              className="input city-select"
              value={selectedCity}
              onChange={(e) => setSelectedCity(e.target.value)}
            >
              <option value="">All Cities</option>
              {getCityNames().map((city) => (
                <option key={city} value={city}>
                  {city}
                </option>
              ))}
            </select>
          </div>
          {selectedCity && (
            <div className="radius-input-group">
              <label htmlFor="radius-input">Radius (km)</label>
              <input
                id="radius-input"
                type="number"
                className="input radius-input"
                placeholder="10"
                value={radius}
                onChange={(e) => setRadius(e.target.value)}
                min="1"
                max="50"
              />
            </div>
          )}
          {selectedCity && (
            <button
              className="btn btn-secondary btn-clear-filter"
              onClick={() => {
                setSelectedCity('')
                setRadius('10')
              }}
            >
              Clear
            </button>
          )}
        </div>
      </div>

      <div className="listings-section">
        <div className="section-header">
          <h3>{selectedCategory ? `${selectedCategory.replace('_', ' ')} Listings` : 'Latest Listings'}</h3>
          <div className="sort-controls">
            <label htmlFor="sort-select">Sort by:</label>
            <select
              id="sort-select"
              className="sort-select"
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as SortOption)}
            >
              <option value="date_desc">Newest First</option>
              <option value="date_asc">Oldest First</option>
              <option value="price_asc">Price: Low to High</option>
              <option value="price_desc">Price: High to Low</option>
            </select>
          </div>
        </div>
        {loading ? (
          <div className="loading">Loading...</div>
        ) : latestListings.length === 0 ? (
          <div className="empty-state">No listings found</div>
        ) : (
          <div className="listings-grid">
            {latestListings.map((listing) => (
              <Link
                key={listing._id}
                to={`/listing/${listing._id}`}
                className="listing-card"
              >
                {listing.images && listing.images.length > 0 ? (
                  <img
                    src={resolveImageUrl(listing.images[0])}
                    alt={listing.title}
                    className="listing-image"
                  />
                ) : (
                  <div className="listing-image-placeholder">No Image</div>
                )}
                <div className="listing-content">
                  <div className="listing-header">
                    <h4 className="listing-title">{listing.title}</h4>
                    <span className="listing-price">{formatPrice(listing.price)}</span>
                  </div>
                  <p className="listing-description">{listing.description.substring(0, 100)}...</p>
                  <div className="listing-meta">
                    <span className="listing-city">{listing.city}</span>
                    <span className="listing-category">{listing.category}</span>
                  </div>
                  {listing.tags && listing.tags.length > 0 && (
                    <div className="listing-tags">
                      {listing.tags.slice(0, 3).map((tag) => (
                        <span key={tag} className="tag">{tag}</span>
                      ))}
                    </div>
                  )}
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
