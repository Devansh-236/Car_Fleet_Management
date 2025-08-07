from fastapi import FastAPI
from database.connectDB import init_database
from api import vehicles, telemetry, alerts
from services.analytics_service import analytics_service

app = FastAPI(
    title="Connected Car Fleet Management System",
    description="A system for managing vehicle fleets and processing real-time telemetry data with SQLite3 database",
    version="1.0.0"
)

@app.on_event("startup")
def startup_event():
    """Initialize database on startup"""
    init_database()

# Include routers
app.include_router(vehicles.router)
app.include_router(telemetry.router)
app.include_router(alerts.router)

@app.get("/")
async def root():
    return {"message": "Connected Car Fleet Management System API with SQLite3"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "database": "SQLite3 connected"}

@app.get("/analytics")
async def get_analytics():
    """Get fleet analytics"""
    return analytics_service.get_fleet_analytics()
