from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from datetime import datetime

class RegistrationStatus(str, Enum):
    ACTIVE = "Active"
    MAINTENANCE = "Maintenance"
    DECOMMISSIONED = "Decommissioned"

class VehicleBase(BaseModel):
    vin: str = Field(..., description="Vehicle Identification Number")
    manufacturer: str = Field(..., description="Vehicle manufacturer")
    model: str = Field(..., description="Vehicle model")
    fleet_id: str = Field(..., description="Fleet identifier")
    owner_operator: str = Field(..., description="Owner/Operator information")
    registration_status: RegistrationStatus = Field(default=RegistrationStatus.ACTIVE)

class VehicleCreate(VehicleBase):
    pass

class Vehicle(VehicleBase):
    id: int
    created_at: datetime

class VehicleResponse(Vehicle):
    pass

    class Config:
        from_attributes = True
