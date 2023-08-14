from datetime import date, timezone, tzinfo
from datetime import datetime
from typing import Callable


def now(tz: tzinfo = timezone.utc) -> datetime:
    """
    Get the current aware datetime.
    
    Args:
        tz (tzinfo): The timezone for the datetime (default is UTC).
    
    Returns:
        datetime: The current datetime in the specified timezone.
    """
    return datetime.now(tz)

def today(tz: tzinfo = timezone.utc) -> date:
    """
    Get today's aware date.
    
    Args:
        tz (tzinfo): The timezone for the date (default is UTC).
    
    Returns:
        date: Today's date in the specified timezone.
    """
    return now(tz).date()

def make_now_factory(tz: tzinfo) -> Callable[[], datetime]:
    """
    Create a function to get the current aware datetime with a specific timezone.
    
    Args:
        tz (tzinfo): The timezone for the datetime factory.
    
    Returns:
        Callable[[], datetime]: A function that returns the current datetime in the specified timezone.
    """
    def _now():
        return now(tz)
    return _now