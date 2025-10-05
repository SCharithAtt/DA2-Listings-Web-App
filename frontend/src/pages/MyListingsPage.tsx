import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { getCityNames } from '../utils/cities'
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
}

export const MyListingsPage: React.FC = () => {
  const [listings, setListings] = useState<Listing[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [editForm, setEditForm] = useState<Partial<Listing>>({})
  const [imageUrl, setImageUrl] = useState('')
  const [addingImageTo, setAddingImageTo] = useState<string | null>(null)
  const [newImageUrl, setNewImageUrl] = useState('')
  const [categories] = useState<string[]>([
    'electronics', 'vehicles', 'real_estate', 'jobs', 'services',
    'furniture', 'clothing', 'books', 'sports', 'pets', 'toys',
    'home_garden', 'health_beauty', 'food_beverages', 'other'
  ])
  const [availableCities] = useState<string[]>(getCityNames())
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

      const res = await fetch(`${API_URL}/listings/${listingId}/images/upload`, {
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

  const handleAddImageByUrl = async (listingId: string) => {
    if (!imageUrl.trim()) {
      alert('Please enter an image URL')
      return
    }

    if (!imageUrl.startsWith('http://') && !imageUrl.startsWith('https://')) {
      alert('Please enter a valid URL (must start with http:// or https://)')
      return
    }

    try {
      const res = await fetch(`${API_URL}/listings/${listingId}/images/url?image_url=${encodeURIComponent(imageUrl)}`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`
        }
      })

      const data = await res.json()

      if (!res.ok) {
        throw new Error(data?.detail || 'Failed to add image')
      }

      // Update listing with new image
      setListings(listings.map(l => 
        l._id === listingId 
          ? { ...l, images: [...l.images, imageUrl] }
          : l
      ))

      setImageUrl('')
      setAddingImageTo(null)
      alert('Image URL added successfully!')
    } catch (err: any) {
      alert(`Error: ${err.message}`)
    }
  }

  const startEdit = (listing: Listing) => {
    setEditingId(listing._id)
    setEditForm({
      title: listing.title,
      description: listing.description,
      price: listing.price,
      city: listing.city,
      category: listing.category,
      tags: listing.tags,
      images: [...listing.images] // Include images in edit form
    })
  }

  const handleRemoveImage = (imageUrl: string) => {
    if (!editForm.images) return
    setEditForm({
      ...editForm,
      images: editForm.images.filter(img => img !== imageUrl)
    })
  }

  const handleAddNewImage = () => {
    if (!newImageUrl.trim()) {
      alert('Please enter an image URL')
      return
    }

    if (!newImageUrl.startsWith('http://') && !newImageUrl.startsWith('https://')) {
      alert('Please enter a valid URL (must start with http:// or https://)')
      return
    }

    setEditForm({
      ...editForm,
      images: [...(editForm.images || []), newImageUrl]
    })
    setNewImageUrl('')
  }

  const handleUpdate = async (listingId: string) => {
    try {
      const payload = {
        title: editForm.title,
        description: editForm.description,
        price: editForm.price,
        city: editForm.city,
        category: editForm.category,
        tags: editForm.tags,
        images: editForm.images // Include images in update
      }

      const res = await fetch(`${API_URL}/listings/${listingId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify(payload)
      })

      const data = await res.json()

      if (!res.ok) {
        throw new Error(data?.detail || 'Failed to update listing')
      }

      // Update local state
      setListings(listings.map(l => l._id === listingId ? { ...l, ...editForm } : l))
      setEditingId(null)
      setEditForm({})
      setNewImageUrl('')
      alert('Listing updated successfully!')
    } catch (err: any) {
      alert(`Error: ${err.message}`)
    }
  }

  const cancelEdit = () => {
    setEditingId(null)
    setEditForm({})
    setNewImageUrl('')
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
                  src={resolveImageUrl(listing.images[0])}
                  alt={listing.title}
                  className="listing-image"
                />
              ) : (
                <div className="listing-image-placeholder">No Image</div>
              )}
              
              <div className="listing-content">
                {editingId === listing._id ? (
                  // Edit Mode
                  <div className="edit-form">
                    <div className="form-group">
                      <label>Title</label>
                      <input
                        type="text"
                        className="input"
                        value={editForm.title || ''}
                        onChange={(e) => setEditForm({ ...editForm, title: e.target.value })}
                      />
                    </div>
                    
                    <div className="form-group">
                      <label>Description</label>
                      <textarea
                        className="input"
                        rows={3}
                        value={editForm.description || ''}
                        onChange={(e) => setEditForm({ ...editForm, description: e.target.value })}
                      />
                    </div>
                    
                    <div className="form-row">
                      <div className="form-group">
                        <label>Price (LKR)</label>
                        <input
                          type="number"
                          className="input"
                          value={editForm.price || 0}
                          onChange={(e) => setEditForm({ ...editForm, price: Number(e.target.value) })}
                        />
                      </div>
                      
                      <div className="form-group">
                        <label>City</label>
                        <select
                          className="input"
                          value={editForm.city || ''}
                          onChange={(e) => setEditForm({ ...editForm, city: e.target.value })}
                        >
                          {availableCities.map(c => (
                            <option key={c} value={c}>{c}</option>
                          ))}
                        </select>
                      </div>
                    </div>
                    
                    <div className="form-group">
                      <label>Category</label>
                      <select
                        className="input"
                        value={editForm.category || ''}
                        onChange={(e) => setEditForm({ ...editForm, category: e.target.value })}
                      >
                        {categories.map(cat => (
                          <option key={cat} value={cat}>{cat.replace('_', ' ')}</option>
                        ))}
                      </select>
                    </div>
                    
                    <div className="form-group">
                      <label>Tags (comma-separated)</label>
                      <input
                        type="text"
                        className="input"
                        value={editForm.tags?.join(', ') || ''}
                        onChange={(e) => setEditForm({ 
                          ...editForm, 
                          tags: e.target.value.split(',').map(t => t.trim()).filter(Boolean)
                        })}
                      />
                    </div>
                    
                    {/* Image Management Section */}
                    <div className="form-group">
                      <label>Images</label>
                      <div className="image-management">
                        {editForm.images && editForm.images.length > 0 ? (
                          <div className="image-list">
                            {editForm.images.map((img, index) => (
                              <div key={index} className="image-item">
                                <img 
                                  src={resolveImageUrl(img)} 
                                  alt={`Image ${index + 1}`}
                                  className="image-thumbnail"
                                />
                                <button
                                  type="button"
                                  onClick={() => handleRemoveImage(img)}
                                  className="btn-remove-image"
                                  title="Remove image"
                                >
                                  ✕
                                </button>
                                <small className="image-url-text">{img.substring(0, 30)}...</small>
                              </div>
                            ))}
                          </div>
                        ) : (
                          <p className="no-images-text">No images</p>
                        )}
                        
                        {/* Add New Image URL */}
                        <div className="add-image-section">
                          <div className="add-image-input-group">
                            <input
                              type="url"
                              className="input"
                              placeholder="https://example.com/image.jpg"
                              value={newImageUrl}
                              onChange={(e) => setNewImageUrl(e.target.value)}
                            />
                            <button
                              type="button"
                              onClick={handleAddNewImage}
                              className="btn btn-secondary btn-sm"
                            >
                              + Add Image
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    <div className="listing-actions">
                      <button
                        onClick={() => handleUpdate(listing._id)}
                        className="btn btn-primary btn-sm"
                      >
                        Save
                      </button>
                      <button
                        onClick={cancelEdit}
                        className="btn btn-secondary btn-sm"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                ) : (
                  // View Mode
                  <>
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
                        {listing.tags.map((tag) => (
                          <span key={tag} className="tag">{tag}</span>
                        ))}
                      </div>
                    )}

                    <div className="listing-dates">
                      <small>Expires: {new Date(listing.expires_at).toLocaleDateString()}</small>
                    </div>

                    {/* Image URL Input */}
                    {addingImageTo === listing._id && (
                      <div className="url-input-container" style={{ marginTop: '10px', marginBottom: '10px' }}>
                        <input
                          type="url"
                          className="input"
                          placeholder="https://example.com/image.jpg"
                          value={imageUrl}
                          onChange={(e) => setImageUrl(e.target.value)}
                          style={{ marginBottom: '5px' }}
                        />
                        <div style={{ display: 'flex', gap: '5px' }}>
                          <button
                            onClick={() => handleAddImageByUrl(listing._id)}
                            className="btn btn-primary btn-sm"
                          >
                            Add URL
                          </button>
                          <button
                            onClick={() => {
                              setAddingImageTo(null)
                              setImageUrl('')
                            }}
                            className="btn btn-secondary btn-sm"
                          >
                            Cancel
                          </button>
                        </div>
                      </div>
                    )}

                    <div className="listing-actions">
                      <Link to={`/listing/${listing._id}`} className="btn btn-secondary btn-sm">
                        View
                      </Link>
                      
                      <button
                        onClick={() => startEdit(listing)}
                        className="btn btn-secondary btn-sm"
                      >
                        Edit
                      </button>
                      
                      <label className="btn btn-secondary btn-sm" style={{ cursor: 'pointer' }}>
                        Upload Image
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
                        onClick={() => setAddingImageTo(listing._id)}
                        className="btn btn-secondary btn-sm"
                      >
                        Image URL
                      </button>

                      <button
                        onClick={() => handleDelete(listing._id)}
                        className="btn btn-danger btn-sm"
                      >
                        Delete
                      </button>
                    </div>
                  </>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
