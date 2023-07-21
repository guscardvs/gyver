from datetime import datetime


def now() -> datetime:
    """Returns a datetime aware date"""
    return datetime.now().astimezone()
