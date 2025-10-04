from fastapi import FastAPI
from app.db.mongo import connect_to_mongo, close_mongo_connection, ensure_indexes
from app.routes import auth as auth_routes
from app.routes import listings as listings_routes
from app.routes import analytics as analytics_routes

app = FastAPI(title="DA2 Smart Listings API", version="0.1.0")


@app.on_event("startup")
async def startup_event():
    await connect_to_mongo()
    await ensure_indexes()


@app.on_event("shutdown")
async def shutdown_event():
    await close_mongo_connection()


app.include_router(auth_routes.router, prefix="/auth", tags=["auth"])
app.include_router(listings_routes.router, prefix="/listings", tags=["listings"])
app.include_router(analytics_routes.router, prefix="/analytics", tags=["analytics"])
