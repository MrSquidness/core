"""Support for Västtrafik public transport."""

from __future__ import annotations

from datetime import datetime, timedelta
import logging

import vasttrafik
import voluptuous as vol

from homeassistant.components.sensor import (
    PLATFORM_SCHEMA as SENSOR_PLATFORM_SCHEMA,
    SensorEntity,
)
from homeassistant.const import CONF_DELAY, CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.util import Throttle

from . import setup_service

_LOGGER = logging.getLogger(__name__)

ATTR_ACCESSIBILITY = "accessibility"
ATTR_DIRECTION = "direction"
ATTR_LINE = "line"
ATTR_TRACK = "track"
ATTR_FROM = "from"
ATTR_TO = "to"
ATTR_DELAY = "delay"

CONF_DEPARTURES = "departures"
CONF_FROM = "from"
CONF_HEADING = "heading"
CONF_LINES = "lines"
CONF_KEY = "key"
CONF_SECRET = "secret"

DEFAULT_DELAY = 0

MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=120)

PLATFORM_SCHEMA = SENSOR_PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_KEY): cv.string,
        vol.Required(CONF_SECRET): cv.string,
        vol.Required(CONF_DEPARTURES): [
            {
                vol.Required(CONF_FROM): cv.string,
                vol.Optional(CONF_DELAY, default=DEFAULT_DELAY): cv.positive_int,
                vol.Optional(CONF_HEADING): cv.string,
                vol.Optional(CONF_LINES, default=[]): vol.All(
                    cv.ensure_list, [cv.string]
                ),
                vol.Optional(CONF_NAME): cv.string,
            }
        ],
    }
)


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the departure sensor."""
    planner = vasttrafik.JournyPlanner(config.get(CONF_KEY), config.get(CONF_SECRET))
    """Register the plan_journey service."""
    setup_service(hass, planner)
    add_entities(
        (
            VasttrafikDepartureSensor(
                planner,
                departure.get(CONF_NAME),
                departure.get(CONF_FROM),
                "",
                departure.get(CONF_HEADING),
                departure.get(CONF_LINES),
                departure.get(CONF_DELAY),
            )
            for departure in config[CONF_DEPARTURES]
        ),
        True,
    )


class VasttrafikDepartureSensor(SensorEntity):
    """Implementation of a Vasttrafik Departure Sensor."""

    _attr_attribution = "Data provided by Västtrafik"
    _attr_icon = "mdi:train"

    def __init__(self, planner, name, departure, stop, heading, lines, delay):
        """Initialize the sensor."""
        self._planner = planner
        self._name = name or departure
        self._departure = self.get_station_id(departure)
        if stop != "":
            self._stop = self.get_station_id(stop)
        else:
            self._stop = ""
        self._heading = self.get_station_id(heading)
        self._lines = lines if lines else None
        self._delay = timedelta(minutes=delay)
        self._journeys = None
        self._state = None
        self._attributes = None

    def get_station_id(self, location):
        """Get the station ID."""
        if location.isdecimal():
            station_info = {"station_name": location, "station_id": location}
        else:
            station_id = self._planner.location_name(location)[0]["gid"]
            station_info = {"station_name": location, "station_id": station_id}
        return station_info

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return self._attributes

    @property
    def native_value(self):
        """Return the next departure time."""
        return self._state

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self) -> None:
        if self._stop != "":
            a = self._get_journey(
                self._departure["station_id"], self._stop["station_id"]
            )
            b = self._get_journey(self._stop["station_id"], self._heading["station_id"])
            c = a + b
        else:
            c = self._get_journey(
                self._departure["station_id"], self._heading["station_id"]
            )

        departure = c[0]
        print(c)

        """Proof of function"""
        _LOGGER.debug(
            "%s ->",
            departure.get("origin", {}).get("stopPoint", {}).get("name", {}),
        )
        for trip in c:
            _LOGGER.debug(
                "-> %s",
                trip.get("destination", {}).get("stopPoint", {}).get("name", {}),
            )

        if not departure.get("isCancelled"):
            if "estimatedOtherwisePlannedDepartureTime" in departure:
                try:
                    self._state = datetime.fromisoformat(
                        departure["estimatedOtherwisePlannedDepartureTime"]
                    ).strftime("%H:%M")
                except ValueError:
                    self._state = departure["estimatedOtherwisePlannedDepartureTime"]
            else:
                self._state = None

            # Build full multileg attribute list
            legs = []

            for leg in c:
                origin = leg.get("origin", {}).get("stopPoint", {})
                dest = leg.get("destination", {}).get("stopPoint", {})
                service = leg.get("serviceJourney", {})
                line = service.get("line", {})

                legs.append(
                    {
                        "from": origin.get("name"),
                        "to": dest.get("name"),
                        "line": line.get("shortName"),
                        "direction": service.get("shortDirection"),
                        "track": origin.get("platform"),
                        "accessible": line.get("isWheelchairAccessible"),
                    }
                )

            # Store attributes: full journey preserved
            self._attributes = {
                "legs": legs,
                "from": legs[0].get("from"),
                "to": legs[-1].get("to"),
                "delay": self._delay.seconds // 60 % 60,
            }
        print(legs)

    def _get_journey(self, origin, destination) -> list:
        try:
            self._journeys = self._custom_journey_call(
                origin,
                destination,
            )
        except vasttrafik.Error:
            _LOGGER.debug("Unable to read departure board, updating token")
            self._planner.update_token()

        if not self._journeys:
            _LOGGER.debug(
                "No departures from departure station %s to destination station %s",
                origin,
                destination,
            )
            self._state = None
            self._attributes = {}
            print("EMPTY")
            return []
        trips = self._journeys[0].get("tripLegs", {})
        if trips:
            return trips
        return []

    # From journy_planner.py trip()
    def _custom_journey_call(self, origin_id, dest_id):
        request_parameters = {
            "originGid": origin_id,
            "destinationGid": dest_id,
            "originWalk": "50",
            "destWalk": "50",
        }
        response = self._planner._request(  # noqa: SLF001
            "journeys", **request_parameters
        )
        return vasttrafik.journy_planner._get_node(response, "results")  # noqa: SLF001
