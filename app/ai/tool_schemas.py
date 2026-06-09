from typing import Any

from app.models.domain import UserMode

_ABOUT_FALSA = {
    "type": "function",
    "function": {
        "name": "about_falsa",
        "description": (
            "Retrieve official FALSA company, FAQ, policy, or pricing information."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The customer's question about FALSA.",
                },
                "language": {
                    "type": "string",
                    "enum": ["ar", "en"],
                    "description": "Customer language for the result.",
                },
            },
            "required": ["query", "language"],
            "additionalProperties": False,
        },
    },
}

_SEARCH_TRIPS = {
    "type": "function",
    "function": {
        "name": "search_trips",
        "description": (
            "Search active car or bus trips. "
            "Use when the customer asks for travel options."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "departure": {
                    "type": "string",
                    "description": "Departure city or area in Arabic.",
                },
                "destination": {
                    "type": "string",
                    "description": "Destination city or area in Arabic.",
                },
                "travel_datetime": {
                    "type": "string",
                    "description": (
                        "Optional requested date/time in ISO format. Times are interpreted "
                        "in Asia/Aden and normalized to morning, noon, or night."
                    ),
                },
                "travel_date": {
                    "type": "string",
                    "description": (
                        "Optional requested trip date as YYYY-MM-DD in Asia/Aden. Use English digits."
                    ),
                },
                "travel_time": {
                    "type": "string",
                    "enum": ["صباح", "ظهر", "ليل"],
                    "description": (
                        "Optional requested trip time bucket in Arabic. If the customer also provides "
                        "an exact time, provide the matching Arabic bucket: صباح before 12:00, ظهر from 12:00-17:59, ليل from 18:00."
                    ),
                },
                "travel_time_exact": {
                    "type": "string",
                    "description": (
                        "Optional exact requested time as HH:MM in Asia/Aden, for example "
                        "06:00. Use English digits and colon formatting. Also provide the corresponding Arabic travel_time bucket when possible."
                    ),
                },
                "seats": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "Optional number of seats requested.",
                },
                "vehicle_type": {
                    "type": "string",
                    "description": "Optional car type in Arabic, for example سيارة or باص.",
                },
                "vector_query_text": {
                    "type": "string",
                    "description": (
                        "Natural-language semantic search text containing the route, date, "
                        "time, seats, and vehicle preferences extracted from the customer."
                    ),
                },
            },
            "required": ["departure", "destination", "vector_query_text"],
            "additionalProperties": False,
        },
    },
}

_CREATE_BOOKING_LEAD = {
    "type": "function",
    "function": {
        "name": "create_booking_lead",
        "description": (
            "Create a pending booking lead and notify the driver. "
            "This does not reserve seats or confirm payment."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "trip_id": {"type": "string", "description": "Selected trip ID."},
                "requested_seats": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "Number of seats requested by the customer.",
                },
                "notes": {
                    "type": "string",
                    "description": "Optional customer notes or pickup details.",
                },
            },
            "required": ["trip_id", "requested_seats"],
            "additionalProperties": False,
        },
    },
}

_CREATE_DRIVER_ACCOUNT = {
    "type": "function",
    "function": {
        "name": "create_driver_account",
        "description": (
            "Register the current WhatsApp sender as a FALSA driver. "
            "Phone number is taken automatically from the chat session."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Driver full legal name.",
                },
            },
            "required": ["name"],
            "additionalProperties": False,
        },
    },
}

_CHECK_DRIVER_INFO = {
    "type": "function",
    "function": {
        "name": "check_driver_info",
        "description": (
            "Retrieve the registered driver's account details, registered vehicles, and active trip summary. "
            "Use when a driver asks about their own profile or vehicle status."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        },
    },
}

_CHECK_DRIVER_TRIPS = {
    "type": "function",
    "function": {
        "name": "check_driver_trips",
        "description": (
            "List all upcoming active trips for the registered driver. "
            "A trip is considered upcoming if it has status active and has not yet departed."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        },
    },
}

