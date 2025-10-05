"""
Agam Organics - FastAPI Backend
Main application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import auth, products, cart, orders, profile, reviews, banners, checkout
from app.db.init_db import init_database

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="E-commerce API for organic masala products"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(products.router, prefix="/api/products", tags=["Products"])
app.include_router(cart.router, prefix="/api/cart", tags=["Cart"])
app.include_router(orders.router, prefix="/api/orders", tags=["Orders"])
app.include_router(profile.router, prefix="/api/profile", tags=["Profile"])
app.include_router(reviews.router, prefix="/api/reviews", tags=["Reviews"])
app.include_router(banners.router, prefix="/api/banners", tags=["Banners"])
app.include_router(checkout.router, prefix="/api/checkout", tags=["Checkout"])


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    await init_database()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Agam Organics API",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": settings.APP_NAME}
