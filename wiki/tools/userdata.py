from pathlib import Path
from typing import Dict, Iterable, List
from dataclasses import dataclass
from tqdm import tqdm

@dataclass
class UserData:
    id: int
    name: str
    gender: int
    roles: List[int]

rolesMap = { r:i for i, r in enumerate(['bureaucrat', 'reviewer', 'founder', 'checkuser', 'import', 'templateeditor', 'abusefilter', 'confirmed', 'extendedmover', 'copyviobot', 'rollbacker', 'user', 'oversight', 'researcher', 'autoconfirmed', 'patroller', 'sysop', 'accountcreator', 'extendedconfirmed', 'abusefilter-helper', 'autoreviewer', '*', 'eventcoordinator', 'ipblock-exempt', 'massmessage-sender', 'interface-admin', 'filemover', 'flow-bot', 'bot']) }

def parseUser(line: str):
    info = line.strip('\n').split('\t')
    if len(info) > 5:
        id = int(info[0])
        roles = [ rolesMap[r] for r in info[5].split(',') ]
        return UserData(
            id,
            info[1],
            0 if info[2] == 'female' else (1 if info[2] == 'male' else -1),
            roles
        )
    return None


def loadUserDataLive(path: Path) -> Iterable[UserData]:
    with open(path) as f:
        for l in tqdm(f):
            u = parseUser(l)
            if u is not None:
                yield u

def loadUserData(path: Path) -> Dict[int, UserData]:
    with open(path) as f:
        data = { u.id: u for u in [ parseUser(l) for l in tqdm(f) ] if u is not None }
        return data