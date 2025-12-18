"""
PowerTrack Output Module
========================

Output directory management and file operations for PowerTrack scripts.

Usage:
    from powertrack.output import get_site_output_directory

    # Get organized output directory for a site
    output_dir = get_site_output_directory(site_id, site_info)
"""

from pathlib import Path
from typing import Dict, Any, Optional


def get_site_output_directory(
    site_id: str,
    site_info: Optional[Dict[str, Any]] = None,
    base_output_dir: str = "Sites"
) -> Path:
    """
    Determine the output directory for a site based on site configuration.

    Priority:
    1. Use outputDir from site_info (if provided in SiteList.json)
    2. Fall back to base_output_dir/site_id/

    Args:
        site_id: Site identifier (e.g., "S60308")
        site_info: Site information dict from SiteList.json (optional)
        base_output_dir: Base directory when no outputDir specified (default: "Sites")

    Returns:
        Path object pointing to the output directory (created if it doesn't exist)

    Example:
        site_info = {"key": "S34924", "outputDir": "portfolio/C8458/..."}

        output_dir = get_site_output_directory("S34924", site_info)
        # Output: portfolio/C8458/...
    """
    if site_info and site_info.get("outputDir"):
        # Use the custom output directory from site configuration
        output_dir = Path(site_info["outputDir"])
    else:
        # Fall back to standard structure: base_output_dir/site_id/
        output_dir = Path(base_output_dir) / site_id

    # Ensure the directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    return output_dir


def ensure_output_structure(output_dir: Path) -> None:
    """
    Ensure the standard output directory structure exists.

    Args:
        output_dir: Base output directory for the site
    """
    # Create standard subdirectories
    subdirs = ['Settings', 'Alerts', 'modeling']
    for subdir in subdirs:
        (output_dir / subdir).mkdir(parents=True, exist_ok=True)


def get_output_paths(output_dir: Path, site_id: str) -> Dict[str, Path]:
    """
    Get standard output file paths for a site.

    Args:
        output_dir: Base output directory
        site_id: Site identifier

    Returns:
        Dict of file paths for different data types
    """
    return {
        'complete_data': output_dir / f'{site_id}_complete.json',
        'hardware_data': output_dir / f'{site_id}_all_hardware.json',
        'hardware_csv': output_dir / f'{site_id}_hardware_summary.csv',
        'alerts_data': output_dir / 'Alerts' / f'{site_id}_all_alerts.json',
        'modeling_data': output_dir / 'modeling' / f'{site_id}_modeling.json',
        'modeling_summary': output_dir / 'modeling' / f'{site_id}_modeling_summary.json'
    }