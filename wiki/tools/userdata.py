from pathlib import Path
from typing import Dict, List
from dataclasses import dataclass
from tqdm import tqdm

@dataclass
class UserData:
    id: int
    name: str
    gender: int
    roles: List[str]

def loadUserData(path: Path) -> Dict[int, UserData]:
    data = {}
    with open(path) as f:
        for l in tqdm(f):
            info = l.strip('\n').split('\t')
            id = int(info[0])
            data[id] = UserData(
                id,
                info[1],
                0 if info[2] == 'female' else (1 if info[2] == 'male' else -1),
                info[5].split(',')
            )

    return data