"""
PowerTrack Data Extractors Module
==================================

Data processing utilities for extracting and transforming PowerTrack API data
for database storage and analysis.

This module provides functions to process raw API responses into structured
database records.
"""

from typing import Dict, List, Any, Optional, Union
import logging

logger = logging.getLogger(__name__)


def process_site_for_database(site_key: str, json_data: Dict[str, Any], db_manager) -> bool:
    """
    Process complete site data for database storage.

    Args:
        site_key: Site identifier (e.g., "S60308")
        json_data: Complete site data from API responses
        db_manager: DatabaseManager instance

    Returns:
        bool: True if processing successful
    """
    try:
        logger.info(f"Processing site {site_key} for database storage")

        # Extract and process hardware data
        hardware_data = json_data.get('hardware', [])
        if hardware_data:
            _process_hardware_data(site_key, hardware_data, db_manager)

        # Extract and process alert data
        alert_data = json_data.get('alerts', [])
        if alert_data:
            _process_alert_data(site_key, alert_data, db_manager)

        # Extract and process modeling data
        modeling_data = json_data.get('modeling', {})
        if modeling_data:
            _process_modeling_data(site_key, modeling_data, db_manager)

        logger.info(f"Successfully processed site {site_key}")
        return True

    except Exception as e:
        logger.error(f"Failed to process site {site_key}: {e}")
        return False


def _process_hardware_data(site_key: str, hardware_data: List[Dict[str, Any]], db_manager) -> None:
    """Process hardware data for database storage."""
    for hardware in hardware_data:
        try:
            hardware_record = {
                'site_key': site_key,
                'hardware_key': hardware.get('key'),
                'name': hardware.get('name'),
                'type_code': hardware.get('functionCode'),
                'manufacturer': hardware.get('manufacturer'),
                'model': hardware.get('model'),
                'serial_number': hardware.get('serialNumber'),
                'status': hardware.get('status'),
                'last_updated': hardware.get('lastChanged')
            }
            db_manager.insert_hardware(hardware_record)
        except Exception as e:
            logger.warning(f"Failed to process hardware {hardware.get('key')}: {e}")


def _process_alert_data(site_key: str, alert_data: List[Dict[str, Any]], db_manager) -> None:
    """Process alert data for database storage."""
    for alert in alert_data:
        try:
            alert_record = {
                'site_key': site_key,
                'alert_key': alert.get('key'),
                'name': alert.get('name'),
                'type': alert.get('type'),
                'severity': alert.get('severity'),
                'status': alert.get('status'),
                'last_updated': alert.get('lastChanged')
            }
            db_manager.insert_alert(alert_record)
        except Exception as e:
            logger.warning(f"Failed to process alert {alert.get('key')}: {e}")


def _process_modeling_data(site_key: str, modeling_data: Dict[str, Any], db_manager) -> None:
    """Process modeling data for database storage."""
    try:
        modeling_record = {
            'site_key': site_key,
            'system_size_kw': modeling_data.get('systemSize'),
            'module_count': modeling_data.get('moduleCount'),
            'inverter_count': modeling_data.get('inverterCount'),
            'tilt_angle': modeling_data.get('tiltAngle'),
            'azimuth_angle': modeling_data.get('azimuthAngle'),
            'last_updated': modeling_data.get('lastChanged')
        }
        db_manager.insert_modeling(modeling_record)
    except Exception as e:
        logger.warning(f"Failed to process modeling data for {site_key}: {e}")


def extract_hardware_summary(site_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract hardware summary statistics from site data.

    Args:
        site_data: Raw site data from API

    Returns:
        Dict with hardware summary statistics
    """
    hardware = site_data.get('hardware', [])

    summary = {
        'total_devices': len(hardware),
        'inverters': 0,
        'meters': 0,
        'weather_stations': 0,
        'gateways': 0,
        'other_devices': 0
    }

    for device in hardware:
        func_code = device.get('functionCode')
        if func_code == 1:
            summary['inverters'] += 1
        elif func_code in [2, 3, 4, 20, 37]:
            summary['meters'] += 1
        elif func_code == 5:
            summary['weather_stations'] += 1
        elif func_code == 10:
            summary['gateways'] += 1
        else:
            summary['other_devices'] += 1

    return summary


def extract_alert_summary(site_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract alert summary statistics from site data.

    Args:
        site_data: Raw site data from API

    Returns:
        Dict with alert summary statistics
    """
    alerts = site_data.get('alerts', [])

    summary = {
        'total_alerts': len(alerts),
        'active_alerts': 0,
        'inactive_alerts': 0,
        'critical_alerts': 0,
        'warning_alerts': 0
    }

    for alert in alerts:
        status = alert.get('status', '').lower()
        if status == 'active':
            summary['active_alerts'] += 1
        else:
            summary['inactive_alerts'] += 1

        severity = alert.get('severity', '').lower()
        if severity == 'critical':
            summary['critical_alerts'] += 1
        elif severity == 'warning':
            summary['warning_alerts'] += 1

    return summary


def validate_site_data(site_data: Dict[str, Any]) -> List[str]:
    """
    Validate site data structure and return any issues found.

    Args:
        site_data: Raw site data from API

    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []

    required_keys = ['site_info', 'hardware', 'alerts', 'modeling']
    for key in required_keys:
        if key not in site_data:
            errors.append(f"Missing required key: {key}")

    hardware = site_data.get('hardware', [])
    if not isinstance(hardware, list):
        errors.append("Hardware data must be a list")
    else:
        for i, device in enumerate(hardware):
            if not device.get('key'):
                errors.append(f"Hardware device {i} missing key")
            if not device.get('functionCode'):
                errors.append(f"Hardware device {i} missing functionCode")

    return errors