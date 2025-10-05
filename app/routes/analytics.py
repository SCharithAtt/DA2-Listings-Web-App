from fastapi import APIRouter, Depends, HTTPException, status
from app.db.mongo import get_db
from app.utils.mongo_helpers import normalize_id
from app.routes.auth import get_current_role
from app.models.user import Role


router = APIRouter()


@router.get("/summary")
async def get_summary(db=Depends(get_db), role: Role = Depends(get_current_role)):
    if role != Role.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only")
    doc = await db.analytics_summary.find_one(sort=[("generatedAt", -1)])
    if not doc:
        raise HTTPException(status_code=404, detail="No analytics available")
    return normalize_id(doc)
