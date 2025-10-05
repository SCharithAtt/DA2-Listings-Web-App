import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { resolveImageUrl, formatPrice } from '../utils/imageHelper'

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
  posted_date: string
}

export const HomePage: React.FC = () => {
  const [latestListings, setLatestListings] = useState<Listing[]>([])
  const [categories, setCategories] = useState<string[]>([])
  const [selectedCategory, setSelectedCategory] = useState<string>('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
  }, [selectedCategory])

  const loadData = async () => {
    setLoading(true)
    try {
      // Load latest listings
      const listingsUrl = selectedCategory 
        ? `${API_URL}/listings?category=${selectedCategory}&limit=12`
        : `${API_URL}/listings/latest?limit=12`
      
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

      <div className="listings-section">
        <h3>{selectedCategory ? `${selectedCategory.replace('_', ' ')} Listings` : 'Latest Listings'}</h3>
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
