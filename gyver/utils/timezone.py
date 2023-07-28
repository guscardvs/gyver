from datetime import date, datetime
from typing import Optional
from zoneinfo import ZoneInfo


def now(tz: Optional[ZoneInfo] = None) -> datetime:
    """Returns a datetime aware date"""
    val = datetime.now(tz)
    if tz is None:
        val = val.astimezone()
    return val


def today(tz: Optional[ZoneInfo] = None) -> date:
    return now(tz).date()
