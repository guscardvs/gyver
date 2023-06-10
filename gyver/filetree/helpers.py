from gyver.exc import InvalidPath


def python_filename(filename: str, private: bool = False, dunder: bool = False):
    if private and dunder:
        raise InvalidPath("cannot have both private and dunder file")
    elif private:
        filename = f"_{filename}"
    elif dunder:
        filename = f"__{filename}__"
    return f"{filename}.py"
