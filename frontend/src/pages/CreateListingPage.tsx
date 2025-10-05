import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { getCityNames, getCityCoordinates } from '../utils/cities'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const CreateListingPage: React.FC = () => {
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [price, setPrice] = useState('')
  const [city, setCity] = useState('')
  const [category, setCategory] = useState('')
  const [tags, setTags] = useState('')
  const [availableCities] = useState<string[]>(getCityNames())
  const [expiryDays, setExpiryDays] = useState('30')
  const [imageFile, setImageFile] = useState<File | null>(null)
  const [imagePreview, setImagePreview] = useState<string | null>(null)
  const [categories, setCategories] = useState<string[]>([
    'electronics',
    'vehicles',
    'real_estate',
    'jobs',
    'services',
    'furniture',
    'clothing',
    'books',
    'sports',
    'pets',
    'toys',
    'home_garden',
    'health_beauty',
    'food_beverages',
    'other'
  ])
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const { token } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    loadCategories()
  }, [])

  const loadCategories = async () => {
    try {
      const res = await fetch(`${API_URL}/listings/categories`)
      if (res.ok) {
        const data = await res.json()
        if (Array.isArray(data) && data.length > 0) {
          setCategories(data)
        }
      }
    } catch (error) {
      console.error('Failed to load categories, using defaults:', error)
    }
  }

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      if (!file.type.startsWith('image/')) {
        setError('Please select an image file')
        return
      }
      setImageFile(file)
      const reader = new FileReader()
      reader.onloadend = () => {
        setImagePreview(reader.result as string)
      }
      reader.readAsDataURL(file)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)

    // Validation
    if (!title || !description || !imageFile || !city || !category) {
      setError('Please fill in all required fields (Title, Description, Image, City, Category)')
      return
    }

    // Get coordinates for selected city
    const coordinates = getCityCoordinates(city)
    if (!coordinates) {
      setError('Invalid city selected')
      return
    }

    setLoading(true)

    try {
      // Create listing first
      const payload = {
        title,
        description,
        price: Number(price) || 0,
        city,
        category,
        lat: coordinates.lat,
        lng: coordinates.lng,
        tags: tags ? tags.split(',').map(t => t.trim()).filter(Boolean) : [],
        features: [],
        expiry_days: Number(expiryDays)
      }

      const res = await fetch(`${API_URL}/listings`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify(payload)
      })

      const data = await res.json()

      if (!res.ok) {
        // Handle validation errors
        if (data?.detail) {
          if (Array.isArray(data.detail)) {
            // FastAPI validation errors
            const errors = data.detail.map((err: any) => `${err.loc.join('.')}: ${err.msg}`).join(', ')
            throw new Error(errors)
          } else if (typeof data.detail === 'string') {
            throw new Error(data.detail)
          } else {
            throw new Error(JSON.stringify(data.detail))
          }
        }
        throw new Error('Failed to create listing')
      }

      const listingId = data._id

      // Upload image
      const formData = new FormData()
      formData.append('file', imageFile)

      const imgRes = await fetch(`${API_URL}/listings/${listingId}/images`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`
        },
        body: formData
      })

      if (!imgRes.ok) {
        throw new Error('Failed to upload image')
      }

      navigate('/my-listings')
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page">
      <div className="form-container">
        <h2>Create New Listing</h2>
        <form onSubmit={handleSubmit} className="listing-form">
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="title">Title *</label>
              <input
                id="title"
                type="text"
                className="input"
                placeholder="e.g., iPhone 13 Pro"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="price">Price ($)</label>
              <input
                id="price"
                type="number"
                className="input"
                placeholder="0.00"
                value={price}
                onChange={(e) => setPrice(e.target.value)}
                min="0"
                step="0.01"
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="description">Description *</label>
            <textarea
              id="description"
              className="input textarea"
              placeholder="Describe your listing..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={4}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="image">Image * (Required)</label>
            <input
              id="image"
              type="file"
              accept="image/*"
              onChange={handleImageChange}
              className="file-input"
              required
            />
            {imagePreview && (
              <div className="image-preview">
                <img src={imagePreview} alt="Preview" />
              </div>
            )}
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="city">City *</label>
              <select
                id="city"
                className="input"
                value={city}
                onChange={(e) => setCity(e.target.value)}
                required
              >
                <option value="">Select a city</option>
                {availableCities.map((cityName) => (
                  <option key={cityName} value={cityName}>
                    {cityName}
                  </option>
                ))}
              </select>
              <small style={{ color: '#666', fontSize: '0.85rem', marginTop: '4px', display: 'block' }}>
                Location coordinates will be automatically set based on the selected city
              </small>
            </div>

            <div className="form-group">
              <label htmlFor="category">Category *</label>
              <select
                id="category"
                className="input"
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                required
              >
                <option value="">Select category</option>
                {categories.map((cat) => (
                  <option key={cat} value={cat}>
                    {cat.replace('_', ' ')}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="tags">Tags (comma-separated)</label>
              <input
                id="tags"
                type="text"
                className="input"
                placeholder="e.g., smartphone, apple, unlocked"
                value={tags}
                onChange={(e) => setTags(e.target.value)}
              />
            </div>

            <div className="form-group">
              <label htmlFor="expiry">Expiry *</label>
              <select
                id="expiry"
                className="input"
                value={expiryDays}
                onChange={(e) => setExpiryDays(e.target.value)}
                required
              >
                <option value="7">7 days</option>
                <option value="14">14 days</option>
                <option value="30">30 days</option>
                <option value="90">90 days</option>
              </select>
            </div>
          </div>

          {error && <div className="error-message">{error}</div>}

          <button type="submit" className="btn btn-primary btn-full" disabled={loading}>
            {loading ? 'Creating...' : 'Create Listing'}
          </button>
        </form>
      </div>
    </div>
  )
}
