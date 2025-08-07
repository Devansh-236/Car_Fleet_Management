from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum
from datetime import datetime

class EngineStatus(str, Enum):
    ON = "On"
    OFF = "Off"
    IDLE = "Idle"

class TelemetryBase(BaseModel):
    vehicle_vin: str = Field(..., description="Vehicle Identification Number")
    latitude: float = Field(..., description="GPS latitude")
    longitude: float = Field(..., description="GPS longitude")
    speed: float = Field(..., description="Current speed in km/h")
    engine_status: EngineStatus = Field(..., description="Engine status")
    fuel_battery_level: float = Field(..., ge=0, le=100, description="Fuel/Battery level percentage")
    odometer_reading: float = Field(..., description="Total kilometers")
    diagnostic_codes: Optional[List[str]] = Field(default=[], description="Error diagnostic codes")

class TelemetryCreate(TelemetryBase):
    pass

class TelemetryResponse(BaseModel):
    id: int
    vehicle_vin: str
    latitude: float
    longitude: float
    speed: float
    engine_status: EngineStatus
    fuel_battery_level: float
    odometer_reading: float
    diagnostic_codes: List[str]
    timestamp: datetime

    class Config:
        from_attributes = True
