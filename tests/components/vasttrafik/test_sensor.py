import pytest
import ast
import os

from homeassistant.core import HomeAssistant
from homeassistant.components.vasttrafik import sensor

from .conftest import vasttrafik_sensor, mock_api_result


async def test_update(hass, vasttrafik_sensor, mock_api_result) -> None:
    triplegs = mock_api_result["results"][0]["tripLegs"]

    vasttrafik_sensor.update()

    assert len(
        vasttrafik_sensor._attributes[vasttrafik_sensor._journeys[0]["name"]][
            sensor.ATTR_LEGS
        ]
    ) == len(triplegs)

    assert (
        vasttrafik_sensor._attributes[vasttrafik_sensor._journeys[0]["name"]][
            sensor.ATTR_FROM
        ]
        == triplegs[0]["origin"]["stopPoint"]["name"]
    )

    assert (
        vasttrafik_sensor._attributes[vasttrafik_sensor._journeys[0]["name"]][
            sensor.ATTR_TO
        ]
        == triplegs[-1]["destination"]["stopPoint"]["name"]
    )


async def test_build_legs_information(hass, vasttrafik_sensor, mock_api_result) -> None:
    triplegs = mock_api_result["results"][0]["tripLegs"]

    legs_information = vasttrafik_sensor._build_legs_information(triplegs)

    assert (
        legs_information[0][sensor.ATTR_LEG_FROM]
        == triplegs[0]["origin"]["stopPoint"]["name"]
    )
    assert (
        legs_information[0][sensor.ATTR_LEG_TO]
        == triplegs[0]["destination"]["stopPoint"]["name"]
    )
    assert (
        legs_information[0][sensor.ATTR_LEG_LINE]
        == triplegs[0]["serviceJourney"]["line"]["shortName"]
    )
    assert (
        legs_information[0][sensor.ATTR_LEG_DIRECTION]
        == triplegs[0]["serviceJourney"]["directionDetails"]["shortDirection"]
    )
    assert (
        legs_information[0][sensor.ATTR_LEG_TRACK]
        == triplegs[0]["origin"]["stopPoint"]["platform"]
    )
    assert (
        legs_information[0][sensor.ATTR_LEG_ACCESSIBILITY]
        == triplegs[0]["serviceJourney"]["line"]["isWheelchairAccessible"]
    )

    assert (
        legs_information[1][sensor.ATTR_LEG_TO]
        == triplegs[1]["destination"]["stopPoint"]["name"]
    )


async def test_get_journey(hass, vasttrafik_sensor, mock_api_result) -> None:
    triplegs = mock_api_result["results"][0]["tripLegs"]

    parsed_mock_api_result = vasttrafik_sensor._get_journey(
        vasttrafik_sensor._journeys[0]["from"]["station_id"],
        vasttrafik_sensor._journeys[0]["heading"]["station_id"],
        [],
    )

    assert (
        parsed_mock_api_result[0]["origin"]["stopPoint"]["name"]
        == triplegs[0]["origin"]["stopPoint"]["name"]
    )

    assert (
        parsed_mock_api_result[1]["origin"]["stopPoint"]["name"]
        == triplegs[1]["origin"]["stopPoint"]["name"]
    )
