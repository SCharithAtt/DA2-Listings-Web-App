from typing import List, Optional
from pydantic import BaseModel, Field


class GeoPoint(BaseModel):
    type: str = Field(default="Point")
    coordinates: List[float] = Field(..., min_items=2, max_items=2, description="[lng, lat]")


class ListingBase(BaseModel):
    title: str
    description: str
    price: float = Field(ge=0)
    tags: List[str] = []
    city: str
    features: List[str] = []


class ListingCreate(ListingBase):
    lat: float
    lng: float


class ListingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = Field(default=None, ge=0)
    tags: Optional[List[str]] = None
    city: Optional[str] = None
    features: Optional[List[str]] = None
    lat: Optional[float] = None
    lng: Optional[float] = None


class ListingOut(BaseModel):
    id: str = Field(alias="_id")
    title: str
    description: str
    price: float
    tags: List[str]
    city: str
    features: List[str]
    userId: str
    location: GeoPoint
    score: Optional[float] = None
