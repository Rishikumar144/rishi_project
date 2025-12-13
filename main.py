"""
RideCare Backend - Main Application Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from routes import vehicles, services

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="RideCare API",
    description="Vehicle Maintenance Record System Backend",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(vehicles.router, prefix="/api/vehicles", tags=["Vehicles"])
app.include_router(services.router, prefix="/api/services", tags=["Services"])

@app.get("/")
def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "RideCare Backend",
        "version": "1.0.0"
    }

@app.get("/health")
def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected"
    }
