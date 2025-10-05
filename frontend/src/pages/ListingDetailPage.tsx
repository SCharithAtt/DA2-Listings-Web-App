import React, { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
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
  expires_at: string
  features: string[]
  location: {
    coordinates: [number, number]
  }
}

export const ListingDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [listing, setListing] = useState<Listing | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [currentImageIndex, setCurrentImageIndex] = useState(0)

  useEffect(() => {
    if (id) {
      loadListing()
    }
  }, [id])

  const loadListing = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await fetch(`${API_URL}/listings/${id}`)
      const data = await res.json()

      if (!res.ok) {
        throw new Error(data?.detail || 'Failed to load listing')
      }

      setListing(data)
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="page">
        <div className="loading">Loading listing...</div>
      </div>
    )
  }

  if (error || !listing) {
    return (
      <div className="page">
        <div className="error-message">{error || 'Listing not found'}</div>
        <button onClick={() => navigate('/')} className="btn btn-primary">
          Go Back Home
        </button>
      </div>
    )
  }

  const nextImage = () => {
    if (listing.images && listing.images.length > 0) {
      setCurrentImageIndex((prev) => (prev + 1) % listing.images.length)
    }
  }

  const prevImage = () => {
    if (listing.images && listing.images.length > 0) {
      setCurrentImageIndex((prev) => (prev - 1 + listing.images.length) % listing.images.length)
    }
  }

  return (
    <div className="page">
      <div className="detail-container">
        <button onClick={() => navigate(-1)} className="btn btn-secondary back-btn">
          ← Back
        </button>

        <div className="detail-content">
          <div className="detail-images">
            {listing.images && listing.images.length > 0 ? (
              <>
                <div className="image-viewer">
                  <img
                    src={resolveImageUrl(listing.images[currentImageIndex])}
                    alt={listing.title}
                    className="detail-main-image"
                  />
                  {listing.images.length > 1 && (
                    <>
                      <button className="image-nav prev" onClick={prevImage}>
                        ‹
                      </button>
                      <button className="image-nav next" onClick={nextImage}>
                        ›
                      </button>
                      <div className="image-indicator">
                        {currentImageIndex + 1} / {listing.images.length}
                      </div>
                    </>
                  )}
                </div>
                {listing.images.length > 1 && (
                  <div className="image-thumbnails">
                    {listing.images.map((img, idx) => (
                      <img
                        key={idx}
                        src={resolveImageUrl(img)}
                        alt={`${listing.title} ${idx + 1}`}
                        className={`thumbnail ${idx === currentImageIndex ? 'active' : ''}`}
                        onClick={() => setCurrentImageIndex(idx)}
                      />
                    ))}
                  </div>
                )}
              </>
            ) : (
              <div className="detail-image-placeholder">No Image Available</div>
            )}
          </div>

          <div className="detail-info">
            <div className="detail-header">
              <h1>{listing.title}</h1>
              <div className="detail-price">{formatPrice(listing.price)}</div>
            </div>

            <div className="detail-meta">
              <span className="meta-item">
                <strong>Category:</strong> {listing.category.replace('_', ' ')}
              </span>
              <span className="meta-item">
                <strong>Location:</strong> {listing.city}
              </span>
              <span className="meta-item">
                <strong>Posted:</strong> {new Date(listing.posted_date).toLocaleDateString()}
              </span>
              <span className="meta-item">
                <strong>Expires:</strong> {new Date(listing.expires_at).toLocaleDateString()}
              </span>
            </div>

            {listing.tags && listing.tags.length > 0 && (
              <div className="detail-tags">
                {listing.tags.map((tag) => (
                  <span key={tag} className="tag">{tag}</span>
                ))}
              </div>
            )}

            <div className="detail-description">
              <h3>Description</h3>
              <p>{listing.description}</p>
            </div>

            {listing.features && listing.features.length > 0 && (
              <div className="detail-features">
                <h3>Features</h3>
                <ul>
                  {listing.features.map((feature, idx) => (
                    <li key={idx}>{feature}</li>
                  ))}
                </ul>
              </div>
            )}

            {listing.location && (
              <div className="detail-location">
                <h3>Location</h3>
                <p>
                  Coordinates: {listing.location.coordinates[1].toFixed(4)}, {listing.location.coordinates[0].toFixed(4)}
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
