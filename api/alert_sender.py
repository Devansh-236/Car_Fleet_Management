from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Optional
from models.alert_sender import (
    ActiveAlertResponse, ActiveAlertUpdate, AlertHistoryResponse,
    ActiveAlertStatus
)
from services.alert_sender_service import alert_sender_service

router = APIRouter(prefix="/alert-sender", tags=["alert-sender"])

@router.get("/active-alerts", response_model=List[ActiveAlertResponse])
async def get_active_alerts(status: Optional[str] = Query(None, description="Filter by status: active, resolved, acknowledged")):
    """Get all active alerts, optionally filtered by status"""
    return alert_sender_service.get_all_active_alerts(status)

@router.get("/active-alerts/{alert_sender_id}", response_model=ActiveAlertResponse)
async def get_active_alert(alert_sender_id: str):
    """Get a specific active alert by alert_sender_id"""
    alert = alert_sender_service.get_active_alert_by_id(
        # Get ID from alert_sender_id
        next((result['id'] for result in alert_sender_service.execute_query(
            "SELECT id FROM active_alerts WHERE alert_sender_id = ?", (alert_sender_id,)
        )), None)
    )
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Active alert not found")
    return alert

@router.get("/vehicle/{vin}/active-alerts", response_model=List[ActiveAlertResponse])
async def get_vehicle_active_alerts(vin: str):
    """Get all active alerts for a specific vehicle"""
    return alert_sender_service.get_active_alerts_by_vehicle(vin)

@router.put("/active-alerts/{alert_sender_id}", response_model=ActiveAlertResponse)
async def update_alert_status(alert_sender_id: str, update_data: ActiveAlertUpdate):
    """Update alert status (resolve, acknowledge, etc.)"""
    updated_alert = alert_sender_service.update_alert_status(alert_sender_id, update_data)
    if not updated_alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Active alert not found")
    return updated_alert

@router.post("/active-alerts/{alert_sender_id}/resolve")
async def resolve_alert(alert_sender_id: str, resolved_by: str = Query(..., description="Who resolved the alert")):
    """Resolve an active alert"""
    update_data = ActiveAlertUpdate(status=ActiveAlertStatus.RESOLVED, resolved_by=resolved_by)
    updated_alert = alert_sender_service.update_alert_status(alert_sender_id, update_data)
    if not updated_alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Active alert not found")
    return {"message": "Alert resolved successfully", "alert": updated_alert}

@router.post("/active-alerts/{alert_sender_id}/acknowledge")
async def acknowledge_alert(alert_sender_id: str, acknowledged_by: str = Query(..., description="Who acknowledged the alert")):
    """Acknowledge an active alert"""
    update_data = ActiveAlertUpdate(status=ActiveAlertStatus.ACKNOWLEDGED, resolved_by=acknowledged_by)
    updated_alert = alert_sender_service.update_alert_status(alert_sender_id, update_data)
    if not updated_alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Active alert not found")
    return {"message": "Alert acknowledged successfully", "alert": updated_alert}

@router.get("/active-alerts/{alert_sender_id}/history", response_model=AlertHistoryResponse)
async def get_alert_history(alert_sender_id: str):
    """Get complete alert history including all related raw alerts"""
    history = alert_sender_service.get_alert_history(alert_sender_id)
    if not history:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert history not found")
    return history

@router.get("/dashboard/summary")
async def get_alert_dashboard():
    """Get alert dashboard summary"""
    active_alerts = alert_sender_service.get_all_active_alerts("active")
    resolved_alerts = alert_sender_service.get_all_active_alerts("resolved")
    acknowledged_alerts = alert_sender_service.get_all_active_alerts("acknowledged")
    
    # Count by severity
    severity_counts = {}
    for alert in active_alerts:
        severity = alert.severity
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
    
    # Count by type
    type_counts = {}
    for alert in active_alerts:
        alert_type = alert.alert_type
        type_counts[alert_type] = type_counts.get(alert_type, 0) + 1
    
    return {
        "active_alerts_count": len(active_alerts),
        "resolved_alerts_count": len(resolved_alerts),
        "acknowledged_alerts_count": len(acknowledged_alerts),
        "alerts_by_severity": severity_counts,
        "alerts_by_type": type_counts,
        "recent_active_alerts": active_alerts[:10]  
    }
