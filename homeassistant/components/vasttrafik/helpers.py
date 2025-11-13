"""Helper utilities for the Västtrafik integration."""

from __future__ import annotations

import logging
from typing import Any

import vasttrafik

_LOGGER = logging.getLogger(__name__)


def is_numeric_id(location: str) -> bool:
    """Detect if location input is a numeric ID.

    Args:
        location: The location string to check

    Returns:
        True if the location is a numeric ID, False if it's a name
    """
    return location.isdecimal()


def normalize_location(
    planner: vasttrafik.JournyPlanner, location: str
) -> dict[str, Any]:
    """Normalize location input to both ID and name.

    Handles both numeric IDs and location names, converting them to a
    standardized format with both the station ID and station name.

    Args:
        planner: The Västtrafik journey planner instance
        location: The location as either a numeric ID string or a location name

    Returns:
        Dictionary with keys:
            - station_id: The numeric station ID
            - station_name: The human-readable station name
            - is_numeric_id: True if input was a numeric ID, False if it was a name

    Raises:
        ValueError: If the location name cannot be resolved to a station
    """
    if is_numeric_id(location):
        # Input is already a numeric ID - we don't have the name yet
        return {
            "station_id": location,
            "station_name": location,
            "is_numeric_id": True,
        }

    # Input is a location name - we need to look it up
    try:
        locations = planner.location_name(location)
        if not locations:
            raise ValueError(f"Location '{location}' not found")

        # Use the first match
        station_data = locations[0]
        return {
            "station_id": station_data["gid"],
            "station_name": location,
            "is_numeric_id": False,
        }
    except vasttrafik.Error as err:
        raise ValueError(f"Failed to resolve location '{location}': {err}") from err
