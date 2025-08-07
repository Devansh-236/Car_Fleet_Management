from typing import List, Optional
from datetime import datetime
from app.models.vehicle import Vehicle, VehicleCreate
from app.database.connection import execute_query, execute_insert, execute_update
from fastapi import HTTPException, status

class VehicleService:
    @staticmethod
    def create_vehicle(vehicle_data: VehicleCreate) -> Vehicle:
        existing = VehicleService.get_vehicle(vehicle_data.vin)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Vehicle with VIN {vehicle_data.vin} already exists"
            )
        
        query = """
            INSERT INTO vehicles (vin, manufacturer, model, fleet_id, owner_operator, registration_status)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        params = (
            vehicle_data.vin,
            vehicle_data.manufacturer,
            vehicle_data.model,
            vehicle_data.fleet_id,
            vehicle_data.owner_operator,
            vehicle_data.registration_status.value
        )
        
        vehicle_id = execute_insert(query, params)
        return VehicleService.get_vehicle_by_id(vehicle_id) 
    @staticmethod
    def get_vehicle(vin: str) -> Optional[Vehicle]:
        query = "SELECT * FROM vehicles WHERE vin = ?"
        results = execute_query(query, (vin,))
        if results:
            row = results[0]
            return Vehicle(
                id=row['id'],
                vin=row['vin'],
                manufacturer=row['manufacturer'],
                model=row['model'],
                fleet_id=row['fleet_id'],
                owner_operator=row['owner_operator'],
                registration_status=row['registration_status'],
                created_at=datetime.fromisoformat(row['created_at'])
            )
        return None
    @staticmethod
    def get_vehicle_by_id(vehicle_id: int) -> Optional[Vehicle]:
        query = "SELECT * FROM vehicles WHERE id = ?"
        results = execute_query(query, (vehicle_id,))
        if results:
            row = results[0]
            return Vehicle(
                id=row['id'],
                vin=row['vin'],
                manufacturer=row['manufacturer'],
                model=row['model'],
                fleet_id=row['fleet_id'],
                owner_operator=row['owner_operator'],
                registration_status=row['registration_status'],
                created_at=datetime.fromisoformat(row['created_at'])
            )
        return None
    @staticmethod
    def get_all_vehicles() -> List[Vehicle]:
        query = "SELECT * FROM vehicles ORDER BY created_at DESC"
        results = execute_query(query)
        vehicles = []
        for row in results:
            vehicles.append(Vehicle(
                id=row['id'],
                vin=row['vin'],
                manufacturer=row['manufacturer'],
                model=row['model'],
                fleet_id=row['fleet_id'],
                owner_operator=row['owner_operator'],
                registration_status=row['registration_status'],
                created_at=datetime.fromisoformat(row['created_at'])
            ))
        return vehicles
    @staticmethod
    def delete_vehicle(vin: str) -> bool:
        query = "DELETE FROM vehicles WHERE vin = ?"
        affected_rows = execute_update(query, (vin,))
        return affected_rows > 0
    @staticmethod
    def get_vehicles_by_fleet(fleet_id: str) -> List[Vehicle]:
        query = "SELECT * FROM vehicles WHERE fleet_id = ? ORDER BY created_at DESC"
        results = execute_query(query, (fleet_id,))
        vehicles = []
        for row in results:
            vehicles.append(Vehicle(
                id=row['id'],
                vin=row['vin'],
                manufacturer=row['manufacturer'],
                model=row['model'],
                fleet_id=row['fleet_id'],
                owner_operator=row['owner_operator'],
                registration_status=row['registration_status'],
                created_at=datetime.fromisoformat(row['created_at'])
            ))
        return vehicles
vehicle_service = VehicleService()
