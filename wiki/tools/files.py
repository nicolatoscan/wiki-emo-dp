import gzip
from pathlib import Path
import json
from typing import Callable, List

def readFileSections(files: List[Path], callback: Callable[[int, List[dict]], None]) -> None:
    for file in files:
        with gzip.open(file, 'rt') as f:
            currId: None | int = None
            currData = []

            for l in f:
                [id, data] = l.split('\t')
                id = int(id)

                if id != currId:
                    if currId is not None:
                        callback(currId, currData)
                    currId = id
                    currData = []

                currData.append(json.loads(data))

            if currId is not None and len(currData) > 0:
                callback(currId, currData)


