import sqlite3
import os
from contextlib import contextmanager
from typing import Generator

# Database file path
DB_FILE = "fleet_management.db"

def create_database_schema():
    schema_queries = [
        # Vehicles table
        """
        CREATE TABLE IF NOT EXISTS vehicles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vin TEXT UNIQUE NOT NULL,
            manufacturer TEXT NOT NULL,
            model TEXT NOT NULL,
            fleet_id TEXT NOT NULL,
            owner_operator TEXT NOT NULL,
            registration_status TEXT CHECK(registration_status IN ('Active', 'Maintenance', 'Decommissioned')) DEFAULT 'Active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        
        # Indexes for vehicles table
        "CREATE INDEX IF NOT EXISTS idx_vehicles_vin ON vehicles(vin)",
        "CREATE INDEX IF NOT EXISTS idx_vehicles_fleet_id ON vehicles(fleet_id)",
        
        # Telemetry data table
        """
        CREATE TABLE IF NOT EXISTS telemetry_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_vin TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            speed REAL NOT NULL,
            engine_status TEXT CHECK(engine_status IN ('On', 'Off', 'Idle')) NOT NULL,
            fuel_battery_level REAL CHECK(fuel_battery_level >= 0 AND fuel_battery_level <= 100) NOT NULL,
            odometer_reading REAL NOT NULL,
            diagnostic_codes TEXT DEFAULT '',
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (vehicle_vin) REFERENCES vehicles (vin) ON DELETE CASCADE
        )
        """,
        
        # Indexes for telemetry_data table
        "CREATE INDEX IF NOT EXISTS idx_telemetry_vehicle_vin ON telemetry_data(vehicle_vin)",
        "CREATE INDEX IF NOT EXISTS idx_telemetry_timestamp ON telemetry_data(timestamp)",
        
        # Alerts table
        """
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            alert_id TEXT UNIQUE NOT NULL,
            vehicle_vin TEXT NOT NULL,
            alert_type TEXT CHECK(alert_type IN ('speed_violation', 'low_fuel_battery')) NOT NULL,
            severity TEXT CHECK(severity IN ('low', 'medium', 'high')) NOT NULL,
            message TEXT NOT NULL,
            resolved INTEGER DEFAULT 0 CHECK(resolved IN (0, 1)),
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (vehicle_vin) REFERENCES vehicles (vin) ON DELETE CASCADE
        )
        """,
        
        # Indexes for alerts table
        "CREATE INDEX IF NOT EXISTS idx_alerts_alert_id ON alerts(alert_id)",
        "CREATE INDEX IF NOT EXISTS idx_alerts_vehicle_vin ON alerts(vehicle_vin)",
        "CREATE INDEX IF NOT EXISTS idx_alerts_timestamp ON alerts(timestamp)"
    ]
    
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        for query in schema_queries:
            conn.execute(query)
        conn.commit()
    
    print(f"Database initialized at: {os.path.abspath(DB_FILE)}")

def get_db_path() -> str:
    return os.path.abspath(DB_FILE)

def init_database():
    create_database_schema()

@contextmanager
def get_db_connection() -> Generator[sqlite3.Connection, None, None]:
    """Context manager for database connections"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # Enable dict-like access to rows
    conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
    try:
        yield conn
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def execute_query(query: str, params: tuple = ()) -> list:
    with get_db_connection() as conn:
        cursor = conn.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

def execute_insert(query: str, params: tuple = ()) -> int:
    with get_db_connection() as conn:
        cursor = conn.execute(query, params)
        conn.commit()
        return cursor.lastrowid

def execute_update(query: str, params: tuple = ()) -> int:
    with get_db_connection() as conn:
        cursor = conn.execute(query, params)
        conn.commit()
        return cursor.rowcount

