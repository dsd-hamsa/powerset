"""
PowerTrack Database Module
==========================

Database operations for PowerTrack data storage and retrieval.
Provides a unified interface for database interactions across all scripts.

Usage:
    from powertrack.database import DatabaseManager

    db = DatabaseManager()
    db.insert_hardware(hardware_record)
    db.insert_alert(alert_record)
"""

from typing import Dict, List, Any, Optional, Union
import sqlite3
import logging
from contextlib import contextmanager
from datetime import datetime

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database operations for PowerTrack API data"""

    def __init__(self, db_path: str = 'portfolio/powertrack_data.db'):
        self.db_path = db_path
        self._persistent_conn = None
        # Ensure tables exist on initialization
        self.create_tables()

    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute("PRAGMA foreign_keys = ON")
            # Ensure tables exist for this connection
            self._ensure_tables(conn)
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def _ensure_tables(self, conn):
        """Ensure tables exist in the given connection"""
        cursor = conn.cursor()

        # Hardware table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hardware (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                site_key TEXT NOT NULL,
                hardware_key TEXT NOT NULL,
                name TEXT,
                type_code INTEGER,
                manufacturer TEXT,
                model TEXT,
                serial_number TEXT,
                status TEXT,
                last_updated TEXT,
                created_at TEXT,
                UNIQUE(site_key, hardware_key)
            )
        ''')

        # Alerts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                site_key TEXT NOT NULL,
                alert_key TEXT NOT NULL,
                name TEXT,
                type TEXT,
                severity TEXT,
                status TEXT,
                last_updated TEXT,
                created_at TEXT,
                UNIQUE(site_key, alert_key)
            )
        ''')

        # Modeling table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS modeling (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                site_key TEXT NOT NULL UNIQUE,
                system_size_kw REAL,
                module_count INTEGER,
                inverter_count INTEGER,
                tilt_angle REAL,
                azimuth_angle REAL,
                last_updated TEXT,
                created_at TEXT
            )
        ''')

        conn.commit()

    def insert_hardware(self, hardware_data: Dict[str, Any]) -> bool:
        """Insert hardware record into database"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    INSERT OR REPLACE INTO hardware (
                        site_key, hardware_key, name, type_code, manufacturer,
                        model, serial_number, status, last_updated, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    hardware_data['site_key'],
                    hardware_data['hardware_key'],
                    hardware_data['name'],
                    hardware_data['type_code'],
                    hardware_data.get('manufacturer'),
                    hardware_data.get('model'),
                    hardware_data.get('serial_number'),
                    hardware_data.get('status'),
                    hardware_data.get('last_updated'),
                    datetime.now().isoformat()
                ))

                conn.commit()
                logger.debug(f"Inserted hardware: {hardware_data['hardware_key']}")
                return True

        except Exception as e:
            logger.error(f"Failed to insert hardware: {e}")
            return False

    def insert_alert(self, alert_data: Dict[str, Any]) -> bool:
        """Insert alert record into database"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    INSERT OR REPLACE INTO alerts (
                        site_key, alert_key, name, type, severity,
                        status, last_updated, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    alert_data['site_key'],
                    alert_data['alert_key'],
                    alert_data['name'],
                    alert_data.get('type'),
                    alert_data.get('severity'),
                    alert_data.get('status'),
                    alert_data.get('last_updated'),
                    datetime.now().isoformat()
                ))

                conn.commit()
                logger.debug(f"Inserted alert: {alert_data['alert_key']}")
                return True

        except Exception as e:
            logger.error(f"Failed to insert alert: {e}")
            return False

    def insert_modeling(self, modeling_data: Dict[str, Any]) -> bool:
        """Insert modeling record into database"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    INSERT OR REPLACE INTO modeling (
                        site_key, system_size_kw, module_count, inverter_count,
                        tilt_angle, azimuth_angle, last_updated, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    modeling_data['site_key'],
                    modeling_data.get('system_size_kw'),
                    modeling_data.get('module_count'),
                    modeling_data.get('inverter_count'),
                    modeling_data.get('tilt_angle'),
                    modeling_data.get('azimuth_angle'),
                    modeling_data.get('last_updated'),
                    datetime.now().isoformat()
                ))

                conn.commit()
                logger.debug(f"Inserted modeling data for: {modeling_data['site_key']}")
                return True

        except Exception as e:
            logger.error(f"Failed to insert modeling data: {e}")
            return False

    def get_site_hardware(self, site_key: str) -> List[Dict[str, Any]]:
        """Retrieve all hardware for a site"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM hardware WHERE site_key = ?', (site_key,))
                rows = cursor.fetchall()

                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in rows]

        except Exception as e:
            logger.error(f"Failed to get hardware for {site_key}: {e}")
            return []

    def get_site_alerts(self, site_key: str) -> List[Dict[str, Any]]:
        """Retrieve all alerts for a site"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM alerts WHERE site_key = ?', (site_key,))
                rows = cursor.fetchall()

                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in rows]

        except Exception as e:
            logger.error(f"Failed to get alerts for {site_key}: {e}")
            return []

    def create_tables(self) -> bool:
        """Create necessary database tables if they don't exist"""
        try:
            with self.get_connection() as conn:
                # Tables are already created by _ensure_tables
                logger.info("Database tables created/verified")
                return True

        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
            return False

    def get_stats(self) -> Dict[str, int]:
        """Get database statistics"""
        stats = {'hardware_count': 0, 'alerts_count': 0, 'sites_count': 0}

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute('SELECT COUNT(*) FROM hardware')
                stats['hardware_count'] = cursor.fetchone()[0]

                cursor.execute('SELECT COUNT(*) FROM alerts')
                stats['alerts_count'] = cursor.fetchone()[0]

                cursor.execute('SELECT COUNT(DISTINCT site_key) FROM hardware')
                stats['sites_count'] = cursor.fetchone()[0]

        except Exception as e:
            logger.error(f"Failed to get stats: {e}")

        return stats