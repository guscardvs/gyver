def boolean_cast(string: str):
    """
    The boolean_cast function converts a string to its boolean equivalent.
    1 and true(case-insensitive) are considered True, everything else, False.

    :param string: str: Check if the string is true or false
    :return: A boolean value based on the string it receives
    """
    return {
        "true": True,
        "false": False,
        "1": True,
        "0": False,
        "": False,
    }.get(string.lower(), False)
