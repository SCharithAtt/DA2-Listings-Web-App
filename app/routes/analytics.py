from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime, timedelta
from typing import List, Dict, Any
from app.db.mongo import get_db
from app.utils.mongo_helpers import normalize_id
from app.routes.auth import get_current_role
from app.models.user import Role


router = APIRouter()


@router.get("/summary")
async def get_summary(db=Depends(get_db), role: Role = Depends(get_current_role)):
    """Get pre-generated analytics summary from ETL"""
    if role != Role.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only")
    doc = await db.analytics_summary.find_one(sort=[("generatedAt", -1)])
    if not doc:
        raise HTTPException(status_code=404, detail="No analytics available")
    return normalize_id(doc)


@router.get("/live")
async def get_live_analytics(db=Depends(get_db), role: Role = Depends(get_current_role)):
    """
    Get real-time analytics using MongoDB aggregation pipelines.
    Provides fresh data without needing ETL.
    """
    if role != Role.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only")
    
    # Get total counts
    total_listings = await db.listings.count_documents({})
    total_users = await db.users.count_documents({})
    
    # Active listings (not expired)
    now = datetime.utcnow()
    active_listings = await db.listings.count_documents({
        "$or": [
            {"expires_at": {"$exists": False}},
            {"expires_at": None},
            {"expires_at": {"$gt": now}}
        ]
    })
    
    # Expired listings
    expired_listings = total_listings - active_listings
    
    # Listings by city
    city_pipeline = [
        {"$group": {"_id": "$city", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]
    cities = await db.listings.aggregate(city_pipeline).to_list(length=10)
    
    # Listings by category
    category_pipeline = [
        {"$group": {"_id": "$category", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]
    categories = await db.listings.aggregate(category_pipeline).to_list(length=10)
    
    # Average price by category
    price_by_category_pipeline = [
        {"$match": {"price": {"$exists": True, "$gt": 0}}},
        {"$group": {
            "_id": "$category",
            "avgPrice": {"$avg": "$price"},
            "minPrice": {"$min": "$price"},
            "maxPrice": {"$max": "$price"},
            "count": {"$sum": 1}
        }},
        {"$sort": {"avgPrice": -1}},
        {"$limit": 10}
    ]
    price_stats = await db.listings.aggregate(price_by_category_pipeline).to_list(length=10)
    
    # Daily new listings (last 30 days)
    thirty_days_ago = now - timedelta(days=30)
    daily_listings_pipeline = [
        {"$match": {"posted_date": {"$gte": thirty_days_ago}}},
        {"$group": {
            "_id": {
                "$dateToString": {
                    "format": "%Y-%m-%d",
                    "date": "$posted_date"
                }
            },
            "count": {"$sum": 1}
        }},
        {"$sort": {"_id": -1}},
        {"$limit": 30}
    ]
    daily_listings = await db.listings.aggregate(daily_listings_pipeline).to_list(length=30)
    
    # Top tags (unwind array and count)
    tags_pipeline = [
        {"$match": {"tags": {"$exists": True, "$ne": []}}},
        {"$unwind": "$tags"},
        {"$group": {"_id": "$tags", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 15}
    ]
    top_tags = await db.listings.aggregate(tags_pipeline).to_list(length=15)
    
    # Price range distribution
    price_ranges_pipeline = [
        {"$match": {"price": {"$exists": True, "$gt": 0}}},
        {"$bucket": {
            "groupBy": "$price",
            "boundaries": [0, 100, 500, 1000, 5000, 10000, 50000, 100000],
            "default": "100000+",
            "output": {"count": {"$sum": 1}}
        }}
    ]
    try:
        price_ranges = await db.listings.aggregate(price_ranges_pipeline).to_list(length=10)
    except:
        price_ranges = []
    
    # User registration trend (last 30 days)
    user_trend_pipeline = [
        {"$group": {
            "_id": {
                "$dateToString": {
                    "format": "%Y-%m-%d",
                    "date": {"$toDate": "$_id"}
                }
            },
            "count": {"$sum": 1}
        }},
        {"$sort": {"_id": -1}},
        {"$limit": 30}
    ]
    user_registrations = await db.users.aggregate(user_trend_pipeline).to_list(length=30)
    
    # Listings with images vs without
    with_images = await db.listings.count_documents({"images": {"$exists": True, "$ne": []}})
    without_images = total_listings - with_images
    
    # Most active users (by listing count)
    active_users_pipeline = [
        {"$group": {"_id": "$userId", "listingCount": {"$sum": 1}}},
        {"$sort": {"listingCount": -1}},
        {"$limit": 10},
        {"$lookup": {
            "from": "users",
            "localField": "_id",
            "foreignField": "_id",
            "as": "user"
        }},
        {"$unwind": {"path": "$user", "preserveNullAndEmptyArrays": True}},
        {"$project": {
            "_id": 1,
            "listingCount": 1,
            "email": "$user.email"
        }}
    ]
    active_users = await db.users.aggregate(active_users_pipeline).to_list(length=10)
    
    return {
        "generatedAt": datetime.utcnow().isoformat(),
        "overview": {
            "totalListings": total_listings,
            "activeListings": active_listings,
            "expiredListings": expired_listings,
            "totalUsers": total_users,
            "listingsWithImages": with_images,
            "listingsWithoutImages": without_images
        },
        "byCity": cities,
        "byCategory": categories,
        "priceStatsByCategory": price_stats,
        "dailyListings": daily_listings,
        "topTags": top_tags,
        "priceRanges": price_ranges,
        "userRegistrations": user_registrations,
        "mostActiveUsers": active_users
    }
