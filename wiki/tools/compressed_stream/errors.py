"""
Error classes for convenience.
"""


class FileTypeError(Exception):
    """
    Thrown when an CSV compressed file is not of an expected type.
    """
    pass


class FileNotFound(Exception):
    """
    Thrown when the input file is not found.
    """
    pass
