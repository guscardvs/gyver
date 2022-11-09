from datetime import datetime


def now() -> datetime:
    """returns a datetime aware date"""
    return datetime.now().astimezone()
