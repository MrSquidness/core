import pytest
from homeassistant.core import HomeAssistant

from homeassistant.components.vasttrafik import sensor


class MockPlanner:
    def location_name(self, location):
        if location == "Chalmers":
            return [{"gid": 0}]
        elif location == "Lindholmen":
            return [{"gid": 1}]
        else:
            return -1

    def update_token(self):
        return

    def _request(self, call, **parameters):
        return api_result


@pytest.fixture
async def vasttrafik_sensor(hass: HomeAssistant):
    mock_journeys = [
        {
            sensor.CONF_JOURNEY_FROM: "Chalmers",
            sensor.CONF_JOURNEY_HEADING: "Lindholmen",
        }
    ]
    return sensor.VasttrafikDepartureSensor(MockPlanner(), mock_journeys, None, 0)


@pytest.fixture
async def mock_api_result(hass: HomeAssistant):
    return api_result


api_result = {
    "results": [
        {
            "reconstructionReference": "¶HKI¶T$A=1@O=Engdahlsgatan, Göteborg@L=2230001@a=128@$A=1@O=Vasaplatsen, Göteborg@L=7300003@a=128@$202511121408$202511121416$Bus   61$$1$$$$$$§T$A=1@O=Vasaplatsen, Göteborg@L=7300003@a=128@$A=1@O=Lindholmen, Göteborg@L=4490004@a=128@$202511121423$202511121441$Bus   16$$1$$$$$$¶KC¶#VE#2#CF#100#CA#0#CM#0#SICT#0#AM#17#AM2#0#RT#15#¶KRCC¶#VE#1#VOLL#IST#",
            "detailsReference": "eyJUIjpbeyJSIjoiMXw4ODMxfDR8ODB8MTIxMTIwMjUiLCJPIjo1LCJEIjo5LCJJIjowLCJDTCI6ZmFsc2UsIlBDTCI6ZmFsc2V9LHsiUiI6IjF8NDg0N3wyfDgwfDEyMTEyMDI1IiwiTyI6OCwiRCI6MTUsIkkiOjEsIkNMIjpmYWxzZSwiUENMIjpmYWxzZX1dfQ",
            "tripLegs": [
                {
                    "origin": {
                        "stopPoint": {
                            "gid": "9022014002230001",
                            "name": "Engdahlsgatan, Göteborg",
                            "platform": "A",
                            "latitude": 57.68670653,
                            "longitude": 11.98316348,
                            "stopArea": {
                                "gid": "9021014002230000",
                                "name": "Engdahlsgatan",
                                "latitude": 57.68666008,
                                "longitude": 11.98310022,
                                "tariffZone1": {
                                    "gid": "9081014200003000",
                                    "name": "Zon A",
                                    "number": 3000,
                                    "shortName": "A",
                                },
                            },
                        },
                        "plannedTime": "2025-11-12T14:08:00.0000000+01:00",
                        "estimatedTime": "2025-11-12T14:17:00.0000000+01:00",
                        "estimatedOtherwisePlannedTime": "2025-11-12T14:17:00.0000000+01:00",
                        "notes": [],
                    },
                    "destination": {
                        "stopPoint": {
                            "gid": "9022014007300003",
                            "name": "Vasaplatsen, Göteborg",
                            "platform": "C",
                            "latitude": 57.69954118,
                            "longitude": 11.96925315,
                            "stopArea": {
                                "gid": "9021014007300000",
                                "name": "Vasaplatsen",
                                "latitude": 57.69912227,
                                "longitude": 11.96977501,
                                "tariffZone1": {
                                    "gid": "9081014200003000",
                                    "name": "Zon A",
                                    "number": 3000,
                                    "shortName": "A",
                                },
                            },
                        },
                        "plannedTime": "2025-11-12T14:16:00.0000000+01:00",
                        "estimatedTime": "2025-11-12T14:23:00.0000000+01:00",
                        "estimatedOtherwisePlannedTime": "2025-11-12T14:23:00.0000000+01:00",
                        "notes": [],
                    },
                    "isCancelled": False,
                    "isPartCancelled": False,
                    "serviceJourney": {
                        "gid": "9015014506100113",
                        "direction": "Masthugget, Påstigning fram",
                        "directionDetails": {
                            "fullDirection": "Masthugget, Påstigning fram",
                            "shortDirection": "Masthugget",
                            "isFrontEntry": True,
                        },
                        "number": "113",
                        "line": {
                            "shortName": "61",
                            "designation": "61",
                            "isWheelchairAccessible": True,
                            "name": "Buss 61",
                            "backgroundColor": "#ffff50",
                            "foregroundColor": "#0061eb",
                            "borderColor": "#ffff50",
                            "isRealtimeJourney": False,
                            "transportMode": "bus",
                            "transportSubMode": "none",
                        },
                    },
                    "notes": [],
                    "plannedDepartureTime": "2025-11-12T14:08:00.0000000+01:00",
                    "plannedArrivalTime": "2025-11-12T14:16:00.0000000+01:00",
                    "plannedDurationInMinutes": 8,
                    "estimatedDepartureTime": "2025-11-12T14:17:00.0000000+01:00",
                    "estimatedArrivalTime": "2025-11-12T14:23:00.0000000+01:00",
                    "estimatedDurationInMinutes": 6,
                    "estimatedOtherwisePlannedArrivalTime": "2025-11-12T14:23:00.0000000+01:00",
                    "estimatedOtherwisePlannedDepartureTime": "2025-11-12T14:17:00.0000000+01:00",
                    "journeyLegIndex": 0,
                },
                {
                    "origin": {
                        "stopPoint": {
                            "gid": "9022014007300003",
                            "name": "Vasaplatsen, Göteborg",
                            "platform": "C",
                            "latitude": 57.69954118,
                            "longitude": 11.96925315,
                            "stopArea": {
                                "gid": "9021014007300000",
                                "name": "Vasaplatsen",
                                "latitude": 57.69912227,
                                "longitude": 11.96977501,
                                "tariffZone1": {
                                    "gid": "9081014200003000",
                                    "name": "Zon A",
                                    "number": 3000,
                                    "shortName": "A",
                                },
                            },
                        },
                        "plannedTime": "2025-11-12T14:23:00.0000000+01:00",
                        "estimatedTime": "2025-11-12T14:26:00.0000000+01:00",
                        "estimatedOtherwisePlannedTime": "2025-11-12T14:26:00.0000000+01:00",
                        "notes": [],
                    },
                    "destination": {
                        "stopPoint": {
                            "gid": "9022014004490004",
                            "name": "Lindholmen, Göteborg",
                            "platform": "D",
                            "latitude": 57.7080502,
                            "longitude": 11.93742673,
                            "stopArea": {
                                "gid": "9021014004490000",
                                "name": "Lindholmen",
                                "latitude": 57.70770985,
                                "longitude": 11.93673345,
                                "tariffZone1": {
                                    "gid": "9081014200003000",
                                    "name": "Zon A",
                                    "number": 3000,
                                    "shortName": "A",
                                },
                            },
                        },
                        "plannedTime": "2025-11-12T14:41:00.0000000+01:00",
                        "estimatedTime": "2025-11-12T14:42:00.0000000+01:00",
                        "estimatedOtherwisePlannedTime": "2025-11-12T14:42:00.0000000+01:00",
                        "notes": [],
                    },
                    "isCancelled": False,
                    "isPartCancelled": False,
                    "serviceJourney": {
                        "gid": "9015014501600142",
                        "direction": "Västra Eriksberg",
                        "directionDetails": {
                            "fullDirection": "Västra Eriksberg",
                            "shortDirection": "Västra Eriksberg",
                        },
                        "number": "142",
                        "line": {
                            "shortName": "16",
                            "designation": "16",
                            "isWheelchairAccessible": True,
                            "name": "Buss 16",
                            "backgroundColor": "#007c4f",
                            "foregroundColor": "#ffff50",
                            "borderColor": "#007c4f",
                            "isRealtimeJourney": False,
                            "transportMode": "bus",
                            "transportSubMode": "none",
                        },
                    },
                    "notes": [],
                    "plannedConnectingTimeInMinutes": 7,
                    "estimatedConnectingTimeInMinutes": 3,
                    "isRiskOfMissingConnection": False,
                    "plannedDepartureTime": "2025-11-12T14:23:00.0000000+01:00",
                    "plannedArrivalTime": "2025-11-12T14:41:00.0000000+01:00",
                    "plannedDurationInMinutes": 18,
                    "estimatedDepartureTime": "2025-11-12T14:26:00.0000000+01:00",
                    "estimatedArrivalTime": "2025-11-12T14:42:00.0000000+01:00",
                    "estimatedDurationInMinutes": 16,
                    "estimatedOtherwisePlannedArrivalTime": "2025-11-12T14:42:00.0000000+01:00",
                    "estimatedOtherwisePlannedDepartureTime": "2025-11-12T14:26:00.0000000+01:00",
                    "journeyLegIndex": 1,
                },
            ],
            "connectionLinks": [],
            "isDeparted": True,
        },
        {
            "reconstructionReference": "¶HKI¶T$A=1@O=Engdahlsgatan, Göteborg@L=2230001@a=128@$A=1@O=Grönsakstorget, Göteborg@L=2850001@a=128@$202511121418$202511121427$Bus   61$$1$$$$$$§T$A=1@O=Grönsakstorget, Göteborg@L=2850001@a=128@$A=1@O=Lindholmen, Göteborg@L=4490004@a=128@$202511121435$202511121451$Bus   16$$1$$$$$$¶KC¶#VE#2#CF#100#CA#0#CM#0#SICT#0#AM#17#AM2#0#RT#15#¶KRCC¶#VE#1#",
            "detailsReference": "eyJUIjpbeyJSIjoiMXw4ODMxfDV8ODB8MTIxMTIwMjUiLCJPIjo1LCJEIjoxMCwiSSI6MCwiQ0wiOmZhbHNlLCJQQ0wiOmZhbHNlfSx7IlIiOiIxfDQ4NDd8M3w4MHwxMjExMjAyNSIsIk8iOjksIkQiOjE1LCJJIjoxLCJDTCI6ZmFsc2UsIlBDTCI6ZmFsc2V9XX0",
            "tripLegs": [
                {
                    "origin": {
                        "stopPoint": {
                            "gid": "9022014002230001",
                            "name": "Engdahlsgatan, Göteborg",
                            "platform": "A",
                            "latitude": 57.68670653,
                            "longitude": 11.98316348,
                            "stopArea": {
                                "gid": "9021014002230000",
                                "name": "Engdahlsgatan",
                                "latitude": 57.68666008,
                                "longitude": 11.98310022,
                                "tariffZone1": {
                                    "gid": "9081014200003000",
                                    "name": "Zon A",
                                    "number": 3000,
                                    "shortName": "A",
                                },
                            },
                        },
                        "plannedTime": "2025-11-12T14:18:00.0000000+01:00",
                        "estimatedTime": "2025-11-12T14:23:00.0000000+01:00",
                        "estimatedOtherwisePlannedTime": "2025-11-12T14:23:00.0000000+01:00",
                        "notes": [],
                    },
                    "destination": {
                        "stopPoint": {
                            "gid": "9022014002850001",
                            "name": "Grönsakstorget, Göteborg",
                            "platform": "A",
                            "latitude": 57.7025284,
                            "longitude": 11.96489012,
                            "stopArea": {
                                "gid": "9021014002850000",
                                "name": "Grönsakstorget",
                                "latitude": 57.70249064,
                                "longitude": 11.96443998,
                                "tariffZone1": {
                                    "gid": "9081014200003000",
                                    "name": "Zon A",
                                    "number": 3000,
                                    "shortName": "A",
                                },
                            },
                        },
                        "plannedTime": "2025-11-12T14:27:00.0000000+01:00",
                        "estimatedTime": "2025-11-12T14:31:00.0000000+01:00",
                        "estimatedOtherwisePlannedTime": "2025-11-12T14:31:00.0000000+01:00",
                        "notes": [],
                    },
                    "isCancelled": False,
                    "isPartCancelled": False,
                    "serviceJourney": {
                        "gid": "9015014506100115",
                        "direction": "Masthugget, Påstigning fram",
                        "directionDetails": {
                            "fullDirection": "Masthugget, Påstigning fram",
                            "shortDirection": "Masthugget",
                            "isFrontEntry": True,
                        },
                        "number": "115",
                        "line": {
                            "shortName": "61",
                            "designation": "61",
                            "isWheelchairAccessible": True,
                            "name": "Buss 61",
                            "backgroundColor": "#ffff50",
                            "foregroundColor": "#0061eb",
                            "borderColor": "#ffff50",
                            "isRealtimeJourney": False,
                            "transportMode": "bus",
                            "transportSubMode": "none",
                        },
                    },
                    "notes": [],
                    "plannedDepartureTime": "2025-11-12T14:18:00.0000000+01:00",
                    "plannedArrivalTime": "2025-11-12T14:27:00.0000000+01:00",
                    "plannedDurationInMinutes": 9,
                    "estimatedDepartureTime": "2025-11-12T14:23:00.0000000+01:00",
                    "estimatedArrivalTime": "2025-11-12T14:31:00.0000000+01:00",
                    "estimatedDurationInMinutes": 8,
                    "estimatedOtherwisePlannedArrivalTime": "2025-11-12T14:31:00.0000000+01:00",
                    "estimatedOtherwisePlannedDepartureTime": "2025-11-12T14:23:00.0000000+01:00",
                    "journeyLegIndex": 0,
                },
                {
                    "origin": {
                        "stopPoint": {
                            "gid": "9022014002850001",
                            "name": "Grönsakstorget, Göteborg",
                            "platform": "A",
                            "latitude": 57.7025284,
                            "longitude": 11.96489012,
                            "stopArea": {
                                "gid": "9021014002850000",
                                "name": "Grönsakstorget",
                                "latitude": 57.70249064,
                                "longitude": 11.96443998,
                                "tariffZone1": {
                                    "gid": "9081014200003000",
                                    "name": "Zon A",
                                    "number": 3000,
                                    "shortName": "A",
                                },
                            },
                        },
                        "plannedTime": "2025-11-12T14:35:00.0000000+01:00",
                        "estimatedTime": "2025-11-12T14:34:00.0000000+01:00",
                        "estimatedOtherwisePlannedTime": "2025-11-12T14:34:00.0000000+01:00",
                        "notes": [],
                    },
                    "destination": {
                        "stopPoint": {
                            "gid": "9022014004490004",
                            "name": "Lindholmen, Göteborg",
                            "platform": "D",
                            "latitude": 57.7080502,
                            "longitude": 11.93742673,
                            "stopArea": {
                                "gid": "9021014004490000",
                                "name": "Lindholmen",
                                "latitude": 57.70770985,
                                "longitude": 11.93673345,
                                "tariffZone1": {
                                    "gid": "9081014200003000",
                                    "name": "Zon A",
                                    "number": 3000,
                                    "shortName": "A",
                                },
                            },
                        },
                        "plannedTime": "2025-11-12T14:51:00.0000000+01:00",
                        "estimatedTime": "2025-11-12T14:50:00.0000000+01:00",
                        "estimatedOtherwisePlannedTime": "2025-11-12T14:50:00.0000000+01:00",
                        "notes": [],
                    },
                    "isCancelled": False,
                    "isPartCancelled": False,
                    "serviceJourney": {
                        "gid": "9015014501600144",
                        "direction": "Västra Eriksberg",
                        "directionDetails": {
                            "fullDirection": "Västra Eriksberg",
                            "shortDirection": "Västra Eriksberg",
                        },
                        "number": "144",
                        "line": {
                            "shortName": "16",
                            "designation": "16",
                            "isWheelchairAccessible": True,
                            "name": "Buss 16",
                            "backgroundColor": "#007c4f",
                            "foregroundColor": "#ffff50",
                            "borderColor": "#007c4f",
                            "isRealtimeJourney": False,
                            "transportMode": "bus",
                            "transportSubMode": "none",
                        },
                    },
                    "notes": [],
                    "plannedConnectingTimeInMinutes": 8,
                    "estimatedConnectingTimeInMinutes": 3,
                    "isRiskOfMissingConnection": False,
                    "plannedDepartureTime": "2025-11-12T14:35:00.0000000+01:00",
                    "plannedArrivalTime": "2025-11-12T14:51:00.0000000+01:00",
                    "plannedDurationInMinutes": 16,
                    "estimatedDepartureTime": "2025-11-12T14:34:00.0000000+01:00",
                    "estimatedArrivalTime": "2025-11-12T14:50:00.0000000+01:00",
                    "estimatedDurationInMinutes": 16,
                    "estimatedOtherwisePlannedArrivalTime": "2025-11-12T14:50:00.0000000+01:00",
                    "estimatedOtherwisePlannedDepartureTime": "2025-11-12T14:34:00.0000000+01:00",
                    "journeyLegIndex": 1,
                },
            ],
            "connectionLinks": [],
            "isDeparted": False,
        },
    ],
    "pagination": {"limit": 0, "offset": 0, "size": 0},
    "links": {
        "previous": "journeys?originGid=9021014002230000&destinationGid=9021014004490000&dateTimeRelatesTo=departure&limit=1&transportModes=tram&transportModes=bus&transportModes=ferry&transportModes=train&transportModes=walk&onlyDirectConnections=False&includeNearbyStopAreas=False&useRealTimeMode=False&includeOccupancy=False&bodSearch=False&dateTime=2025-11-12T13%3A17%3A19.0000000%2B00%3A00&paginationReference=M3xPQnxNVMK1MTTCtTkwMTM4wrU5MDEzOMK1OTAxNzHCtTkwMTcxwrUwwrUwwrU4NcK1OTAxMzfCtTHCtTDCtTLCtTDCtTDCtS0yMTQ3NDgzNjQ4wrUxwrUyfFBESMK1N2Y1NmQzOWY4N2VkNjA2ODQwMTU4Njk3ODc0ZmRkYWR8UkTCtTEyMTEyMDI1fFJUwrUxNDE3MTl8VVPCtTB8UlPCtUlOSVQ",
        "next": "journeys?originGid=9021014002230000&destinationGid=9021014004490000&dateTimeRelatesTo=departure&limit=1&transportModes=tram&transportModes=bus&transportModes=ferry&transportModes=train&transportModes=walk&onlyDirectConnections=False&includeNearbyStopAreas=False&useRealTimeMode=False&includeOccupancy=False&bodSearch=False&dateTime=2025-11-12T13%3A17%3A19.0000000%2B00%3A00&paginationReference=M3xPRnxNVMK1MTTCtTkwMTM4wrU5MDEzOMK1OTAxNzHCtTkwMTcxwrUwwrUwwrU4NcK1OTAxMzfCtTHCtTDCtTLCtTDCtTDCtS0yMTQ3NDgzNjQ4wrUxwrUyfFBESMK1N2Y1NmQzOWY4N2VkNjA2ODQwMTU4Njk3ODc0ZmRkYWR8UkTCtTEyMTEyMDI1fFJUwrUxNDE3MTl8VVPCtTB8UlPCtUlOSVQ",
        "current": "journeys?originGid=9021014002230000&destinationGid=9021014004490000&dateTimeRelatesTo=departure&limit=1&transportModes=tram&transportModes=bus&transportModes=ferry&transportModes=train&transportModes=walk&onlyDirectConnections=False&includeNearbyStopAreas=False&useRealTimeMode=False&includeOccupancy=False&bodSearch=False&dateTime=2025-11-12T13%3A17%3A19.0000000%2B00%3A00",
    },
}
