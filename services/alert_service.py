from typing import List, Optional
from datetime import datetime
import uuid
from models.alert import Alert, AlertType, AlertSeverity, AlertResponse
from database.connectDB import execute_query, execute_insert

class AlertService:
    SPEED_LIMIT = 80.0  # km/h , taken as default speed limit
    LOW_FUEL_THRESHOLD = 15.0  # taken as default low fuel/battery threshold percentage

    @staticmethod
    def process_telemetry_alerts(telemetry_data) -> List[Alert]:
        alerts = []
        
        # Speed violation check
        if telemetry_data['speed'] > AlertService.SPEED_LIMIT:
            alert_id = str(uuid.uuid4())
            query = """
                INSERT INTO alerts (alert_id, vehicle_vin, alert_type, severity, message, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            params = (
                alert_id,
                telemetry_data['vehicle_vin'],
                AlertType.SPEED_VIOLATION.value,
                AlertSeverity.HIGH.value,
                f"Speed violation: {telemetry_data['speed']} km/h (limit: {AlertService.SPEED_LIMIT} km/h)",
                telemetry_data['timestamp'].isoformat()
            )
            execute_insert(query, params)
            alert = AlertService.get_alert(alert_id)
            if alert:
                alerts.append(alert)
        
        # Low fuel/battery check
        if telemetry_data['fuel_battery_level'] < AlertService.LOW_FUEL_THRESHOLD:
            severity = AlertSeverity.HIGH if telemetry_data['fuel_battery_level'] < 5 else AlertSeverity.MEDIUM
            alert_id = str(uuid.uuid4())
            query = """
                INSERT INTO alerts (alert_id, vehicle_vin, alert_type, severity, message, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            params = (
                alert_id,
                telemetry_data['vehicle_vin'],
                AlertType.LOW_FUEL_BATTERY.value,
                severity.value,
                f"Low fuel/battery level: {telemetry_data['fuel_battery_level']}%",
                telemetry_data['timestamp'].isoformat()
            )
            execute_insert(query, params)
            alert = AlertService.get_alert(alert_id)
            if alert:
                alerts.append(alert)
        
        return alerts
    
    @staticmethod
    def get_alert(alert_id: str) -> Optional[Alert]:
        query = "SELECT * FROM alerts WHERE alert_id = ?"
        results = execute_query(query, (alert_id,))
        if results:
            row = results[0]
            return Alert(
                id=row['id'],
                alert_id=row['alert_id'],
                vehicle_vin=row['vehicle_vin'],
                alert_type=row['alert_type'],
                severity=row['severity'],
                message=row['message'],
                resolved=bool(row['resolved']),
                timestamp=datetime.fromisoformat(row['timestamp'])
            )
        return None
    
    @staticmethod
    def get_all_alerts() -> List[AlertResponse]:
        query = "SELECT * FROM alerts ORDER BY timestamp DESC"
        results = execute_query(query)
        alerts = []
        for row in results:
            alerts.append(AlertResponse(
                id=row['id'],
                alert_id=row['alert_id'],
                vehicle_vin=row['vehicle_vin'],
                alert_type=row['alert_type'],
                severity=row['severity'],
                message=row['message'],
                resolved=bool(row['resolved']),
                timestamp=datetime.fromisoformat(row['timestamp'])
            ))
        return alerts
    
    @staticmethod
    def get_alerts_by_vin(vin: str) -> List[AlertResponse]:
        query = "SELECT * FROM alerts WHERE vehicle_vin = ? ORDER BY timestamp DESC"
        results = execute_query(query, (vin,))
        alerts = []
        for row in results:
            alerts.append(AlertResponse(
                id=row['id'],
                alert_id=row['alert_id'],
                vehicle_vin=row['vehicle_vin'],
                alert_type=row['alert_type'],
                severity=row['severity'],
                message=row['message'],
                resolved=bool(row['resolved']),
                timestamp=datetime.fromisoformat(row['timestamp'])
            ))
        return alerts

alert_service = AlertService()
