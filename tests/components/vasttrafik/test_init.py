import pytest
import ast
import os

from homeassistant.core import HomeAssistant
from homeassistant.components.vasttrafik import sensor

from .conftest import vasttrafik_sensor


async def test_vasttrafik_init(hass, vasttrafik_sensor):
    assert vasttrafik_sensor._journeys[0]["name"] == "Journey 0"
    assert vasttrafik_sensor._journeys[0]["from"]["station_id"] == 0
    assert vasttrafik_sensor._journeys[0]["heading"]["station_name"] == "Lindholmen"
