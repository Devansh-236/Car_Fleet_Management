from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum
from datetime import datetime
import uuid

class ActiveAlertStatus(str, Enum):
    ACTIVE = "active"
    RESOLVED = "resolved"
    ACKNOWLEDGED = "acknowledged"

class ActiveAlertSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ActiveAlertType(str, Enum):
    SPEED_VIOLATION = "speed_violation"
    LOW_FUEL_BATTERY = "low_fuel_battery"

class ActiveAlert(BaseModel):
    id: int
    alert_sender_id: str
    vehicle_vin: str
    alert_type: ActiveAlertType
    severity: ActiveAlertSeverity
    title: str
    description: str
    status: ActiveAlertStatus
    first_occurrence: datetime
    last_occurrence: datetime
    occurrence_count: int
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    created_at: datetime

class ActiveAlertCreate(BaseModel):
    vehicle_vin: str
    alert_type: ActiveAlertType
    severity: ActiveAlertSeverity
    title: str
    description: str

class ActiveAlertUpdate(BaseModel):
    status: Optional[ActiveAlertStatus] = None
    resolved_by: Optional[str] = None

class ActiveAlertResponse(ActiveAlert):
    related_alerts_count: int 

    class Config:
        from_attributes = True

class AlertHistoryResponse(BaseModel):
    active_alert: ActiveAlertResponse
    raw_alerts: List[dict]  

    class Config:
        from_attributes = True
