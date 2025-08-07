from fastapi import APIRouter, HTTPException, status
from typing import List
from app.models.alert import AlertResponse
from app.services.alert_service import alert_service

router = APIRouter(prefix="/alerts", tags=["alerts"])

@router.get("/", response_model=List[AlertResponse])
async def get_all_alerts():
    return alert_service.get_all_alerts()

@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(alert_id: str):
    alert = alert_service.get_alert(alert_id)
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")
    return alert

@router.get("/vehicle/{vin}", response_model=List[AlertResponse])
async def get_alerts_by_vin(vin: str):
    return alert_service.get_alerts_by_vin(vin)
