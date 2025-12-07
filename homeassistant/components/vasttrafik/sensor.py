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
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.util import Throttle

_LOGGER = logging.getLogger(__name__)

ATTR_ACCESSIBILITY = "accessibility"
ATTR_DIRECTION = "direction"
ATTR_LINE = "line"
ATTR_TRACK = "track"
ATTR_FROM = "from"
ATTR_TO = "to"
ATTR_DELAY = "delay"

CONF_DEPARTURES = "departures"
CONF_JOURNEY_NAME = "name"
CONF_JOURNEY_FROM = "from"
CONF_JOURNEY_HEADING = "heading"
CONF_JOURNEY_DELAY = "delay"
CONF_LINES = "lines"
CONF_KEY = "key"
CONF_SECRET = "secret"
CONF_TRANSFERS = "transfers"

DEFAULT_DELAY = 0

MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=120)

PLATFORM_SCHEMA = SENSOR_PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_KEY): cv.string,
        vol.Required(CONF_SECRET): cv.string,
        vol.Required(CONF_DEPARTURES): [
            {
                vol.Optional(CONF_JOURNEY_NAME): cv.string,
                vol.Required(CONF_JOURNEY_FROM): cv.string,
                vol.Required(CONF_JOURNEY_HEADING): cv.string,
                vol.Optional(
                    CONF_JOURNEY_DELAY, default=DEFAULT_DELAY
                ): cv.positive_int,
                vol.Optional(CONF_TRANSFERS, default=[]): vol.All(
                    cv.ensure_list, [cv.string]
                ),
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
    add_entities(
        (
            VasttrafikDepartureSensor(
                planner,
                config[CONF_DEPARTURES],
                [],
                0,
            )
            for i in range(1)
        ),
        True,
    )


class VasttrafikDepartureSensor(SensorEntity):
    """Implementation of a Vasttrafik Departure Sensor."""

    _attr_attribution = "Data provided by Västtrafik"
    _attr_icon = "mdi:train"

    def __init__(self, planner, journeys, lines, delay):
        """Initialize the sensor."""
        self._planner = planner
        self._name = "Vasttrafik"
        self._journeys = []

        i = 0
        for journey in journeys:
            if CONF_JOURNEY_NAME in journey:
                journey_name = journey[CONF_JOURNEY_NAME]
            else:
                journey_name = "Journey " + str(i)

            journey_from = self.get_station_id(journey[CONF_JOURNEY_FROM])
            journey_heading = self.get_station_id(journey[CONF_JOURNEY_HEADING])
            transfers = [
                self.get_station_id(t) for t in journey.get(CONF_TRANSFERS, [])
            ]

            self._journeys.append(
                {
                    "name": journey_name,
                    "from": journey_from,
                    "heading": journey_heading,
                    "transfers": transfers,
                }
            )
            i += 1

        self._lines = lines if lines else None
        self._delay = timedelta(minutes=delay)
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
        return self._name

    @property
    def extra_state_attributes(self):
        return self._attributes

    @property
    def native_value(self):
        return self._state

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self) -> None:
        self._attributes = {}

        for journey in self._journeys:
            transfer_ids = [t["station_id"] for t in journey["transfers"]]

            journey_trip_legs = self._get_journey(
                journey["from"]["station_id"],
                journey["heading"]["station_id"],
                transfer_ids,
            )

            if not journey_trip_legs or journey_trip_legs[0].get("isCancelled"):
                self._attributes[journey["name"]] = {
                    "legs": [],
                    "from": journey["from"]["station_id"],
                    "to": journey["from"]["station_id"],
                    "delay": 0,
                }
                continue

            if "estimatedOtherwisePlannedDepartureTime" in journey_trip_legs[0]:
                try:
                    self._state = datetime.fromisoformat(
                        journey_trip_legs[0]["estimatedOtherwisePlannedDepartureTime"]
                    ).strftime("%H:%M")
                except ValueError:
                    self._state = journey_trip_legs[0][
                        "estimatedOtherwisePlannedDepartureTime"
                    ]
            else:
                self._state = None

            legs_information = []

            for leg in journey_trip_legs:
                origin = leg.get("origin", {}).get("stopPoint", {})
                dest = leg.get("destination", {}).get("stopPoint", {})
                service = leg.get("serviceJourney", {})
                line = service.get("line", {})

                legs_information.append(
                    {
                        "from": origin.get("name"),
                        "to": dest.get("name"),
                        "line": line.get("shortName"),
                        "direction": service.get("shortDirection"),
                        "track": origin.get("platform"),
                        "accessible": line.get("isWheelchairAccessible"),
                        "time": datetime.fromisoformat(
                            leg.get("estimatedOtherwisePlannedDepartureTime")
                        ).strftime("%H:%M"),
                    }
                )

            self._attributes[journey["name"]] = {
                "legs": legs_information,
                "from": legs_information[0].get("from"),
                "to": legs_information[-1].get("to"),
                "delay": legs_information[0]["time"],
            }

    def _get_journey(self, origin, destination, transfers) -> list:
        if not transfers:
            return self._call_simple(origin, destination)

        full_trip = []
        points = [origin] + transfers + [destination]

        for i in range(len(points) - 1):
            part = self._call_simple(points[i], points[i + 1])
            if not part:
                return []
            full_trip.extend(part)

        return full_trip

    def _call_simple(self, origin_id, dest_id):
        try:
            api_return = self._custom_journey_call(origin_id, dest_id)
        except vasttrafik.Error:
            _LOGGER.debug("Updating token after error")
            self._planner.update_token()
            return []

        if not api_return:
            return []

        trips = api_return[0].get("tripLegs", {})
        if trips:
            return trips
        return []

    def _custom_journey_call(self, origin_id, dest_id):
        request_parameters = {
            "originGid": origin_id,
            "destinationGid": dest_id,
            "originWalk": "50",
            "destWalk": "50",
            "useRealTimeMode": "true",
        }
        response = self._planner._request("journeys", **request_parameters)
        return vasttrafik.journy_planner._get_node(response, "results")