_ADD_DRIVER_CAR = {
    "type": "function",
    "function": {
        "name": "add_driver_car",
        "description": (
            "Register a new vehicle for the current WhatsApp driver. "
            "Only the car name is required; plate number and seat count are optional."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Vehicle name or type in Arabic.",
                },
                "plate_number": {
                    "type": "string",
                    "description": "Optional vehicle plate number.",
                },
                "seat_count": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "Optional number of seats in the vehicle.",
                },
            },
            "required": ["name"],
            "additionalProperties": False,
        },
    },
}

_ADD_TRIP_BY_DRIVER = {
    "type": "function",
    "function": {
        "name": "add_trip_by_driver",
        "description": (
            "Create an active trip for the registered driver on this WhatsApp number. "
            "Phone is taken from the chat session. Optional car, seat, and price fields "
            "default from the driver's most recent trip or sole registered vehicle."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "departure": {
                    "type": "string",
                    "description": "Departure city or area in Arabic.",
                },
                "destination": {
                    "type": "string",
                    "description": "Destination city or area in Arabic.",
                },
                "departure_date": {
                    "type": "string",
                    "description": "Trip date as YYYY-MM-DD in Asia/Aden.",
                },
                "departure_time": {
                    "type": "string",
                    "description": (
                        "Trip time bucket: morning, noon, night, or Arabic "
                        "صباح / ظهر / ليل."
                    ),
                },
                "vehicle_type": {
                    "type": "string",
                    "description": (
                        "Optional vehicle name or type in Arabic, for example "
                        "سيارة or باص. Matched against the driver's registered cars."
                    ),
                },
                "available_seats": {
                    "type": "integer",
                    "minimum": 0,
                    "description": "Optional seats available for booking.",
                },
                "total_seats": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "Optional total vehicle seats for this trip.",
                },
                "price": {
                    "type": "number",
                    "minimum": 0,
                    "description": "Optional trip price.",
                },
            },
            "required": ["departure", "destination", "departure_date", "departure_time"],
            "additionalProperties": False,
        },
    },
}

_SWITCH_TO_DRIVER = {
    "type": "function",
    "function": {
        "name": "switch_to_driver",
        "description": (
            "Switch this sender to driver mode. "
            "Requires an existing driver account; use create_driver_account first if needed."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        },
    },
}

_SWITCH_TO_PASSENGER = {
    "type": "function",
    "function": {
        "name": "switch_to_passenger",
        "description": (
            "Switch this sender to passenger mode so they can search and book trips."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Optional passenger display name.",
                },
            },
            "required": [],
            "additionalProperties": False,
        },
    },
}

_TOOL_SCHEMAS: dict[str, dict[str, Any]] = {
    "about_falsa": _ABOUT_FALSA,
    "search_trips": _SEARCH_TRIPS,
    "create_booking_lead": _CREATE_BOOKING_LEAD,
    "create_driver_account": _CREATE_DRIVER_ACCOUNT,
    "check_driver_info": _CHECK_DRIVER_INFO,
    "check_driver_trips": _CHECK_DRIVER_TRIPS,
    "add_driver_car": _ADD_DRIVER_CAR,
    "add_trip_by_driver": _ADD_TRIP_BY_DRIVER,
    "switch_to_driver": _SWITCH_TO_DRIVER,
    "switch_to_passenger": _SWITCH_TO_PASSENGER,
}

_TOOLS_BY_MODE: dict[UserMode, list[str]] = {
    "new_user": [
        "about_falsa",
        "create_driver_account",
        "switch_to_driver",
        "switch_to_passenger",
    ],
    "driver": [
        "about_falsa",
        "check_driver_info",
        "check_driver_trips",
        "add_driver_car",
        "add_trip_by_driver",
        "switch_to_passenger",
    ],
    "passenger": [
        "about_falsa",
        "search_trips",
        "create_booking_lead",
        "create_driver_account",
        "switch_to_driver",
    ],
}


def get_tool_schemas(user_mode: UserMode = "new_user") -> list[dict[str, Any]]:
    return [_TOOL_SCHEMAS[name] for name in _TOOLS_BY_MODE[user_mode]]


def get_all_tool_schemas() -> list[dict[str, Any]]:
    return list(_TOOL_SCHEMAS.values())
