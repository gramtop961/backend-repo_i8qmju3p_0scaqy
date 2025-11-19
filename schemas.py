"""
Database Schemas for Alles In Farbe – Gordon Nehls

Each Pydantic model represents a MongoDB collection. The collection name is the
lowercased class name (e.g., ContactMessage -> "contactmessage").
"""
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr, HttpUrl
from datetime import date

# Core lead capture schemas
class ContactMessage(BaseModel):
    name: str = Field(..., min_length=2, description="Vollständiger Name")
    email: EmailStr = Field(..., description="E-Mail-Adresse")
    phone: Optional[str] = Field(None, description="Telefonnummer")
    message: str = Field(..., min_length=5, max_length=2000, description="Nachricht des Kunden")
    consent: bool = Field(True, description="Einwilligung zur Kontaktaufnahme")

class QuoteRequest(BaseModel):
    name: str = Field(..., min_length=2)
    email: EmailStr
    phone: Optional[str] = None
    project_type: str = Field(..., description="Art der Arbeiten, z. B. Innenanstrich")
    area_sqm: Optional[float] = Field(None, ge=0, description="Fläche in m²")
    interior: Optional[bool] = Field(None, description="Innenarbeiten")
    exterior: Optional[bool] = Field(None, description="Außenarbeiten")
    details: Optional[str] = Field(None, max_length=4000)
    image_urls: Optional[List[HttpUrl]] = Field(default=None, description="Optionale Foto-Links")
    preferred_date: Optional[date] = None

# Content schemas (optional CMS-like)
class PortfolioItem(BaseModel):
    title: str
    description: Optional[str] = None
    before_image: Optional[HttpUrl] = None
    after_image: Optional[HttpUrl] = None
    location: Optional[str] = None
    tags: Optional[List[str]] = None

class Testimonial(BaseModel):
    name: str
    quote: str
    rating: int = Field(ge=1, le=5, default=5)
    location: Optional[str] = None

class BlogPost(BaseModel):
    title: str
    slug: str
    excerpt: Optional[str] = None
    content: str
    cover_image: Optional[HttpUrl] = None
    published: bool = True
