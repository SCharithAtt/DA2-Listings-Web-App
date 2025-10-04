import React, { useEffect, useMemo, useState, ChangeEvent } from 'react'

type HeadersInit = Record<string, string>

export const Auth: React.FC<{ apiUrl: string; onToken: (t: string|null)=>void }>=({ apiUrl, onToken })=>{
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [token, setToken] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(()=>{ onToken(token) }, [token])

  const login = async ()=>{
    setLoading(true); setError(null)
    try{
      const body = new URLSearchParams({ username: email, password })
      const res = await fetch(`${apiUrl}/auth/login`, {
        method:'POST', headers: { 'Content-Type':'application/x-www-form-urlencoded' }, body
      })
      const data = await res.json()
      if(!res.ok) throw new Error(data?.detail || 'Login failed')
      setToken(data.access_token)
    }catch(e:any){ setError(e.message) }
    finally{ setLoading(false) }
  }

  const register = async ()=>{
    setLoading(true); setError(null)
    try{
      const res = await fetch(`${apiUrl}/auth/register`, {
        method:'POST', headers: { 'Content-Type':'application/json' }, body: JSON.stringify({ email, password })
      })
      const data = await res.json()
      if(!res.ok) throw new Error(data?.detail || 'Register failed')
      setToken(data.access_token)
    }catch(e:any){ setError(e.message) }
    finally{ setLoading(false) }
  }

  return (
    <div>
      <h3 style={{marginTop:0}}>Auth</h3>
      <div className="row">
        <input className="input" placeholder="email" value={email} onChange={e=>setEmail(e.target.value)} />
        <input className="input" type="password" placeholder="password" value={password} onChange={e=>setPassword(e.target.value)} />
        <button className="btn" onClick={login} disabled={loading}>Login</button>
        <button className="btn" onClick={register} disabled={loading}>Register</button>
        {token && <span className="badge">token acquired</span>}
      </div>
      {error && <div style={{color:'#b91c1c', marginTop:8}}>{error}</div>}
    </div>
  )
}

export const Listings: React.FC<{ apiUrl: string; authHeader: HeadersInit }>=({ apiUrl, authHeader })=>{
  const [items, setItems] = useState<any[]>([])
  const [form, setForm] = useState({ title:'', description:'', price: '', tags:'', city:'', category:'', lat:'', lng:'', features:'' })
  const [error, setError] = useState<string | null>(null)

  const load = async ()=>{
    const res = await fetch(`${apiUrl}/listings`)
    const data = await res.json()
    setItems(Array.isArray(data)?data:[])
  }
  useEffect(()=>{ load() }, [apiUrl])

  const create = async ()=>{
    setError(null)
    try{
      const payload = {
        title: form.title,
        description: form.description,
        price: Number(form.price||0),
        tags: form.tags? form.tags.split(',').map(t=>t.trim()).filter(Boolean): [],
  city: form.city,
  category: form.category || null,
        lat: Number(form.lat),
        lng: Number(form.lng),
  features: form.features? form.features.split(',').map((t: string)=>t.trim()).filter(Boolean): [],
      }
      const res = await fetch(`${apiUrl}/listings`, { method:'POST', headers: { 'Content-Type':'application/json', ...authHeader }, body: JSON.stringify(payload) })
      const data = await res.json()
      if(!res.ok) throw new Error(data?.detail || 'Create failed')
  setForm({ title:'', description:'', price:'', tags:'', city:'', category:'', lat:'', lng:'', features:'' })
      load()
    }catch(e:any){ setError(e.message) }
  }

  return (
    <div>
      <h3 style={{marginTop:0}}>Listings</h3>
      <div className="row" style={{marginBottom:8}}>
  <input className="input" placeholder="title" value={form.title} onChange={(e: ChangeEvent<HTMLInputElement>)=>setForm({...form, title:e.target.value})} />
  <input className="input" placeholder="price" value={form.price} onChange={(e: ChangeEvent<HTMLInputElement>)=>setForm({...form, price:e.target.value})} />
  <input className="input" placeholder="city" value={form.city} onChange={(e: ChangeEvent<HTMLInputElement>)=>setForm({...form, city:e.target.value})} />
  <input className="input" placeholder="category" value={form.category} onChange={(e: ChangeEvent<HTMLInputElement>)=>setForm({...form, category:e.target.value})} />
      </div>
      <div className="row" style={{marginBottom:8}}>
  <input className="input" placeholder="lat" value={form.lat} onChange={(e: ChangeEvent<HTMLInputElement>)=>setForm({...form, lat:e.target.value})} />
  <input className="input" placeholder="lng" value={form.lng} onChange={(e: ChangeEvent<HTMLInputElement>)=>setForm({...form, lng:e.target.value})} />
  <input className="input" placeholder="tags comma-separated" value={form.tags} onChange={(e: ChangeEvent<HTMLInputElement>)=>setForm({...form, tags:e.target.value})} />
      </div>
      <div className="row" style={{marginBottom:8}}>
        <input className="input" placeholder="features comma-separated" value={form.features} onChange={e=>setForm({...form, features:e.target.value})} />
      </div>
      <div className="row" style={{marginBottom:12}}>
        <input className="input" placeholder="description" value={form.description} onChange={e=>setForm({...form, description:e.target.value})} />
        <button className="btn" onClick={create}>Create (auth)</button>
        {error && <span style={{color:'#b91c1c'}}>{error}</span>}
      </div>

      <div className="grid">
        {items.map((it)=> (
          <div key={it._id} className="card">
            <div style={{display:'flex', justifyContent:'space-between'}}>
              <strong>{it.title}</strong>
              <span className="badge">${it.price}</span>
            </div>
            <div style={{color:'var(--muted)', margin:'6px 0'}}>{it.city} {it.category && <span className="badge" style={{marginLeft:6}}>{it.category}</span>}</div>
            <div style={{marginBottom:6}}>{(it.tags||[]).map((t:string)=>(<span className="tag" key={t}>{t}</span>))}</div>
            <div style={{fontSize:13}}>{it.description}</div>
          </div>
        ))}
      </div>
    </div>
  )
}

