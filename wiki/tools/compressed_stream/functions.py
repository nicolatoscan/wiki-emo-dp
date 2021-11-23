"""
Utility functions to process compressed CSV files
"""

# Based on funxtions.py from mediawiki-utilities by halfak et al.
# See:
# https://github.com/mediawiki-utilities/python-mediawiki-utilities/\
#   commit/42362c3be270b5533dfed3c3850ef7dc6208a54f

import os
import re
import io
import codecs
import subprocess

from .errors import FileTypeError, FileNotFound

EXTENSIONS = {
    'gz': ["zcat"],
    'bz2': ["bzcat"],
    '7z': ["7z", "e", "-so"],
    'lzma': ["lzcat"]
}
"""
A map from file extension to the command to run to extract the data to standard
out.
"""

EXT_RE = re.compile(r'\.([^\.]+)$')
"""
A regular expression for extracting the final extension of a file.
"""


def file(path_or_f: str):
    """
    Verifies that a file exists at a given path and that the file has a
    known extension type.

    :Parameters:
        path : `str`
            the path to a dump file

    """
    if hasattr(path_or_f, "readline"):
        return path_or_f
    else:
        path = path_or_f

    path = os.path.expanduser(path)
    if not os.path.isfile(path):
        raise FileNotFound("Can't find file {}".format(path))

    match = EXT_RE.search(path)
    if match is None:
        raise FileTypeError("No extension found for {}.".format(path))
    else:
        return path


def open_file(path_or_f: str, algo=None, encoding='utf-8'):
    """
    Turns a path to a dump file into a file-like object of (decompressed)
    XML data.

    :Parameters:
        path : `str`
            the path to the dump file to read
    """
    file(path_or_f)

    if hasattr(path_or_f, "read"):
        return path_or_f
    else:
        path = path_or_f

    if algo is None:
        match = EXT_RE.search(path)
        ext = match.groups()[0]
        algo = ext

    p = subprocess.Popen(
        EXTENSIONS.get(algo, ['cat']) + [path],
        stdout=subprocess.PIPE,
        stderr=open(os.devnull, "w")
    )

    return io.TextIOWrapper(p.stdout, 'utf-8')
