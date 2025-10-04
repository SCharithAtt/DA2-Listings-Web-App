from fastapi import APIRouter, Depends, HTTPException
from app.db.mongo import get_db
from app.utils.mongo_helpers import normalize_id


router = APIRouter()


@router.get("/summary")
async def get_summary(db=Depends(get_db)):
    doc = await db.analytics_summary.find_one(sort=[("generatedAt", -1)])
    if not doc:
        raise HTTPException(status_code=404, detail="No analytics available")
    return normalize_id(doc)
