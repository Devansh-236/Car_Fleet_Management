from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from datetime import datetime
import uuid

class AlertType(str, Enum):
    SPEED_VIOLATION = "speed_violation"
    LOW_FUEL_BATTERY = "low_fuel_battery"

class AlertSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class AlertBase(BaseModel):
    vehicle_vin: str = Field(..., description="Vehicle Identification Number")
    alert_type: AlertType = Field(..., description="Type of alert")
    severity: AlertSeverity = Field(..., description="Alert severity")
    message: str = Field(..., description="Alert message")
    resolved: bool = Field(default=False)

class Alert(AlertBase):
    id: int
    alert_id: str
    timestamp: datetime

class AlertResponse(Alert):
    pass

    class Config:
        from_attributes = True
