import React from 'react'
import { Link } from 'react-router-dom'

export const Footer: React.FC = () => {
  return (
    <footer className="footer">
      <div className="footer-content">
        <div className="footer-section">
          <h4 className="footer-heading">
            <span className="brand-icon">🛒</span> Good Market
          </h4>
          <p className="footer-text">
            Your trusted marketplace for buying and selling quality goods.
          </p>
        </div>

        <div className="footer-section">
          <h4 className="footer-heading">Quick Links</h4>
          <nav className="footer-links">
            <Link to="/" className="footer-link">Home</Link>
            <Link to="/search?q=" className="footer-link">Browse Listings</Link>
            <Link to="/create" className="footer-link">Create Listing</Link>
            <Link to="/my-listings" className="footer-link">My Listings</Link>
          </nav>
        </div>

        <div className="footer-section">
          <h4 className="footer-heading">Categories</h4>
          <nav className="footer-links">
            <Link to="/?category=electronics" className="footer-link">Electronics</Link>
            <Link to="/?category=furniture" className="footer-link">Furniture</Link>
            <Link to="/?category=vehicles" className="footer-link">Vehicles</Link>
            <Link to="/?category=real_estate" className="footer-link">Real Estate</Link>
          </nav>
        </div>

        <div className="footer-section">
          <h4 className="footer-heading">Account</h4>
          <nav className="footer-links">
            <Link to="/login" className="footer-link">Login</Link>
            <Link to="/register" className="footer-link">Sign Up</Link>
            <Link to="/analytics" className="footer-link">Analytics</Link>
          </nav>
        </div>
      </div>

      <div className="footer-bottom">
        <div className="footer-divider"></div>
        <div className="footer-credits">
          <p className="footer-copyright">
            © {new Date().getFullYear()} Good Market. All rights reserved.
          </p>
          <p className="footer-author">
            Developed by <strong>Senura Attanayake - CB011671</strong>
          </p>
        </div>
      </div>
    </footer>
  )
}
