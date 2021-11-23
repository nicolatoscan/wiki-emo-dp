#!/usr/bin/env python3
"""A simple command-line utility to process streams of compressed files."""

# Inspired by mediawiki-utilities by halfak et al.
# See:
# https://github.com/mediawiki-utilities/python-mediawiki-utilities/

import sys
import csv
import argparse
import pathlib

from .functions import open_file, file


########## helpers
def common_args(prog, description):
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        prog=prog,
        description=description,
    )
    parser.add_argument(
        'files',
        metavar='FILE',
        type=pathlib.Path,
        nargs='+',
        help='File to decompress.',
    )
    parser.add_argument(
        '--algorithm', '-a',
        dest='algo',
        choices=['gz', 'bz2', '7z', 'lzma'],
        help="Force decompression algorithm instead of using file extension.",
    )
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help="Don't write any output",
    )
    parser.add_argument(
        '--csv',
        action='store_true',
        help="Read file with CSV reader",
    )

    parsed_args = parser.parse_args()

    return parsed_args
########## end: helpers

########## grep
def decompressgrep():

    args = common_args(prog='decompressgrep',
                       description="search possibly compressed files for a "
                                    "regular expression"
                       )

    # FIXME: to implement
    raise NotImplementedError("This function has not been implemented yet.")
########## end: grep


########## more and less
def decompressless():

    args = common_args(prog='decompressless',
                       description="file perusal filter for viewing of "
                                   "compressed text"
                       )

    # FIXME: to implement
    raise NotImplementedError("This function has not been implemented yet.")


def decompressmore():

    args = common_args(prog='decompressmore',
                       description="file perusal filter for viewing of "
                                   "compressed text"
                       )

    # FIXME: to implement
    raise NotImplementedError("This function has not been implemented yet.")

########## end: more and less

########## diff/cmp
def decompressdiff():

    args = common_args(prog='decompressdiff, decompresscmp',
                       description="compare compressed files"
                       )

    # FIXME: to implement
    raise NotImplementedError("This function has not been implemented yet.")

# cmp is an alias for diff
decompresscmp = decompressdiff

########## end: diff/cmp


########## cat
def main():
    """Main function."""
    args = common_args(prog='decompresscat',
                       description="decompresses files to stdout"
                       )

    for infile in args.files:

        csv_file = open_file(str(infile), algo=args.algo)

        if args.csv:
            reader = csv.reader(csv_file)
            end = '\n'
            lines = ('\t'.join(row) for row in reader)

        else:
            reader = csv_file
            end = ''
            lines = reader

        try:
            for line in lines:
                if not args.quiet:
                    print(line, end=end)
        except BrokenPipeError:
            pass

        exit(0)

# main is cat
decompresscat = main

########## end: cat


if __name__ == '__main__':
    main()