export const Search: React.FC<{ apiUrl: string; authHeader: HeadersInit }>=({ apiUrl })=>{
  const [q, setQ] = useState('')
  const [city, setCity] = useState('')
  const [tags, setTags] = useState('')
  const [category, setCategory] = useState('')
  const [lat, setLat] = useState('')
  const [lng, setLng] = useState('')
  const [radius, setRadius] = useState('5000')
  const [items, setItems] = useState<any[]>([])

  const search = async ()=>{
    const params = new URLSearchParams()
    if(q) params.append('q', q)
    if(city) params.append('city', city)
    if(tags) params.append('tags', tags)
  if(category) params.append('category', category)
  if(lat) params.append('lat', lat)
    if(lng) params.append('lng', lng)
    if(radius) params.append('radius', radius)
    const res = await fetch(`${apiUrl}/listings/search/advanced?${params.toString()}`)
    const data = await res.json()
    setItems(Array.isArray(data)?data:[])
  }

  const nearby = async ()=>{
    if(!lat || !lng) return
    const res = await fetch(`${apiUrl}/listings/nearby?lat=${lat}&lng=${lng}&radius=${radius}`)
    const data = await res.json()
    setItems(Array.isArray(data)?data:[])
  }

  return (
    <div>
      <h3 style={{marginTop:0}}>Search</h3>
      <div className="row" style={{marginBottom:8}}>
  <input className="input" placeholder="q" value={q} onChange={(e: ChangeEvent<HTMLInputElement>)=>setQ(e.target.value)} />
  <input className="input" placeholder="city" value={city} onChange={(e: ChangeEvent<HTMLInputElement>)=>setCity(e.target.value)} />
  <input className="input" placeholder="category" value={category} onChange={(e: ChangeEvent<HTMLInputElement>)=>setCategory(e.target.value)} />
  <input className="input" placeholder="tags (comma)" value={tags} onChange={(e: ChangeEvent<HTMLInputElement>)=>setTags(e.target.value)} />
      </div>
      <div className="row" style={{marginBottom:8}}>
  <input className="input" placeholder="lat" value={lat} onChange={(e: ChangeEvent<HTMLInputElement>)=>setLat(e.target.value)} />
  <input className="input" placeholder="lng" value={lng} onChange={(e: ChangeEvent<HTMLInputElement>)=>setLng(e.target.value)} />
  <input className="input" placeholder="radius m" value={radius} onChange={(e: ChangeEvent<HTMLInputElement>)=>setRadius(e.target.value)} />
        <button className="btn" onClick={search}>Search</button>
        <button className="btn" onClick={nearby}>Nearby</button>
      </div>

      <div className="grid">
        {items.map((it)=> (
          <div key={it._id} className="card">
            <div style={{display:'flex', justifyContent:'space-between'}}>
              <strong>{it.title}</strong>
              {typeof it.score === 'number' && <span className="badge">score {it.score.toFixed(2)}</span>}
            </div>
            <div style={{color:'var(--muted)', margin:'6px 0'}}>{it.city}</div>
            <div style={{marginBottom:6}}>{(it.tags||[]).map((t:string)=>(<span className="tag" key={t}>{t}</span>))}</div>
            {typeof it.distance === 'number' && <div style={{fontSize:12, color:'var(--muted)'}}>{Math.round(it.distance)} m away</div>}
          </div>
        ))}
      </div>
    </div>
  )
}

export const Analytics: React.FC<{ apiUrl: string }>=({ apiUrl })=>{
  const [data, setData] = useState<any | null>(null)

  const load = async ()=>{
    const res = await fetch(`${apiUrl}/analytics/summary`)
    if(res.ok){ setData(await res.json()) } else { setData(null) }
  }
  useEffect(()=>{ load() }, [apiUrl])

  return (
    <div>
      <h3 style={{marginTop:0}}>Analytics</h3>
      {!data && <div style={{color:'var(--muted)'}}>Run the ETL to see data</div>}
      {data && (
        <div style={{fontSize:13}}>
          <div style={{marginBottom:8}}>Generated: {data.generatedAt}</div>
          <div className="row">
            <div style={{flex:1}}>
              <strong>Top Cities</strong>
              <ul>
                {(data.perCity||[]).slice(0,5).map((x:any)=>(<li key={x._id}>{x._id||'Unknown'} — {x.count}</li>))}
              </ul>
            </div>
            <div style={{flex:1}}>
              <strong>Top Categories</strong>
              <ul>
                {(data.perCategory||[]).slice(0,5).map((x:any)=>(<li key={x._id || 'none'}>{x._id || 'Uncategorized'} — {x.count}</li>))}
              </ul>
            </div>
            <div style={{flex:1}}>
              <strong>Common Tags</strong>
              <ul>
                {(data.commonTags||[]).slice(0,5).map((x:any)=>(<li key={x._id}>{x._id} — {x.count}</li>))}
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
