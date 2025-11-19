import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import PlainTextResponse

from database import create_document, get_documents, db
from schemas import ContactMessage, QuoteRequest, Testimonial, PortfolioItem, BlogPost

APP_NAME = "Alles In Farbe – Gordon Nehls"
BASE_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

app = FastAPI(title=APP_NAME, description="API für Website & Lead-Erfassung")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": f"{APP_NAME} API läuft"}


# Lead capture endpoints
@app.post("/api/contact")
def submit_contact(message: ContactMessage):
    try:
        doc_id = create_document("contactmessage", message)
        return {"status": "ok", "id": doc_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/quote")
def submit_quote(req: QuoteRequest):
    try:
        doc_id = create_document("quoterequest", req)
        return {"status": "ok", "id": doc_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Content endpoints (optional CMS-like)
@app.get("/api/testimonials")
def list_testimonials() -> List[Testimonial]:
    try:
        items = get_documents("testimonial")
        if items:
            # convert ObjectId to str if present
            for it in items:
                it["_id"] = str(it.get("_id"))
            return items
    except Exception:
        pass
    # fallback sample testimonials
    return [
        {"name": "Familie Müller", "quote": "Saubere Arbeit, termingerecht und sehr freundlich. Unser Wohnzimmer strahlt wie neu!", "rating": 5, "location": "Hamburg-Eimsbüttel"},
        {"name": "K. Schneider", "quote": "Kompetente Beratung und top Qualität – klare Empfehlung!", "rating": 5, "location": "Hamburg-Nord"},
        {"name": "Bauunternehmen Hansen", "quote": "Zuverlässiger Partner auf der Baustelle. Präzise und flexibel.", "rating": 5, "location": "Norderstedt"},
    ]


@app.get("/api/portfolio")
def list_portfolio() -> List[PortfolioItem]:
    try:
        items = get_documents("portfolioitem")
        if items:
            for it in items:
                it["_id"] = str(it.get("_id"))
            return items
    except Exception:
        pass
    return [
        {
            "title": "Wohnzimmer – Farbauffrischung",
            "description": "Dezentes Beige mit Akzentwand in Petrol.",
            "before_image": "https://images.unsplash.com/photo-1496317556649-f930d733eea0?q=80&w=1600&auto=format&fit=crop",
            "after_image": "https://images.unsplash.com/photo-1505691938895-1758d7feb511?q=80&w=1600&auto=format&fit=crop",
            "location": "Hamburg",
            "tags": ["Innen", "Wohnen", "Akzentwand"],
        },
        {
            "title": "Fassadensanierung Altbau",
            "description": "Schonende Aufbereitung und langlebiger Fassadenanstrich.",
            "before_image": "https://images.unsplash.com/photo-1523661149972-0becaca2016e?q=80&w=1600&auto=format&fit=crop",
            "after_image": "https://images.unsplash.com/photo-1521737604893-d14cc237f11d?q=80&w=1600&auto=format&fit=crop",
            "location": "Hamburg-Winterhude",
            "tags": ["Außen", "Fassade"],
        },
    ]


@app.get("/api/blog")
def list_blog() -> List[BlogPost]:
    try:
        items = get_documents("blogpost")
        if items:
            for it in items:
                it["_id"] = str(it.get("_id"))
            return items
    except Exception:
        pass
    return [
        {
            "title": "Der beste Zeitpunkt für den Fassadenanstrich",
            "slug": "bester-zeitpunkt-fassadenanstrich",
            "excerpt": "Wetter, Untergrund und Planung – darauf sollten Sie achten.",
            "content": "Frühjahr und Frühherbst bieten meist die besten Bedingungen...",
            "published": True,
        },
        {
            "title": "Pflege von lackierten Oberflächen",
            "slug": "pflege-lackierte-oberflaechen",
            "excerpt": "So bleibt der Lack lange schön.",
            "content": "Mit den richtigen Reinigungsmitteln und Intervallen...",
            "published": True,
        },
    ]


# Simple dynamic sitemap
SITEMAP_PATHS = [
    "/",
    "/ueber-uns",
    "/leistungen",
    "/referenzen",
    "/bewertungen",
    "/kontakt",
    "/angebot",
    "/blog",
]

@app.get("/sitemap.xml", response_class=PlainTextResponse)
def sitemap_xml():
    urls = "".join([
        f"\n  <url>\n    <loc>{BASE_URL}{path}</loc>\n    <changefreq>weekly</changefreq>\n    <priority>{'1.0' if path=='/' else '0.8'}</priority>\n  </url>" for path in SITEMAP_PATHS
    ])
    xml = f"""<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">{urls}\n</urlset>"""
    return xml


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": "❌ Not Set",
        "database_name": "❌ Not Set",
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set"
            response["database_name"] = getattr(db, "name", "✅ Connected")
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    import os as _os
    response["database_url"] = "✅ Set" if _os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if _os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
