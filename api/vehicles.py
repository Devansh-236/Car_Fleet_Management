from fastapi import APIRouter, HTTPException, status
from typing import List
from models.vehicle import Vehicle, VehicleCreate, VehicleResponse
from services.vehicle_service import vehicle_service

router = APIRouter(prefix="/vehicles", tags=["vehicles"])

@router.post("/", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED)
async def create_vehicle(vehicle_data: VehicleCreate):
    return vehicle_service.create_vehicle(vehicle_data)

@router.get("/", response_model=List[VehicleResponse])
async def list_vehicles():
    return vehicle_service.get_all_vehicles()

@router.get("/{vin}", response_model=VehicleResponse)
async def get_vehicle(vin: str):
    vehicle = vehicle_service.get_vehicle(vin)
    if not vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found")
    return vehicle

@router.delete("/{vin}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vehicle(vin: str):
    if not vehicle_service.delete_vehicle(vin):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found")

@router.get("/fleet/{fleet_id}", response_model=List[VehicleResponse])
async def get_vehicles_by_fleet(fleet_id: str):
    return vehicle_service.get_vehicles_by_fleet(fleet_id)
