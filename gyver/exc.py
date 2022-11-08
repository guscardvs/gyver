class GyverError(Exception):
    """Base exception for all gyver exceptions"""


class InvalidCast(GyverError):
    """Exception raised for config when
    cast callable raises an error"""


class MissingName(GyverError, KeyError):
    """Exception raised for config when
    name is not found in given environ"""
