import React, { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

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
  const [searchParams, setSearchParams] = useSearchParams()
  const [results, setResults] = useState<Listing[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [useSemanticSearch, setUseSemanticSearch] = useState(true)

  const query = searchParams.get('q') || ''
  const city = searchParams.get('city') || ''
  const category = searchParams.get('category') || ''
  const tags = searchParams.get('tags') || ''

  useEffect(() => {
    if (query) {
      performSearch()
    }
  }, [query, city, category, tags, useSemanticSearch])

  const performSearch = async () => {
    setLoading(true)
    setError(null)

    try {
      const params = new URLSearchParams()
      if (query) params.append('q', query)
      if (city) params.append('city', city)
      if (category) params.append('category', category)
      if (tags) params.append('tags', tags)

      // Use semantic search by default for better typo handling
      const endpoint = useSemanticSearch 
        ? `${API_URL}/listings/search/semantic?${params.toString()}`
        : `${API_URL}/listings/search/advanced?${params.toString()}`

      const res = await fetch(endpoint)
      const data = await res.json()

      if (!res.ok) {
        // If semantic search fails (e.g., not enabled), fall back to advanced search
        if (useSemanticSearch) {
          console.log('Semantic search not available, falling back to advanced search')
          setUseSemanticSearch(false)
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
          {useSemanticSearch && <span className="badge semantic-badge">Smart Search (handles typos)</span>}
        </p>
        
        <div className="search-toggle">
          <label>
            <input
              type="checkbox"
              checked={useSemanticSearch}
              onChange={(e) => setUseSemanticSearch(e.target.checked)}
            />
            Use Smart Search (better with typos)
          </label>
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
          <div className="results-count">
            Found {results.length} listing{results.length !== 1 ? 's' : ''}
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
                    src={`${API_URL}${listing.images[0]}`}
                    alt={listing.title}
                    className="listing-image"
                  />
                ) : (
                  <div className="listing-image-placeholder">No Image</div>
                )}
                <div className="listing-content">
                  <div className="listing-header">
                    <h4 className="listing-title">{listing.title}</h4>
                    <span className="listing-price">${listing.price}</span>
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
