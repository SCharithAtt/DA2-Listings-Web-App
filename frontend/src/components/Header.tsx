import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

export const Header: React.FC = () => {
  const { isAuthenticated, user, logout } = useAuth()
  const navigate = useNavigate()
  const [searchQuery, setSearchQuery] = useState('')
  const [smartSearch, setSmartSearch] = useState(true) // Smart search enabled by default

  const handleLogout = () => {
    logout()
    navigate('/')
  }

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (searchQuery.trim()) {
      const mode = smartSearch ? 'smart' : 'keyword'
      navigate(`/search?q=${encodeURIComponent(searchQuery.trim())}&mode=${mode}`)
    }
  }

  return (
    <header className="header">
      <div className="header-content">
        <Link to="/" className="brand">
          DA2 Listings
        </Link>
        
        <form onSubmit={handleSearch} className="search-form">
          <input
            type="text"
            className="input search-input"
            placeholder={smartSearch ? "Smart search (e.g., 'Apple Phone')..." : "Keyword search..."}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          <div className="search-mode-toggle">
            <label className="toggle-label">
              <input
                type="checkbox"
                checked={smartSearch}
                onChange={(e) => setSmartSearch(e.target.checked)}
                className="toggle-checkbox"
              />
              <span className="toggle-slider"></span>
              <span className="toggle-text">
                {smartSearch ? '🧠 Smart Search' : '🔍 Keyword Search'}
              </span>
            </label>
          </div>
          <button type="submit" className="btn btn-primary">
            Search
          </button>
        </form>

        <nav className="nav-links">
          <Link to="/" className="nav-link">Home</Link>
          
          {isAuthenticated ? (
            <>
              <Link to="/create" className="nav-link">Create Listing</Link>
              <Link to="/my-listings" className="nav-link">My Listings</Link>
              {user?.role === 'admin' && (
                <Link to="/analytics" className="nav-link">Analytics</Link>
              )}
              <button onClick={handleLogout} className="btn btn-secondary">
                Logout
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="btn btn-primary">Login</Link>
              <Link to="/register" className="btn btn-secondary">Sign Up</Link>
            </>
          )}
        </nav>
      </div>
    </header>
  )
}
