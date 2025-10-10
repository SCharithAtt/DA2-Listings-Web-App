import React, { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { resolveImageUrl, formatPrice } from '../utils/imageHelper'
import { getCityNames, getCityCoordinates } from '../utils/cities'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

type SortOption = 'similarity' | 'date_desc' | 'date_asc' | 'price_asc' | 'price_desc'

interface Listing {
  _id: string
  title: string
  description: string
  price: number
  city: string
  category: string
  tags: string[]
  images: string[]
  score?: number
}

export const SearchResultsPage: React.FC = () => {
  const [searchParams] = useSearchParams()
  const [results, setResults] = useState<Listing[]>([])
  const [sortBy, setSortBy] = useState<SortOption>('similarity')
  const [minPrice, setMinPrice] = useState<string>('')
  const [maxPrice, setMaxPrice] = useState<string>('')
  const [selectedCity, setSelectedCity] = useState<string>('')
  const [radius, setRadius] = useState<string>('10')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const query = searchParams.get('q') || ''
  const mode = searchParams.get('mode') || 'smart' // 'smart' or 'keyword'
  const city = searchParams.get('city') || ''
  const category = searchParams.get('category') || ''
  const tags = searchParams.get('tags') || ''

  const isSmartSearch = mode === 'smart'

  useEffect(() => {
    if (query) {
      performSearch()
    }
  }, [query, mode, city, category, tags, sortBy, minPrice, maxPrice, selectedCity, radius])

  const performSearch = async () => {
    setLoading(true)
    setError(null)

    try {
      const params = new URLSearchParams()
      if (query) params.append('q', query)
      if (city) params.append('city', city)
      if (category) params.append('category', category)
      if (tags) params.append('tags', tags)
      if (minPrice) params.append('min_price', minPrice)
      if (maxPrice) params.append('max_price', maxPrice)
      params.append('sort_by', sortBy)
      
      // Add location filter if city is selected
      if (selectedCity) {
        const coords = getCityCoordinates(selectedCity)
        if (coords) {
          params.append('lat', coords.lat.toString())
          params.append('lng', coords.lng.toString())
          params.append('radius', (parseFloat(radius) * 1000).toString()) // Convert km to meters
        }
      }

      // Choose endpoint based on search mode
      let endpoint: string
      if (isSmartSearch) {
        // Use hybrid search for smart mode (combines text + semantic)
        endpoint = `${API_URL}/listings/search/hybrid?${params.toString()}`
      } else {
        // Use advanced text search for keyword mode
        endpoint = `${API_URL}/listings/search/advanced?${params.toString()}`
      }

      console.log(`🔍 Search mode: ${mode}, endpoint: ${endpoint}`)

      const res = await fetch(endpoint)
      const data = await res.json()

      if (!res.ok) {
        // If hybrid/semantic search fails, fall back to text search
        if (isSmartSearch) {
          console.log('Smart search not available, falling back to keyword search')
          const fallbackEndpoint = `${API_URL}/listings/search/advanced?${params.toString()}`
          const fallbackRes = await fetch(fallbackEndpoint)
          const fallbackData = await fallbackRes.json()
          
          if (!fallbackRes.ok) {
            throw new Error(fallbackData?.detail || 'Search failed')
          }
          
          setResults(Array.isArray(fallbackData) ? fallbackData : [])
          return
        }
        throw new Error(data?.detail || 'Search failed')
      }

      setResults(Array.isArray(data) ? data : [])
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page">
      <div className="search-header">
        <h2>Search Results</h2>
        <p className="search-query">
          Searching for: <strong>{query}</strong>
          {isSmartSearch ? (
            <span className="badge" style={{background: '#e8f1ff', color: '#2563eb', marginLeft: '8px'}}>
              🧠 Smart Search (understands synonyms)
            </span>
          ) : (
            <span className="badge" style={{background: '#f3f4f6', color: '#4b5563', marginLeft: '8px'}}>
              🔍 Keyword Search (exact matches)
            </span>
          )}
        </p>
      </div>

      <div className="price-filter-section">
        <h3>💰 Filter by Price</h3>
        <div className="price-filter-controls">
          <div className="price-input-group">
            <label htmlFor="min-price-search">Min Price (Rs)</label>
            <input
              id="min-price-search"
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
            <label htmlFor="max-price-search">Max Price (Rs)</label>
            <input
              id="max-price-search"
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
            <label htmlFor="city-select-search">City</label>
            <select
              id="city-select-search"
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
              <label htmlFor="radius-input-search">Radius (km)</label>
              <input
                id="radius-input-search"
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

      {loading ? (
        <div className="loading">Searching...</div>
      ) : error ? (
        <div className="error-message">{error}</div>
      ) : results.length === 0 ? (
        <div className="empty-state">
          <p>No results found for "{query}"</p>
          <p className="empty-subtitle">Try different keywords or check your spelling</p>
          <Link to="/" className="btn btn-primary">
            Back to Home
          </Link>
        </div>
      ) : (
        <>
          <div className="section-header">
            <div className="results-count">
              Found {results.length} listing{results.length !== 1 ? 's' : ''}
            </div>
            <div className="sort-controls">
              <label htmlFor="sort-select">Sort by:</label>
              <select
                id="sort-select"
                className="sort-select"
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as SortOption)}
              >
                <option value="similarity">Best Match</option>
                <option value="date_desc">Newest First</option>
                <option value="date_asc">Oldest First</option>
                <option value="price_asc">Price: Low to High</option>
                <option value="price_desc">Price: High to Low</option>
              </select>
            </div>
          </div>
          <div className="listings-grid">
            {results.map((listing) => (
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
                  <p className="listing-description">
                    {listing.description.substring(0, 100)}...
                  </p>
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
                  {typeof listing.score === 'number' && (
                    <div className="listing-score">
                      <small>Relevance: {(listing.score * 100).toFixed(0)}%</small>
                    </div>
                  )}
                </div>
              </Link>
            ))}
          </div>
        </>
      )}
    </div>
  )
}
