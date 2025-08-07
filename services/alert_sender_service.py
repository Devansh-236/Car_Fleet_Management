from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
from models.alert_sender import (
    ActiveAlert, ActiveAlertCreate, ActiveAlertUpdate, 
    ActiveAlertResponse, AlertHistoryResponse, ActiveAlertStatus,
    ActiveAlertType, ActiveAlertSeverity
)
from database.connectDB import execute_query, execute_insert, execute_update

class AlertSenderService:
    
    @staticmethod
    def process_raw_alert(raw_alert: dict) -> Optional[ActiveAlertResponse]:
        existing_active_alert = AlertSenderService._get_active_alert_by_vehicle_and_type(
            raw_alert['vehicle_vin'], raw_alert['alert_type']
        )
        
        if existing_active_alert:
            return AlertSenderService._update_existing_active_alert(existing_active_alert, raw_alert)
        else:
            return AlertSenderService._create_new_active_alert(raw_alert)
    
    @staticmethod
    def _get_active_alert_by_vehicle_and_type(vehicle_vin: str, alert_type: str) -> Optional[dict]:
        query = """
            SELECT * FROM active_alerts 
            WHERE vehicle_vin = ? AND alert_type = ? AND status = 'active'
            ORDER BY created_at DESC LIMIT 1
        """
        results = execute_query(query, (vehicle_vin, alert_type))
        return results[0] if results else None
    
    @staticmethod
    def _create_new_active_alert(raw_alert: dict) -> ActiveAlertResponse:
        alert_sender_id = str(uuid.uuid4())
        
        # Generate title and description based on alert type
        title, description = AlertSenderService._generate_alert_content(raw_alert)
        
        query = """
            INSERT INTO active_alerts 
            (alert_sender_id, vehicle_vin, alert_type, severity, title, description, 
             first_occurrence, last_occurrence, occurrence_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        timestamp = datetime.fromisoformat(raw_alert['timestamp']) if isinstance(raw_alert['timestamp'], str) else raw_alert['timestamp']
        
        params = (
            alert_sender_id,
            raw_alert['vehicle_vin'],
            raw_alert['alert_type'],
            raw_alert['severity'],
            title,
            description,
            timestamp.isoformat(),
            timestamp.isoformat(),
            1
        )
        
        active_alert_id = execute_insert(query, params)
        AlertSenderService._link_raw_alert_to_active(active_alert_id, raw_alert['id'])
        return AlertSenderService.get_active_alert_by_id(active_alert_id)
    
    @staticmethod
    def _update_existing_active_alert(existing_alert: dict, raw_alert: dict) -> ActiveAlertResponse:
        timestamp = datetime.fromisoformat(raw_alert['timestamp']) if isinstance(raw_alert['timestamp'], str) else raw_alert['timestamp']
        
        # Update the active alert
        query = """
            UPDATE active_alerts 
            SET last_occurrence = ?, occurrence_count = occurrence_count + 1,
                severity = CASE 
                    WHEN ? = 'high' THEN 'high'
                    WHEN ? = 'critical' THEN 'critical'
                    ELSE severity 
                END
            WHERE id = ?
        """
        
        execute_update(query, (timestamp.isoformat(), raw_alert['severity'], raw_alert['severity'], existing_alert['id']))
        AlertSenderService._link_raw_alert_to_active(existing_alert['id'], raw_alert['id'])
        
        return AlertSenderService.get_active_alert_by_id(existing_alert['id'])
    
    @staticmethod
    def _link_raw_alert_to_active(active_alert_id: int, raw_alert_id: int):
        query = """
            INSERT OR IGNORE INTO alert_relationships (active_alert_id, raw_alert_id)
            VALUES (?, ?)
        """
        execute_insert(query, (active_alert_id, raw_alert_id))
    
    @staticmethod
    def _generate_alert_content(raw_alert: dict) -> tuple[str, str]:
        alert_type = raw_alert['alert_type']
        vehicle_vin = raw_alert['vehicle_vin']
        
        if alert_type == 'speed_violation':
            title = f"Speed Violation - {vehicle_vin}"
            description = f"Vehicle {vehicle_vin} is exceeding speed limits. {raw_alert['message']}"
        elif alert_type == 'low_fuel_battery':
            title = f"Low Fuel/Battery - {vehicle_vin}"
            description = f"Vehicle {vehicle_vin} has low fuel/battery level. {raw_alert['message']}"
        else:
            # This shouldn't happen with our current alert types, but just in case
            title = f"Alert - {vehicle_vin}"
            description = raw_alert['message']
        
        return title, description

    @staticmethod
    def get_active_alert_by_id(active_alert_id: int) -> Optional[ActiveAlertResponse]:
        query = """
            SELECT aa.*, COUNT(ar.raw_alert_id) as related_alerts_count
            FROM active_alerts aa
            LEFT JOIN alert_relationships ar ON aa.id = ar.active_alert_id
            WHERE aa.id = ?
            GROUP BY aa.id
        """
        results = execute_query(query, (active_alert_id,))
        
        if results:
            row = results[0]
            return ActiveAlertResponse(
                id=row['id'],
                alert_sender_id=row['alert_sender_id'],
                vehicle_vin=row['vehicle_vin'],
                alert_type=row['alert_type'],
                severity=row['severity'],
                title=row['title'],
                description=row['description'],
                status=row['status'],
                first_occurrence=datetime.fromisoformat(row['first_occurrence']),
                last_occurrence=datetime.fromisoformat(row['last_occurrence']),
                occurrence_count=row['occurrence_count'],
                resolved_at=datetime.fromisoformat(row['resolved_at']) if row['resolved_at'] else None,
                resolved_by=row['resolved_by'],
                created_at=datetime.fromisoformat(row['created_at']),
                related_alerts_count=row['related_alerts_count']
            )
        return None
    
    @staticmethod
    def get_all_active_alerts(status: Optional[str] = None) -> List[ActiveAlertResponse]:
        if status:
            query = """
                SELECT aa.*, COUNT(ar.raw_alert_id) as related_alerts_count
                FROM active_alerts aa
                LEFT JOIN alert_relationships ar ON aa.id = ar.active_alert_id
                WHERE aa.status = ?
                GROUP BY aa.id
                ORDER BY aa.last_occurrence DESC
            """
            results = execute_query(query, (status,))
        else:
            query = """
                SELECT aa.*, COUNT(ar.raw_alert_id) as related_alerts_count
                FROM active_alerts aa
                LEFT JOIN alert_relationships ar ON aa.id = ar.active_alert_id
                GROUP BY aa.id
                ORDER BY aa.last_occurrence DESC
            """
            results = execute_query(query)
        
        active_alerts = []
        for row in results:
            active_alerts.append(ActiveAlertResponse(
                id=row['id'],
                alert_sender_id=row['alert_sender_id'],
                vehicle_vin=row['vehicle_vin'],
                alert_type=row['alert_type'],
                severity=row['severity'],
                title=row['title'],
                description=row['description'],
                status=row['status'],
                first_occurrence=datetime.fromisoformat(row['first_occurrence']),
                last_occurrence=datetime.fromisoformat(row['last_occurrence']),
                occurrence_count=row['occurrence_count'],
                resolved_at=datetime.fromisoformat(row['resolved_at']) if row['resolved_at'] else None,
                resolved_by=row['resolved_by'],
                created_at=datetime.fromisoformat(row['created_at']),
                related_alerts_count=row['related_alerts_count']
            ))
        
        return active_alerts
    
    @staticmethod
    def get_active_alerts_by_vehicle(vehicle_vin: str) -> List[ActiveAlertResponse]:
        query = """
            SELECT aa.*, COUNT(ar.raw_alert_id) as related_alerts_count
            FROM active_alerts aa
            LEFT JOIN alert_relationships ar ON aa.id = ar.active_alert_id
            WHERE aa.vehicle_vin = ?
            GROUP BY aa.id
            ORDER BY aa.last_occurrence DESC
        """
        results = execute_query(query, (vehicle_vin,))
        
        active_alerts = []
        for row in results:
            active_alerts.append(ActiveAlertResponse(
                id=row['id'],
                alert_sender_id=row['alert_sender_id'],
                vehicle_vin=row['vehicle_vin'],
                alert_type=row['alert_type'],
                severity=row['severity'],
                title=row['title'],
                description=row['description'],
                status=row['status'],
                first_occurrence=datetime.fromisoformat(row['first_occurrence']),
                last_occurrence=datetime.fromisoformat(row['last_occurrence']),
                occurrence_count=row['occurrence_count'],
                resolved_at=datetime.fromisoformat(row['resolved_at']) if row['resolved_at'] else None,
                resolved_by=row['resolved_by'],
                created_at=datetime.fromisoformat(row['created_at']),
                related_alerts_count=row['related_alerts_count']
            ))
        
        return active_alerts
    
    @staticmethod
    def update_alert_status(alert_sender_id: str, update_data: ActiveAlertUpdate) -> Optional[ActiveAlertResponse]:
        set_clauses = []
        params = []
        
        if update_data.status:
            set_clauses.append("status = ?")
            params.append(update_data.status.value)
            
            if update_data.status == ActiveAlertStatus.RESOLVED:
                set_clauses.append("resolved_at = ?")
                params.append(datetime.now().isoformat())
        
        if update_data.resolved_by:
            set_clauses.append("resolved_by = ?")
            params.append(update_data.resolved_by)
        
        if not set_clauses:
            return None
        
        params.append(alert_sender_id)
        
        query = f"""
            UPDATE active_alerts 
            SET {', '.join(set_clauses)}
            WHERE alert_sender_id = ?
        """
        
        affected_rows = execute_update(query, tuple(params))
        
        if affected_rows > 0:
            get_query = "SELECT id FROM active_alerts WHERE alert_sender_id = ?"
            result = execute_query(get_query, (alert_sender_id,))
            if result:
                return AlertSenderService.get_active_alert_by_id(result[0]['id'])
        
        return None
    
    @staticmethod
    def get_alert_history(alert_sender_id: str) -> Optional[AlertHistoryResponse]:
        get_active_query = "SELECT id FROM active_alerts WHERE alert_sender_id = ?"
        active_result = execute_query(get_active_query, (alert_sender_id,))
        
        if not active_result:
            return None
        
        active_alert = AlertSenderService.get_active_alert_by_id(active_result[0]['id'])
        
        get_raw_alerts_query = """
            SELECT a.* FROM alerts a
            INNER JOIN alert_relationships ar ON a.id = ar.raw_alert_id
            WHERE ar.active_alert_id = ?
            ORDER BY a.timestamp DESC
        """
        raw_alerts = execute_query(get_raw_alerts_query, (active_result[0]['id'],))
        
        return AlertHistoryResponse(
            active_alert=active_alert,
            raw_alerts=raw_alerts
        )

alert_sender_service = AlertSenderService()
