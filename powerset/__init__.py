# PowerTrack Package
# =================
#
# A comprehensive Python package for PowerTrack solar monitoring platform automation.
#
# Features:
# - Unified authentication with automatic refresh
# - API client with intelligent retry logic
# - Organized logging and output management
# - Database integration for data persistence
# - Data extraction and processing utilities
#
# Quick Start:
#     from powertrack.api import APIClient
#     from powertrack.auth import load_env, update_auth_from_fetch
#
#     update_auth_from_fetch()  # Refresh auth
#     client = APIClient(load_env())  # Create API client
#     data = client.make_request('/api/sitehardware/S60308')  # Make requests
#
# For more examples, see the scripts/ directory.

__version__ = "1.0.0"
__author__ = "PowerTrack Automation Team"
__description__ = "Python package for PowerTrack solar monitoring platform automation"