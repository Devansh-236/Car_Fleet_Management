from typing import Dict, Any
from datetime import datetime, timedelta
from collections import Counter
from app.database.connection import execute_query

class AnalyticsService:
    @staticmethod
    def get_fleet_analytics() -> Dict[str, Any]:
        cutoff_time = datetime.now() - timedelta(hours=24)
        cutoff_iso = cutoff_time.isoformat()
        total_vehicles_query = "SELECT COUNT(*) as count FROM vehicles"
        total_vehicles = execute_query(total_vehicles_query)[0]['count']
        active_vehicles_query = """
            SELECT COUNT(DISTINCT vehicle_vin) as count 
            FROM telemetry_data 
            WHERE timestamp > ?
        """
        active_vehicles = execute_query(active_vehicles_query, (cutoff_iso,))[0]['count']
        inactive_vehicles = total_vehicles - active_vehicles
        
        avg_fuel_query = """
            SELECT AVG(fuel_battery_level) as avg_fuel 
            FROM telemetry_data 
            WHERE timestamp > ?
        """
        avg_fuel_result = execute_query(avg_fuel_query, (cutoff_iso,))
        avg_fuel_battery = round(avg_fuel_result[0]['avg_fuel'] or 0, 2)
        
        total_distance_query = """
            SELECT SUM(latest_odometer.odometer_reading) as total_distance
            FROM (
                SELECT DISTINCT vehicle_vin, 
                MAX(odometer_reading) as odometer_reading
                FROM telemetry_data 
                WHERE timestamp > ?
                GROUP BY vehicle_vin
            ) as latest_odometer
        """
        total_distance_result = execute_query(total_distance_query, (cutoff_iso,))
        total_distance = round(total_distance_result[0]['total_distance'] or 0, 2)

        all_alerts_query = "SELECT alert_type, severity FROM alerts"
        all_alerts = execute_query(all_alerts_query)
        
        alert_type_counts = Counter(alert['alert_type'] for alert in all_alerts)
        alert_severity_counts = Counter(alert['severity'] for alert in all_alerts)
        
        return {
            "vehicle_status": {
                "active_vehicles": active_vehicles,
                "inactive_vehicles": inactive_vehicles,
                "total_vehicles": total_vehicles
            },
            "fuel_battery_analytics": {
                "average_fuel_battery_level": avg_fuel_battery
            },
            "distance_analytics": {
                "total_distance_24h": total_distance
            },
            "alert_summary": {
                "total_alerts": len(all_alerts),
                "by_type": dict(alert_type_counts),
                "by_severity": dict(alert_severity_counts)
            }
        }

analytics_service = AnalyticsService()
