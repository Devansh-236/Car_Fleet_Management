from typing import List, Optional
from datetime import datetime
from models.telemetry import TelemetryCreate, TelemetryResponse
from database.connectDB import execute_query, execute_insert
from services.vehicle_service import vehicle_service
from services.alert_service import alert_service
from fastapi import HTTPException, status

class TelemetryService:
    @staticmethod
    def receive_telemetry(telemetry_data: TelemetryCreate) -> TelemetryResponse:
        vehicle = vehicle_service.get_vehicle(telemetry_data.vehicle_vin)
        if not vehicle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vehicle with VIN {telemetry_data.vehicle_vin} not found"
            )
        
        diagnostic_codes_str = ",".join(telemetry_data.diagnostic_codes) if telemetry_data.diagnostic_codes else ""
        
        query = """
            INSERT INTO telemetry_data 
            (vehicle_vin, latitude, longitude, speed, engine_status, fuel_battery_level, 
            odometer_reading, diagnostic_codes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            telemetry_data.vehicle_vin,
            telemetry_data.latitude,
            telemetry_data.longitude,
            telemetry_data.speed,
            telemetry_data.engine_status.value,
            telemetry_data.fuel_battery_level,
            telemetry_data.odometer_reading,
            diagnostic_codes_str
        )
        
        telemetry_id = execute_insert(query, params)
        stored_telemetry = TelemetryService.get_telemetry_by_id(telemetry_id)
        
        # Process alerts - convert to dict format for alert processing
        telemetry_dict = {
            'vehicle_vin': stored_telemetry['vehicle_vin'],
            'speed': stored_telemetry['speed'],
            'fuel_battery_level': stored_telemetry['fuel_battery_level'],
            'timestamp': datetime.fromisoformat(stored_telemetry['timestamp'])
        }
        alert_service.process_telemetry_alerts(telemetry_dict)
        
        diagnostic_codes = [code.strip() for code in stored_telemetry['diagnostic_codes'].split(",") if code.strip()] if stored_telemetry['diagnostic_codes'] else []
        
        return TelemetryResponse(
            id=stored_telemetry['id'],
            vehicle_vin=stored_telemetry['vehicle_vin'],
            latitude=stored_telemetry['latitude'],
            longitude=stored_telemetry['longitude'],
            speed=stored_telemetry['speed'],
            engine_status=stored_telemetry['engine_status'],
            fuel_battery_level=stored_telemetry['fuel_battery_level'],
            odometer_reading=stored_telemetry['odometer_reading'],
            diagnostic_codes=diagnostic_codes,
            timestamp=datetime.fromisoformat(stored_telemetry['timestamp'])
        )
    
    @staticmethod
    def get_telemetry_by_id(telemetry_id: int) -> Optional[dict]:
        query = "SELECT * FROM telemetry_data WHERE id = ?"
        results = execute_query(query, (telemetry_id,))
        if results:
            return results[0]
        return None
    
    @staticmethod
    def get_latest_telemetry(vin: str) -> Optional[TelemetryResponse]:
        query = """
            SELECT * FROM telemetry_data 
            WHERE vehicle_vin = ? 
            ORDER BY timestamp DESC 
            LIMIT 1
        """
        results = execute_query(query, (vin,))
        if results:
            row = results[0]
            diagnostic_codes = [code.strip() for code in row['diagnostic_codes'].split(",") if code.strip()] if row['diagnostic_codes'] else []
            return TelemetryResponse(
                id=row['id'],
                vehicle_vin=row['vehicle_vin'],
                latitude=row['latitude'],
                longitude=row['longitude'],
                speed=row['speed'],
                engine_status=row['engine_status'],
                fuel_battery_level=row['fuel_battery_level'],
                odometer_reading=row['odometer_reading'],
                diagnostic_codes=diagnostic_codes,
                timestamp=datetime.fromisoformat(row['timestamp'])
            )
        return None
    
    @staticmethod
    def get_telemetry_history(vin: str, limit: int = 100) -> List[TelemetryResponse]:
        query = """
            SELECT * FROM telemetry_data 
            WHERE vehicle_vin = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        """
        results = execute_query(query, (vin, limit))
        telemetry_list = []
        for row in results:
            diagnostic_codes = [code.strip() for code in row['diagnostic_codes'].split(",") if code.strip()] if row['diagnostic_codes'] else []
            telemetry_list.append(TelemetryResponse(
                id=row['id'],
                vehicle_vin=row['vehicle_vin'],
                latitude=row['latitude'],
                longitude=row['longitude'],
                speed=row['speed'],
                engine_status=row['engine_status'],
                fuel_battery_level=row['fuel_battery_level'],
                odometer_reading=row['odometer_reading'],
                diagnostic_codes=diagnostic_codes,
                timestamp=datetime.fromisoformat(row['timestamp'])
            ))
        return telemetry_list
    
    @staticmethod
    def receive_multiple_telemetry(telemetry_list: List[TelemetryCreate]) -> List[TelemetryResponse]:
        results = []
        for telemetry_data in telemetry_list:
            try:
                result = TelemetryService.receive_telemetry(telemetry_data)
                results.append(result)
            except HTTPException as e:
                print(f"Error processing telemetry for VIN {telemetry_data.vehicle_vin}: {e.detail}")
        return results

telemetry_service = TelemetryService()
