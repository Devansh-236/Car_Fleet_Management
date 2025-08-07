from fastapi import APIRouter, HTTPException, status, Query
from typing import List
from models.telemetry import TelemetryCreate, TelemetryResponse
from services.telemetry_service import telemetry_service

router = APIRouter(prefix="/telemetry", tags=["telemetry"])

@router.post("/", response_model=TelemetryResponse, status_code=status.HTTP_201_CREATED)
async def receive_telemetry(telemetry_data: TelemetryCreate):
    return telemetry_service.receive_telemetry(telemetry_data)

@router.post("/batch", response_model=List[TelemetryResponse], status_code=status.HTTP_201_CREATED)
async def receive_multiple_telemetry(telemetry_list: List[TelemetryCreate]):
    return telemetry_service.receive_multiple_telemetry(telemetry_list)

@router.get("/{vin}/latest", response_model=TelemetryResponse)
async def get_latest_telemetry(vin: str):
    telemetry = telemetry_service.get_latest_telemetry(vin)
    if not telemetry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No telemetry data found")
    return telemetry

@router.get("/{vin}/history", response_model=List[TelemetryResponse])
async def get_telemetry_history(vin: str, limit: int = Query(default=100, ge=1, le=1000)):
    return telemetry_service.get_telemetry_history(vin, limit)
