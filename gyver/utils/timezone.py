from datetime import date, timezone, tzinfo
from datetime import datetime


def now(tz: tzinfo = timezone.utc) -> datetime:
    """
    Get the current aware datetime.
    
    :param tz: The timezone for the datetime (default is UTC).
    :return: The current datetime in the specified timezone.
    """
    return datetime.now(tz)

def today(tz: tzinfo = timezone.utc) -> date:
    """
    Get today's aware date.
    
    :param tz: The timezone for the date (default is UTC).
    :return: Today's date in the specified timezone.
    """
    return now(tz).date()

def make_now_factory(tz: tzinfo):
    """
    Create a function to get the current aware datetime with a specific timezone.
    
    :param tz: The timezone for the datetime factory.
    :return: A function that returns the current datetime in the specified timezone.
    """
    def _now():
        return now(tz)
    return _now