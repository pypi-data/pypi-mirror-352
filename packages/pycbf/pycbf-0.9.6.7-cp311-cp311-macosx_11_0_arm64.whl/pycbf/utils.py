from typing import Union

import pycbf


def cbf2str(string: Union[str, bytes]) -> str:
    """
    Convert whatever the native string return type of pycbf is, to str.

    To help compatibility moving away from pycbf.SWIG_PYTHON_STRICT_BYTE_CHAR -
    if bytes is used strictly, then although we can accept both - return
    types will still be bytes, so we want to be able to convert them.

    Args:
        string: The string-ish object returned from pycbf
    """

    if not isinstance(string, (str, bytes)):
        raise ValueError(f"Unrecognised pycbf string type: {type(string)}")

    if pycbf.HAS_SWIG_PYTHON_STRICT_BYTE_CHAR:
        if isinstance(string, bytes):
            return string.decode()
        return string

    if isinstance(string, bytes):
        # We got passed a bytes!?!? this is probably an actual data object
        raise ValueError("Cannot convert bytes objects - str should be native?")

    return string
