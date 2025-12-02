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
CONF_FROM0 = "from0"
CONF_HEADING0 = "heading0"
CONF_FROM1 = "from1"
CONF_HEADING1 = "heading1"
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
                vol.Required(CONF_FROM0): cv.string,
                vol.Required(CONF_HEADING0): cv.string,
                vol.Optional(CONF_FROM1): cv.string,
                vol.Optional(CONF_HEADING1): cv.string,
                vol.Optional(CONF_DELAY, default=DEFAULT_DELAY): cv.positive_int,
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
                departure.get(CONF_FROM0),
                departure.get(CONF_HEADING0),
                departure.get(CONF_FROM1),
                departure.get(CONF_HEADING1),
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

    def __init__(
        self, planner, name, departure0, heading0, departure1, heading1, lines, delay
    ):
        """Initialize the sensor."""
        self._planner = planner
        self._name = name or departure0
        self._departure = []
        self._heading = []
        self._departure.append(self.get_station_id(departure0))
        self._heading.append(self.get_station_id(heading0))
        self._departure.append(self.get_station_id(departure1))
        self._heading.append(self.get_station_id(heading1))
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
        c = self._get_journey(
            self._departure[0]["station_id"], self._heading[0]["station_id"]
        )

        if not c[0].get("isCancelled"):
            if "estimatedOtherwisePlannedDepartureTime" in c[0]:
                try:
                    self._state = datetime.fromisoformat(
                        c[0]["estimatedOtherwisePlannedDepartureTime"]
                    ).strftime("%H:%M")
                except ValueError:
                    self._state = c[0]["estimatedOtherwisePlannedDepartureTime"]
            else:
                self._state = None

            # Build full multileg attribute list
            legs0 = []

            for leg in c:
                origin = leg.get("origin", {}).get("stopPoint", {})
                dest = leg.get("destination", {}).get("stopPoint", {})
                service = leg.get("serviceJourney", {})
                line = service.get("line", {})

                legs0.append(
                    {
                        "from": origin.get("name"),
                        "to": dest.get("name"),
                        "line": line.get("shortName"),
                        "direction": service.get("shortDirection"),
                        "track": origin.get("platform"),
                        "accessible": line.get("isWheelchairAccessible"),
                        "time": line.get("estimatedOtherwisePlannedTime"),
                    }
                )

        c = self._get_journey(
            self._departure[1]["station_id"], self._heading[1]["station_id"]
        )

        if not c[0].get("isCancelled"):
            if "estimatedOtherwisePlannedDepartureTime" in c[0]:
                try:
                    self._state = datetime.fromisoformat(
                        c[0]["estimatedOtherwisePlannedDepartureTime"]
                    ).strftime("%H:%M")
                except ValueError:
                    self._state = c[0]["estimatedOtherwisePlannedDepartureTime"]
            else:
                self._state = None

            # Build full multileg attribute list
            legs1 = []

            for leg in c:
                origin = leg.get("origin", {}).get("stopPoint", {})
                dest = leg.get("destination", {}).get("stopPoint", {})
                service = leg.get("serviceJourney", {})
                line = service.get("line", {})

                legs1.append(
                    {
                        "from": origin.get("name"),
                        "to": dest.get("name"),
                        "line": line.get("shortName"),
                        "direction": service.get("shortDirection"),
                        "track": origin.get("platform"),
                        "accessible": line.get("isWheelchairAccessible"),
                        "time": datetime.fromisoformat(
                            line.get("estimatedOtherwisePlannedTime")
                        ).strftime("%H:%M"),
                    }
                )

        # Store attributes: full journey preserved
        self._attributes = {
            "journey0": {
                "legs": legs0,
                "from": legs0[0].get("from"),
                "to": legs0[-1].get("to"),
                "delay": legs0[0]["time"],
            },
            "journey1": {
                "legs": legs1,
                "from": legs1[0].get("from"),
                "to": legs1[-1].get("to"),
                "delay": legs1[0]["time"],
            },
        }

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
