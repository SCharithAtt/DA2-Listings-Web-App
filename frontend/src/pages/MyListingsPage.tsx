import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

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
}

export const MyListingsPage: React.FC = () => {
  const [listings, setListings] = useState<Listing[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const { token } = useAuth()

  useEffect(() => {
    loadMyListings()
  }, [])

  const loadMyListings = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await fetch(`${API_URL}/listings/me`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      })

      const data = await res.json()

      if (!res.ok) {
        // Handle validation errors
        if (data?.detail) {
          if (Array.isArray(data.detail)) {
            const errors = data.detail.map((err: any) => `${err.loc.join('.')}: ${err.msg}`).join(', ')
            throw new Error(errors)
          } else if (typeof data.detail === 'string') {
            throw new Error(data.detail)
          } else {
            throw new Error(JSON.stringify(data.detail))
          }
        }
        throw new Error('Failed to load listings')
      }

      setListings(Array.isArray(data) ? data : [])
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (listingId: string) => {
    if (!confirm('Are you sure you want to delete this listing?')) {
      return
    }

    try {
      const res = await fetch(`${API_URL}/listings/${listingId}`, {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${token}`
        }
      })

      if (!res.ok) {
        const data = await res.json()
        throw new Error(data?.detail || 'Failed to delete listing')
      }

      // Remove from list
      setListings(listings.filter(l => l._id !== listingId))
    } catch (err: any) {
      alert(`Error: ${err.message}`)
    }
  }

  const handleUploadImage = async (listingId: string, file: File) => {
    try {
      const formData = new FormData()
      formData.append('file', file)

      const res = await fetch(`${API_URL}/listings/${listingId}/images`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`
        },
        body: formData
      })

      const data = await res.json()

      if (!res.ok) {
        throw new Error(data?.detail || 'Failed to upload image')
      }

      // Update listing with new image
      setListings(listings.map(l => 
        l._id === listingId 
          ? { ...l, images: [...l.images, data.url] }
          : l
      ))
    } catch (err: any) {
      alert(`Error: ${err.message}`)
    }
  }

  if (loading) {
    return (
      <div className="page">
        <div className="loading">Loading your listings...</div>
      </div>
    )
  }

  return (
    <div className="page">
      <div className="page-header">
        <h2>My Listings</h2>
        <Link to="/create" className="btn btn-primary">
          Create New Listing
        </Link>
      </div>

      {error && <div className="error-message">{error}</div>}

      {listings.length === 0 ? (
        <div className="empty-state">
          <p>You haven't created any listings yet.</p>
          <Link to="/create" className="btn btn-primary">
            Create Your First Listing
          </Link>
        </div>
      ) : (
        <div className="listings-grid">
          {listings.map((listing) => (
            <div key={listing._id} className="listing-card my-listing-card">
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
                    {listing.tags.map((tag) => (
                      <span key={tag} className="tag">{tag}</span>
                    ))}
                  </div>
                )}

                <div className="listing-dates">
                  <small>Expires: {new Date(listing.expires_at).toLocaleDateString()}</small>
                </div>

                <div className="listing-actions">
                  <Link to={`/listing/${listing._id}`} className="btn btn-secondary btn-sm">
                    View
                  </Link>
                  
                  <label className="btn btn-secondary btn-sm" style={{ cursor: 'pointer' }}>
                    Add Image
                    <input
                      type="file"
                      accept="image/*"
                      style={{ display: 'none' }}
                      onChange={(e) => {
                        const file = e.target.files?.[0]
                        if (file) {
                          handleUploadImage(listing._id, file)
                          e.currentTarget.value = ''
                        }
                      }}
                    />
                  </label>

                  <button
                    onClick={() => handleDelete(listing._id)}
                    className="btn btn-danger btn-sm"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
