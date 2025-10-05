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

type ListingsProps = { apiUrl: string; authHeader: HeadersInit; token: string | null }
export const Listings: React.FC<ListingsProps> = ({ apiUrl, authHeader, token }: ListingsProps)=>{
  const [items, setItems] = useState<any[]>([])
  const [latest, setLatest] = useState<any[]>([])
  const [categories, setCategories] = useState<string[]>([])
  const [myItems, setMyItems] = useState<any[]>([])
  const [form, setForm] = useState({ title:'', description:'', price: '', tags:'', city:'', category:'', lat:'', lng:'', features:'', expiry_days:'30' })
  const [error, setError] = useState<string | null>(null)
  const [uploadingId, setUploadingId] = useState<string | null>(null)
  const [uploadError, setUploadError] = useState<string | null>(null)
  const [meError, setMeError] = useState<string | null>(null)

  const load = async ()=>{
    const res = await fetch(`${apiUrl}/listings`)
    const data = await res.json()
    setItems(Array.isArray(data)?data:[])
    const r2 = await fetch(`${apiUrl}/listings/latest?limit=12`)
    setLatest(Array.isArray(await r2.json())? await r2.json(): [])
    const r3 = await fetch(`${apiUrl}/listings/categories`)
    setCategories(Array.isArray(await r3.json())? await r3.json(): [])
  }
  useEffect(()=>{ load() }, [apiUrl])

  const loadMine = async ()=>{
    if(!token){ setMyItems([]); return }
    try{
      const res = await fetch(`${apiUrl}/listings/me`, { headers: { ...(authHeader as any) } })
      const data = await res.json()
      if(!res.ok) throw new Error(data?.detail || 'Failed to load my listings')
      setMyItems(Array.isArray(data)?data:[])
      setMeError(null)
    }catch(e:any){ setMeError(e.message) }
  }
  useEffect(()=>{ loadMine() }, [apiUrl, token])

  const create = async ()=>{
    setError(null)
    try{
      const payload = {
        title: form.title,
        description: form.description,
        price: Number(form.price||0),
  tags: form.tags? form.tags.split(',').map((t: string)=>t.trim()).filter(Boolean): [],
  city: form.city,
        category: form.category as any,
        lat: Number(form.lat),
        lng: Number(form.lng),
  features: form.features? form.features.split(',').map((t: string)=>t.trim()).filter(Boolean): [],
        expiry_days: Number(form.expiry_days || 30)
      }
      const res = await fetch(`${apiUrl}/listings`, { method:'POST', headers: { 'Content-Type':'application/json', ...authHeader }, body: JSON.stringify(payload) })
      const data = await res.json()
      if(!res.ok) throw new Error(data?.detail || 'Create failed')
      setForm({ title:'', description:'', price:'', tags:'', city:'', category:'', lat:'', lng:'', features:'', expiry_days:'30' })
      load()
      loadMine()
    }catch(e:any){ setError(e.message) }
  }

  const uploadImage = async (listingId: string, file: File)=>{
    if(!token){ setUploadError('Login required'); return }
    setUploadError(null)
    setUploadingId(listingId)
    try{
      const fd = new FormData()
      fd.append('file', file)
      const res = await fetch(`${apiUrl}/listings/${listingId}/images`, { method:'POST', headers: { ...(authHeader||{}) }, body: fd })
      const data = await res.json()
      if(!res.ok) throw new Error(data?.detail || 'Upload failed')
      // optimistic update: append to images array on the item
  setItems((prev: any[])=> prev.map((it: any)=> it._id===listingId ? { ...it, images: [...(it.images||[]), data.url] } : it))
    }catch(e:any){ setUploadError(e.message) }
    finally{ setUploadingId(null) }
  }

  return (
    <div>
      <h3 style={{marginTop:0}}>Listings</h3>
      <div className="row" style={{gap:12, marginBottom:12}}>
        <div className="card" style={{flex:1}}>
          <strong>Categories</strong>
          <div style={{marginTop:8, display:'flex', flexWrap:'wrap', gap:6}}>
            {categories.map((c)=> <span key={c} className="tag">{c}</span>)}
          </div>
        </div>
        <div className="card" style={{flex:2}}>
          <strong>Latest</strong>
          <div className="grid" style={{marginTop:8}}>
            {latest.map((it)=> (
              <div key={it._id} className="card">
                <div style={{display:'flex', justifyContent:'space-between'}}>
                  <strong>{it.title}</strong>
                  <span className="badge">{it.category}</span>
                </div>
                <div style={{color:'var(--muted)'}}>{it.city}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
      <div className="row" style={{marginBottom:8}}>
  <input className="input" placeholder="title" value={form.title} onChange={(e: ChangeEvent<HTMLInputElement>)=>setForm({...form, title:e.target.value})} />
  <input className="input" placeholder="price" value={form.price} onChange={(e: ChangeEvent<HTMLInputElement>)=>setForm({...form, price:e.target.value})} />
  <input className="input" placeholder="city" value={form.city} onChange={(e: ChangeEvent<HTMLInputElement>)=>setForm({...form, city:e.target.value})} />
        <select className="input" value={form.category} onChange={(e)=>setForm({...form, category:e.target.value})}>
          <option value="">category</option>
          {categories.map(c=> <option key={c} value={c}>{c}</option>)}
        </select>
      </div>
      <div className="row" style={{marginBottom:8}}>
  <input className="input" placeholder="lat" value={form.lat} onChange={(e: ChangeEvent<HTMLInputElement>)=>setForm({...form, lat:e.target.value})} />
  <input className="input" placeholder="lng" value={form.lng} onChange={(e: ChangeEvent<HTMLInputElement>)=>setForm({...form, lng:e.target.value})} />
  <input className="input" placeholder="tags comma-separated" value={form.tags} onChange={(e: ChangeEvent<HTMLInputElement>)=>setForm({...form, tags:e.target.value})} />
      </div>
      <div className="row" style={{marginBottom:8}}>
        <input className="input" placeholder="features comma-separated" value={form.features} onChange={(e: ChangeEvent<HTMLInputElement>)=>setForm({...form, features:e.target.value})} />
        <select className="input" value={form.expiry_days} onChange={(e)=>setForm({...form, expiry_days:e.target.value})}>
          <option value="7">7 days</option>
          <option value="14">14 days</option>
          <option value="30">30 days</option>
          <option value="90">90 days</option>
        </select>
      </div>
      <div className="row" style={{marginBottom:12}}>
        <input className="input" placeholder="description" value={form.description} onChange={(e: ChangeEvent<HTMLInputElement>)=>setForm({...form, description:e.target.value})} />
        <button className="btn" onClick={create}>Create (auth)</button>
        {error && <span style={{color:'#b91c1c'}}>{error}</span>}
      </div>

      <div className="grid">
        {items.map((it)=> (
          <div key={it._id} className="card">
            {Array.isArray(it.images) && it.images.length>0 && (
              <img src={`${apiUrl}${it.images[0]}`} alt={it.title} style={{width:'100%', height:160, objectFit:'cover', borderRadius:6, marginBottom:8, background:'#e5f0ff'}} />
            )}
            <div style={{display:'flex', justifyContent:'space-between'}}>
              <strong>{it.title}</strong>
              <span className="badge">${it.price}</span>
            </div>
            <div style={{color:'var(--muted)', margin:'6px 0'}}>{it.city} {it.category && <span className="badge" style={{marginLeft:6}}>{it.category}</span>}</div>
            <div style={{marginBottom:6}}>{(it.tags||[]).map((t:string)=>(<span className="tag" key={t}>{t}</span>))}</div>
            <div style={{fontSize:13}}>{it.description}</div>
            {/* Owner-only upload control: we don't know the userId on client; allow upload and rely on API 403 if not owner */}
            {token && (
              <div style={{marginTop:10}}>
                <label className="btn" style={{cursor:'pointer'}}>
                  Upload image
                  <input type="file" accept="image/*" style={{display:'none'}} onChange={(e)=>{
                    const f = e.target.files?.[0]; if(f){ uploadImage(it._id, f); e.currentTarget.value=''; }
                  }} />
                </label>
                {uploadingId===it._id && <span className="badge" style={{marginLeft:8}}>uploading...</span>}
                {uploadError && <div style={{color:'#b91c1c', marginTop:6}}>{uploadError}</div>}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* My Listings (requires login) */}
      {token && (
        <div style={{marginTop:16}}>
          <h3 style={{marginTop:0}}>My Listings</h3>
          {meError && <div style={{color:'#b91c1c'}}>{meError}</div>}
          <div className="grid">
            {myItems.map((it)=> (
              <div key={it._id} className="card">
                <div style={{display:'flex', justifyContent:'space-between'}}>
                  <strong>{it.title}</strong>
                  <span className="badge">{it.category}</span>
                </div>
                <div style={{color:'var(--muted)'}}>{it.city}</div>
                <div className="row" style={{marginTop:8}}>
                  <button className="btn" onClick={async ()=>{
                    const res = await fetch(`${apiUrl}/listings/${it._id}`, { method:'DELETE', headers: { ...(authHeader as any) } })
                    if(res.ok){ loadMine(); load(); }
                  }}>Delete</button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export const Search: React.FC<{ apiUrl: string; authHeader: HeadersInit }>=({ apiUrl })=>{
  const [q, setQ] = useState('')
  const [city, setCity] = useState('')
  const [tags, setTags] = useState('')
  const [category, setCategory] = useState('')
  const [categories, setCategories] = useState<string[]>([])
  const [lat, setLat] = useState('')
  const [lng, setLng] = useState('')
  const [radius, setRadius] = useState('5000')
  const [items, setItems] = useState<any[]>([])
  const [semantic, setSemantic] = useState(false)

  useEffect(()=>{
    (async ()=>{
      try{
        const r = await fetch(`${apiUrl}/listings/categories`)
        const data = await r.json()
        if(Array.isArray(data)) setCategories(data)
      }catch{}
    })()
  }, [apiUrl])

  const search = async ()=>{
    const params = new URLSearchParams()
    if(q) params.append('q', q)
    if(city) params.append('city', city)
    if(tags) params.append('tags', tags)
  if(category) params.append('category', category)
  if(lat) params.append('lat', lat)
    if(lng) params.append('lng', lng)
    if(radius) params.append('radius', radius)
    const url = semantic ? `${apiUrl}/listings/search/semantic?${params.toString()}` : `${apiUrl}/listings/search/advanced?${params.toString()}`
    const res = await fetch(url)
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
        <select className="input" value={category} onChange={(e)=>setCategory(e.target.value)}>
          <option value="">category</option>
          {categories.map(c=> <option key={c} value={c}>{c}</option>)}
        </select>
  <input className="input" placeholder="tags (comma)" value={tags} onChange={(e: ChangeEvent<HTMLInputElement>)=>setTags(e.target.value)} />
      </div>
      <div className="row" style={{marginBottom:8}}>
  <input className="input" placeholder="lat" value={lat} onChange={(e: ChangeEvent<HTMLInputElement>)=>setLat(e.target.value)} />
  <input className="input" placeholder="lng" value={lng} onChange={(e: ChangeEvent<HTMLInputElement>)=>setLng(e.target.value)} />
  <input className="input" placeholder="radius m" value={radius} onChange={(e: ChangeEvent<HTMLInputElement>)=>setRadius(e.target.value)} />
        <label style={{display:'flex', alignItems:'center', gap:6}}>
          <input type="checkbox" checked={semantic} onChange={(e)=>setSemantic(e.target.checked)} /> semantic
        </label>
        <button className="btn" onClick={search}>Search</button>
        <button className="btn" onClick={nearby}>Nearby</button>
      </div>

      <div className="grid">
        {items.map((it)=> (
          <div key={it._id} className="card">
            {Array.isArray(it.images) && it.images.length>0 && (
              <img src={`${apiUrl}${it.images[0]}`} alt={it.title} style={{width:'100%', height:160, objectFit:'cover', borderRadius:6, marginBottom:8, background:'#e5f0ff'}} />
            )}
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
  const [error, setError] = useState<string | null>(null)

  const load = async ()=>{
    const res = await fetch(`${apiUrl}/analytics/summary`)
    if(res.ok){ setData(await res.json()); setError(null) } else {
      setData(null)
      if(res.status === 403) setError('Admin only')
    }
  }
  useEffect(()=>{ load() }, [apiUrl])

  return (
    <div>
      <h3 style={{marginTop:0}}>Analytics</h3>
  {!data && !error && <div style={{color:'var(--muted)'}}>Run the ETL to see data</div>}
  {error && <div style={{color:'#b91c1c'}}>{error}</div>}
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
