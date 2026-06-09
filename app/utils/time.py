from datetime import datetime
from zoneinfo import ZoneInfo


def now_in_timezone(timezone_name: str) -> datetime:
    return datetime.now(tz=ZoneInfo(timezone_name))
