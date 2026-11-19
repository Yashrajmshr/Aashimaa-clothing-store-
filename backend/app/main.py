import os
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from sqlalchemy import text
from backend.app.core.config import settings
from backend.app.core.database import engine
from backend.app.api.v1 import (
    auth,
    customers,
    services,
    bookings,
    garments,
    qr,
    departments,
    billing,
    deliveries,
    reports,
    settings as app_settings,
    public_tracking
)

app = FastAPI(
    title="AASHIMA ERP API",
    description="Central Business Management Ecosystem for AASHIMA Women's World & AASHIMA Stitchers 'N' Drapers (581, Turab Nagar, Ghaziabad, UP, India).",
    version="2.4.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount media directory for uploads and PDFs
os.makedirs(settings.MEDIA_DIR, exist_ok=True)
app.mount("/media", StaticFiles(directory=str(settings.MEDIA_DIR)), name="media")

# Include Routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(customers.router, prefix=settings.API_V1_STR)
app.include_router(services.router, prefix=settings.API_V1_STR)
app.include_router(bookings.router, prefix=settings.API_V1_STR)
app.include_router(garments.router, prefix=settings.API_V1_STR)
app.include_router(qr.router, prefix=settings.API_V1_STR)
app.include_router(departments.router, prefix=settings.API_V1_STR)
app.include_router(billing.router, prefix=settings.API_V1_STR)
app.include_router(deliveries.router, prefix=settings.API_V1_STR)
app.include_router(reports.router, prefix=settings.API_V1_STR)
app.include_router(app_settings.router, prefix=settings.API_V1_STR)
app.include_router(public_tracking.router, prefix=settings.API_V1_STR)

@app.get("/health", tags=["Health"])
@app.get("/api/v1/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "business": settings.BUSINESS_LEGAL_NAME,
        "location": settings.SHOP_ADDRESS,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }

@app.get("/ready", tags=["Health"])
def readiness_check():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception:
        return JSONResponse(status_code=503, content={"status": "not_ready", "dependency": "database"})
    return {"status": "ready"}

# Mount Frontend Applications for unified single-port hosting
from fastapi.responses import RedirectResponse
from backend.app.core.config import BASE_DIR
apps_dir = BASE_DIR.parent / "apps"

@app.get("/admin", include_in_schema=False)
def redirect_admin():
    return RedirectResponse(url="/admin/")

@app.get("/mobile", include_in_schema=False)
def redirect_mobile():
    return RedirectResponse(url="/mobile/")

if (apps_dir / "admin-web").exists():
    app.mount("/admin", StaticFiles(directory=str(apps_dir / "admin-web"), html=True), name="admin-web")

if (apps_dir / "mobile").exists():
    app.mount("/mobile", StaticFiles(directory=str(apps_dir / "mobile"), html=True), name="mobile-app")

if (apps_dir / "customer-web").exists():
    app.mount("/", StaticFiles(directory=str(apps_dir / "customer-web"), html=True), name="customer-web")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
