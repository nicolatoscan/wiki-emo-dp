import argparse
from pathlib import Path

def getFiles():
    argParser = argparse.ArgumentParser()
    argParser.add_argument(
        'files',
        metavar='FILE',
        type=Path,
        nargs='+',
        help='Path to files',
    )

    args, _ = argParser.parse_known_args()
    return args.files
