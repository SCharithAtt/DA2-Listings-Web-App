# DA2 Smart Listings Web App - Backend

FastAPI + MongoDB backend for a smart listings app with JWT auth, intelligent text+geo search, geospatial queries, and analytics ETL.

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

## Auth

- POST /auth/register { email, password } -> bearer token
- POST /auth/login (OAuth2 Password flow) -> bearer token

Use the token as `Authorization: Bearer <token>`

## Listings

- POST /listings (auth) create listing with title, description, price, tags, city, lat, lng, features
- GET /listings/{id}
- PUT /listings/{id} (auth, owner only)
- DELETE /listings/{id} (auth, owner only)
- GET /listings (list)
- GET /listings/nearby?lat=..&lng=..&radius=5000
- GET /listings/search/advanced?q=..&lat=..&lng=..&radius=..&city=..&tags=tag1,tag2

Indexes created automatically on startup:
- Text index: title, description, tags
- 2dsphere index: location
- Index on userId

## Analytics ETL

Run periodic ETL to compute:
- listings per city
- most common tags
- daily new listings

```powershell
python -m etl.run_etl
```

Dashboard endpoint: GET /analytics/summary

## Notes

- All writes use Pydantic validation and parameterized queries through motor.
- No external search engines used.
# DA2-Listings-Web-App
CB011671
