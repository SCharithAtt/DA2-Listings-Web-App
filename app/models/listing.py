from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


class GeoPoint(BaseModel):
    type: str = Field(default="Point")
    coordinates: List[float] = Field(..., min_items=2, max_items=2, description="[lng, lat]")


class Category(str, Enum):
    electronics = "electronics"
    vehicles = "vehicles"
    real_estate = "real_estate"
    jobs = "jobs"
    services = "services"
    furniture = "furniture"
    clothing = "clothing"
    books = "books"
    sports = "sports"
    pets = "pets"
    toys = "toys"
    home_garden = "home_garden"
    health_beauty = "health_beauty"
    food_beverages = "food_beverages"
    other = "other"


class ListingBase(BaseModel):
    title: str
    description: str
    price: float = Field(ge=0)
    tags: List[str] = []
    city: str
    category: Category
    features: List[str] = []
    posted_date: Optional[datetime] = None


class ListingCreate(ListingBase):
    lat: float = Field(ge=-90, le=90)
    lng: float = Field(ge=-180, le=180)
    expiry_days: Optional[int] = Field(default=30, description="Allowed: 7,14,30,90")


class ListingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = Field(default=None, ge=0)
    tags: Optional[List[str]] = None
    city: Optional[str] = None
    category: Optional[Category] = None
    features: Optional[List[str]] = None
    lat: Optional[float] = Field(default=None, ge=-90, le=90)
    lng: Optional[float] = Field(default=None, ge=-180, le=180)
    expiry_days: Optional[int] = Field(default=None, description="Allowed: 7,14,30,90")


class ListingOut(BaseModel):
    id: str = Field(alias="_id")
    title: str
    description: str
    price: float
    tags: List[str] = []
    city: str
    category: Optional[str] = None  # Changed to str to accept database values
    features: List[str] = []
    userId: str
    location: GeoPoint
    score: Optional[float] = None
    images: List[str] = []
    posted_date: Optional[datetime] = None
    expires_at: Optional[datetime] = None

    class Config:
        populate_by_name = True
        # Allow arbitrary types for flexibility
        arbitrary_types_allowed = True
