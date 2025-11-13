"""The vasttrafik component.

This integration provides access to public transport information from Västtrafik.
It supports both departure boards and journey planning.
"""

from __future__ import annotations

import logging

import vasttrafik
import voluptuous as vol

from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType

from .const import (
    ATTR_END_STOP_ID,
    ATTR_END_STOP_NAME,
    ATTR_IS_END_ID,
    ATTR_IS_START_ID,
    ATTR_START_STOP_ID,
    ATTR_START_STOP_NAME,
    CONF_END_STOP,
    CONF_START_STOP,
    DOMAIN,
    SERVICE_PLAN_JOURNEY,
)
from .helpers import normalize_location

_LOGGER = logging.getLogger(__name__)

# Service schema for plan_journey, must be a string
PLAN_JOURNEY_SERVICE_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_START_STOP): cv.string,
        vol.Required(CONF_END_STOP): cv.string,
    }
)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Västtrafik integration.

    Function is called when integration first loads, it initializes the integration and registers services.
    """
    hass.data[DOMAIN] = {}
    return True


@callback
def setup_service(hass: HomeAssistant, planner: vasttrafik.JournyPlanner) -> None:
    """Function to setup and register the plan_journey service.

    This is called from sensor.py to register the service with a valid planner instance.
    """

    async def plan_journey_service(call: ServiceCall) -> None:
        """Handle the plan_journey service call (user's input).

        Accepts start and end stops as names or numeric IDs, normalises the input,
        and stores the results for the next subtask to call the Västtrafik API.
        """
        start_stop = call.data[CONF_START_STOP]
        end_stop = call.data[CONF_END_STOP]

        try:
            # Normalise start stop
            start_normalized = normalize_location(planner, start_stop)
            _LOGGER.debug(
                "Normalized start stop: %s -> ID: %s",
                start_stop,
                start_normalized["station_id"],
            )

            # Normalise end stop
            end_normalized = normalize_location(planner, end_stop)
            _LOGGER.debug(
                "Normalized end stop: %s -> ID: %s",
                end_stop,
                end_normalized["station_id"],
            )

            # Store the normalized data in hass.data for the next subtask
            hass.data[DOMAIN]["last_journey_plan"] = {
                ATTR_START_STOP_ID: start_normalized["station_id"],
                ATTR_START_STOP_NAME: start_normalized["station_name"],
                ATTR_IS_START_ID: start_normalized["is_numeric_id"],
                ATTR_END_STOP_ID: end_normalized["station_id"],
                ATTR_END_STOP_NAME: end_normalized["station_name"],
                ATTR_IS_END_ID: end_normalized["is_numeric_id"],
            }

            # This is a user-visible action. Logs a summary at INFO level.
            _LOGGER.info(
                "Journey plan normalized: from %s (%s) to %s (%s)",
                start_normalized["station_name"],
                start_normalized["station_id"],
                end_normalized["station_name"],
                end_normalized["station_id"],
            )

        # When normalize_location() can't find the location.
        except ValueError as err:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="invalid_location",
                translation_placeholders={"location": str(err)},
            ) from err
        # When other unexpected errors occur.
        except Exception as err:
            _LOGGER.error("Unexpected error in plan_journey service: %s", err)
            raise HomeAssistantError(f"Failed to plan journey: {err}") from err

    # Registers the service so users can call it.
    # hass.services.async_register(
    #     DOMAIN,
    #     SERVICE_PLAN_JOURNEY,
    #     plan_journey_service,
    #     schema=PLAN_JOURNEY_SERVICE_SCHEMA,
    # )
    _LOGGER.debug("Registered %s.%s service", DOMAIN, SERVICE_PLAN_JOURNEY)
