# DA2 Smart Listings Web App

Full-stack listings application with FastAPI + MongoDB backend and React + TypeScript frontend. Features JWT auth, intelligent semantic search, geospatial queries, and analytics ETL.

## Project structure

```
.
├─ app/
│  ├─ auth/
│  │  └─ security.py
│  ├─ db/
│  │  └─ mongo.py
│  ├─ models/
│  │  ├─ listing.py
│  │  └─ user.py
│  ├─ routes/
│  │  ├─ analytics.py
│  │  ├─ auth.py
│  │  └─ listings.py
│  └─ utils/
│     └─ settings.py
├─ etl/
│  └─ run_etl.py
├─ main.py
├─ requirements.txt
├─ .env.example
├─ frontend/ (React + Vite)
└─ README.md
```

## Requirements

- Python 3.10+
- MongoDB 5.0+

## Setup

1) Create and fill your .env

Copy `.env.example` to `.env` and update values as needed.

2) Install dependencies

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

3) Run the API

```powershell
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

OpenAPI docs at http://localhost:8000/docs

4) Frontend (React + Vite + TypeScript)

```powershell
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

### Frontend Features
- ✅ Multi-page routing (React Router v6)
- ✅ User authentication with persistent sessions
- ✅ Create listings with mandatory image upload
- ✅ Browse and filter by category
- ✅ Smart semantic search (handles typos)
- ✅ My Listings management (view/edit/delete)
- ✅ Admin analytics dashboard
- ✅ Responsive modern design

See `frontend/README.md` for detailed frontend documentation.

## Auth

- POST /auth/register { email, password } -> bearer token
- POST /auth/login (OAuth2 Password flow) -> bearer token

Use the token as `Authorization: Bearer <token>`

## Listings

- POST /listings (auth) create listing with title, description, price, tags, city, lat, lng, features
	- Optional: category
- GET /listings/{id}
- PUT /listings/{id} (auth, owner only)
- DELETE /listings/{id} (auth, owner only)
- GET /listings (list)
- GET /listings/nearby?lat=..&lng=..&radius=5000
- GET /listings/search/advanced?q=..&lat=..&lng=..&radius=..&city=..&tags=tag1,tag2&category=...
 - POST /listings/{id}/images (auth, owner only) multipart/form-data file field "file"; returns { url }

Indexes created automatically on startup:
- Text index: title, description, tags
- 2dsphere index: location
- Index on userId

## Analytics ETL

Run periodic ETL to compute:
- listings per city
- listings per category
- most common tags
- daily new listings

```powershell
python -m etl.run_etl
```

Dashboard endpoint: GET /analytics/summary

## Notes

- All writes use Pydantic validation and parameterized queries through motor.
- No external search engines used.
 - Local image uploads are saved under `app/listings_images` and served at `/listings/images/...`.
 - Frontend: listing cards show the first image as a thumbnail when available and provide an Upload image button (requires login; server enforces ownership).
 
## Optional: Semantic search (local cosine)

You can enable a simple semantic search that ranks by cosine similarity of sentence embeddings. It does not require external services and works well for small datasets.

Enable and install:

```powershell
# backend
pip install -r requirements.txt
# set in .env
ENABLE_SEMANTIC_SEARCH=true
```

Embeddings generation:
- New/updated listings: embeddings computed in background and stored in `embedding`.
- Existing listings: backfill once

```powershell
python -m etl.backfill_embeddings
```

Endpoint:
- GET /listings/search/semantic?q=...&city=...&tags=tag1,tag2&lat=..&lng=..&radius=5000

Notes:
- Uses sentence-transformers model defined in `EMBEDDING_MODEL` (default MiniLM-L6-v2).
- Keeps existing keyword/geo search intact; this is additive and feature-flagged.
 - CORS is enabled for http://localhost:5173 and http://localhost:3000 in `main.py`.
# DA2-Listings-Web-App
CB011671
