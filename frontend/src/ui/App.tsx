import React, { useMemo, useState, ChangeEvent } from 'react'
import { Auth, Listings, Search, Analytics } from './components'

export const App: React.FC = () => {
  const [token, setToken] = useState<string | null>(null)
  const [apiUrl, setApiUrl] = useState<string>(import.meta.env.VITE_API_URL || 'http://localhost:8000')

  const authHeader = useMemo(() => token ? { Authorization: `Bearer ${token}` } : {}, [token])

  return (
    <div className="container">
      <div className="header">
        <h2 className="brand">DA2 Listings</h2>
  <input className="input" placeholder="API URL" value={apiUrl} onChange={(e: ChangeEvent<HTMLInputElement>) => setApiUrl(e.target.value)} />
      </div>

      <div className="row">
        <div style={{flex:1}} className="card">
          <Auth apiUrl={apiUrl} onToken={setToken} />
        </div>
        <div style={{flex:2}} className="card">
          <Search apiUrl={apiUrl} authHeader={authHeader} />
        </div>
      </div>

      <div className="row" style={{marginTop:12}}>
        <div style={{flex:2}} className="card">
          <Listings apiUrl={apiUrl} authHeader={authHeader} />
        </div>
        <div style={{flex:1}} className="card">
          <Analytics apiUrl={apiUrl} />
        </div>
      </div>
    </div>
  )
}
