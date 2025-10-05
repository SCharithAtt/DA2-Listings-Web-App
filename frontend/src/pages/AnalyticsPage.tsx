import React, { useEffect, useState } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { formatPrice } from '../utils/imageHelper'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

interface Overview {
  totalListings: number
  activeListings: number
  expiredListings: number
  totalUsers: number
  listingsWithImages: number
  listingsWithoutImages: number
}

interface PriceStats {
  _id: string
  avgPrice: number
  minPrice: number
  maxPrice: number
  count: number
}

interface LiveAnalyticsData {
  generatedAt: string
  overview: Overview
  byCity: Array<{ _id: string; count: number }>
  byCategory: Array<{ _id: string; count: number }>
  priceStatsByCategory: Array<PriceStats>
  dailyListings: Array<{ _id: string; count: number }>
  topTags: Array<{ _id: string; count: number }>
  priceRanges: Array<{ _id: number | string; count: number }>
  userRegistrations: Array<{ _id: string; count: number }>
  mostActiveUsers: Array<{ _id: string; listingCount: number; email?: string }>
}

export const AnalyticsPage: React.FC = () => {
  const [data, setData] = useState<LiveAnalyticsData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [lastRefresh, setLastRefresh] = useState<Date | null>(null)
  const { token } = useAuth()

  useEffect(() => {
    loadAnalytics()
  }, [])

  const loadAnalytics = async () => {
    setLoading(true)
    setError(null)

    try {
      // Use live analytics endpoint for real-time data
      const res = await fetch(`${API_URL}/analytics/live`, {
        headers: token ? {
          Authorization: `Bearer ${token}`
        } : {}
      })

      if (!res.ok) {
        if (res.status === 403) {
          throw new Error('Admin access required')
        }
        throw new Error('Failed to load analytics')
      }

      const analyticsData = await res.json()
      setData(analyticsData)
      setLastRefresh(new Date())
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleRefresh = () => {
    loadAnalytics()
  }

  if (loading && !data) {
    return (
      <div className="page">
        <div className="loading">Loading analytics...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="page">
        <div className="error-message">{error}</div>
        <p className="empty-subtitle">
          {error.includes('Admin') 
            ? 'Only administrators can access this page.'
            : 'Unable to load analytics data'}
        </p>
      </div>
    )
  }

  if (!data) {
    return (
      <div className="page">
        <div className="empty-state">
          <p>No analytics data available</p>
        </div>
      </div>
    )
  }

  const maxDailyListings = Math.max(...data.dailyListings.map(d => d.count), 1)
  const maxCityCount = Math.max(...data.byCity.map(c => c.count), 1)

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h2>Analytics Dashboard</h2>
          <p className="analytics-timestamp">
            {lastRefresh ? `Last updated: ${lastRefresh.toLocaleTimeString()}` : 'Loading...'}
          </p>
        </div>
        <button 
          onClick={handleRefresh} 
          className="btn btn-primary"
          disabled={loading}
        >
          {loading ? '🔄 Refreshing...' : '🔄 Refresh Data'}
        </button>
      </div>

      {/* Overview Stats */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">📊</div>
          <div className="stat-content">
            <div className="stat-value">{data.overview.totalListings}</div>
            <div className="stat-label">Total Listings</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">✅</div>
          <div className="stat-content">
            <div className="stat-value">{data.overview.activeListings}</div>
            <div className="stat-label">Active Listings</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">⏰</div>
          <div className="stat-content">
            <div className="stat-value">{data.overview.expiredListings}</div>
            <div className="stat-label">Expired</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">👥</div>
          <div className="stat-content">
            <div className="stat-value">{data.overview.totalUsers}</div>
            <div className="stat-label">Total Users</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">🖼️</div>
          <div className="stat-content">
            <div className="stat-value">{data.overview.listingsWithImages}</div>
            <div className="stat-label">With Images</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">📝</div>
          <div className="stat-content">
            <div className="stat-value">{data.overview.listingsWithoutImages}</div>
            <div className="stat-label">No Images</div>
          </div>
        </div>
      </div>

      {/* Daily Listings Chart */}
      <div className="analytics-card full-width chart-card">
        <h3>📈 Daily New Listings (Last 30 Days)</h3>
        <div className="chart-container">
          <div className="bar-chart">
            {data.dailyListings.slice().reverse().map((item, index) => {
              const height = (item.count / maxDailyListings) * 100
              return (
                <div key={index} className="bar-wrapper">
                  <div className="bar-label-top">{item.count}</div>
                  <div className="bar" style={{ height: `${Math.max(height, 5)}%` }}>
                    <div className="bar-fill"></div>
                  </div>
                  <div className="bar-label">{new Date(item._id).toLocaleDateString('en', { month: 'short', day: 'numeric' })}</div>
                </div>
              )
            })}
          </div>
        </div>
      </div>

      {/* City Distribution with Horizontal Bars */}
      <div className="analytics-card">
        <h3>🏙️ Top Cities</h3>
        <div className="horizontal-bars">
          {data.byCity.slice(0, 8).map((item) => {
            const percentage = (item.count / maxCityCount) * 100
            return (
              <div key={item._id} className="h-bar-row">
                <div className="h-bar-label">{item._id || 'Unknown'}</div>
                <div className="h-bar-container">
                  <div className="h-bar" style={{ width: `${percentage}%` }}></div>
                </div>
                <div className="h-bar-value">{item.count}</div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Price Statistics */}
      <div className="analytics-card">
        <h3>💰 Price Stats by Category</h3>
        <div className="analytics-list">
          <table className="analytics-table">
            <thead>
              <tr>
                <th>Category</th>
                <th>Avg Price</th>
                <th>Min</th>
                <th>Max</th>
                <th>Count</th>
              </tr>
            </thead>
            <tbody>
              {data.priceStatsByCategory.slice(0, 8).map((item) => (
                <tr key={item._id || 'none'}>
                  <td>{item._id ? item._id.replace('_', ' ') : 'Uncategorized'}</td>
                  <td className="count">{formatPrice(item.avgPrice)}</td>
                  <td>{formatPrice(item.minPrice)}</td>
                  <td>{formatPrice(item.maxPrice)}</td>
                  <td className="count">{item.count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Categories */}
      <div className="analytics-card">
        <h3>📂 Top Categories</h3>
        <div className="analytics-list">
          <table className="analytics-table">
            <thead>
              <tr>
                <th>Category</th>
                <th>Count</th>
              </tr>
            </thead>
            <tbody>
              {data.byCategory.slice(0, 10).map((item) => (
                <tr key={item._id || 'none'}>
                  <td>{item._id ? item._id.replace('_', ' ') : 'Uncategorized'}</td>
                  <td className="count">{item.count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Popular Tags */}
      <div className="analytics-card">
        <h3>🏷️ Popular Tags</h3>
        <div className="tag-cloud">
          {data.topTags.slice(0, 20).map((item) => {
            const size = Math.min(1 + (item.count / 10), 2)
            return (
              <span 
                key={item._id} 
                className="tag-cloud-item"
                style={{ fontSize: `${size}rem` }}
              >
                {item._id} ({item.count})
              </span>
            )
          })}
        </div>
      </div>

      {/* Most Active Users */}
      <div className="analytics-card">
        <h3>⭐ Most Active Users</h3>
        <div className="analytics-list">
          <table className="analytics-table">
            <thead>
              <tr>
                <th>Email</th>
                <th>Listings</th>
              </tr>
            </thead>
            <tbody>
              {data.mostActiveUsers.slice(0, 8).map((item) => (
                <tr key={item._id}>
                  <td>{item.email || 'Unknown'}</td>
                  <td className="count">{item.listingCount}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Price Ranges */}
      {data.priceRanges && data.priceRanges.length > 0 && (
        <div className="analytics-card">
          <h3>💵 Price Distribution</h3>
          <div className="analytics-list">
            <table className="analytics-table">
              <thead>
                <tr>
                  <th>Price Range</th>
                  <th>Count</th>
                </tr>
              </thead>
              <tbody>
                {data.priceRanges.map((item, index) => (
                  <tr key={index}>
                    <td>{item._id === '100000+' ? '$100,000+' : `$${item._id.toLocaleString()}`}</td>
                    <td className="count">{item.count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
