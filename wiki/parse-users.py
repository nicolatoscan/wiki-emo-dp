# %% import
from pathlib import Path
from typing import Counter, List, Union
from tools import files, userdata
from datetime import datetime, timedelta
import numpy as np
from itertools import groupby
import json
# import pymongo

# %% settings
typeAction = 'user'
lang = 'en'

namespaces = [ 1,2,3,5,7,9,11,13,15,101,119,711,829 ]
typesEdit = ['CREATION', 'ADDITION', 'MODIFICATION', 'DELETION', 'RESTORATION']
lastDays = [ 10000, 365, 180, 90, 60, 30, 7 ]

rolesNames = [ '*', 'accountcreator', 'autoconfirmed', 'autopatrolled', 'bot', 'botadmin', 'bureaucrat', 'checkuser', 'confirmed', 'flow-bot', 'interface-admin', 'ipblock-exempt', 'mover', 'rollbacker', 'sysop', 'user' ]
emotions = ["TOT", "POS", "NEG", "E0", "E1", "E2", "E3", "E4", "E5", "E6", "E7"]
headers = [
    "id", "name", "ip", "nEdit", "firstEditDate", "lastEditDate", "avgDiffTime",
    "female", "male",
    *rolesNames,
    *typesEdit,
    *[ f"namespace {n}" for n in namespaces ],
    *[ f"{'' if n == 10000 else n}{e}" for n in lastDays for e in emotions ]
]

# %% load user data
filePath = Path(f'../dataset/genders/genders-{lang}.tsv')
# uData = userdata.loadUserData(filePath)
# print(f'Loaded {lang}')

uData = userdata.loadUserDataLive(filePath)

# %% start
savingFile = open(f'{typeAction}-{lang}.csv', 'w')
# savingFileJson = open(f'{typeAction}-{lang}.json', 'w')

savingFile.write(f'{",".join(headers)}\n')

u: userdata.UserData = next(uData)
nomatch = 0
def analyze(id: int, data: List[dict]) -> bool:
    global u, nomatch
    gender = -1
    roles = ['*']
    name = None

    if 'user' in data[0] and 'text' in data[0]['user']:
        while u is None or u.id < id:
            u = next(uData)
        if u.id == id:
            gender = u.gender
            roles = u.roles
        else:
            nomatch += 1
            print(f"No match for {data[0]['user']['text']}")
    # if id in uData:
    #     u = uData[id]
    #     # name = u.name
    #     gender = u.gender
    #     roles = u.roles


    
    revs = []
    for k,vals in groupby(data,key=lambda x:x['id'].split('.')[0]):
        vals = [v for v in vals]
        filtredVals = [v for v in vals if v['type'][0] == 'A' or v['type'][0] == 'C' ]
        emotions = np.sum(
            [ 
                [ int(e) for e in v['emotions'].split(',')[:-1] ]
                for v in filtredVals
            ],
            axis=0
        ) if len(filtredVals) > 0 else np.zeros(11)

        nEmotions = emotions[0]
        emotions = emotions[1:]

        revs.append({
            "id": k,
            "type": [ v['type'] for v in vals ],
            "nEmotions": nEmotions,
            "emotions": emotions,
            "emotionsNorm": [0.0] * len(emotions) if nEmotions == 0 else emotions / nEmotions,
            "pageId": vals[0]['pageId'],
            "pageTitle": vals[0]['pageTitle'],
            "pageNamespace": vals[0]['pageNamespace'],
            "user": vals[0]['user'] if vals[0]['user'] is not None else {},
            "timestamp": datetime.fromisoformat(vals[0]['timestamp'].replace('Z', '+00:00')),
        })

    nEdit = len(revs)
    if nEdit == 0:
        return True
    if name == None and 'text' in revs[0]['user']:
        name =  revs[0]['user']['text']
    ip = revs[0]['user']['ip'] if 'ip' in revs[0]['user'] else None
    firstEditDate = revs[0]['timestamp']
    lastEditDate = revs[-1]['timestamp']
    timeDiff = np.diff([ d['timestamp'] for d in revs ])
    avgDiffTime = None if len(timeDiff) == 0 else np.mean(timeDiff).total_seconds()

    # % of types
    nTypeEdits = Counter([t for r in revs for t in r['type']])
    perTypeEdits = [ nTypeEdits[t] / nEdit for t in typesEdit ]

    # % of namespaces
    nNamespaces = Counter([d['pageNamespace'] for d in revs])
    perNamespaces = [ nNamespaces[n] / nEdit for n in namespaces ]


    lastRev = revs
    perEmotionsLastDays = []
    for n in lastDays:
        d = lastEditDate - timedelta(days=n)
        lastRev = [ r for r in lastRev if r['timestamp'] > d ]
        nEmo = np.sum( [ r['nEmotions'] for r in lastRev ])
        avgEm = np.average( [ r['emotionsNorm'] for r in lastRev ], axis=0)
        perEmotionsLastDays.append( ( n, nEmo, avgEm ) )

    # lineParams = [
    #     id,
    #     gender,
    #     ','.join(roles),
    #     name,
    #     nEdit,
    #     firstEditDate,
    #     lastEditDate,
    #     avgDiffTime,
    #     ','.join([ str(x) for x in perTypeEdits ]),
    #     ','.join([ str(x) for x in perNamespaces ]),
    # ] + [ f"{x[0]}|{x[1]}|{','.join( [ str(i) for i in list(x[2]) ] )}"  for x in perEmotionsLastDays]
    # savingFile.write('\t'.join( [str(x) for x in lineParams ] ) + '\n')

    # d = {
    #     "id": id,
    #     "gender": gender,
    #     "roles": roles,
    #     "name": name,
    #     "nEdit": nEdit,
    #     "firstEditDate": firstEditDate.isoformat(),
    #     "lastEditDate": lastEditDate.isoformat(),
    #     "avgDiffTime": avgDiffTime,
    #     "editTypes": perTypeEdits,
    #     "namespaces": perNamespaces,
    #     "emotionsLastDays": [ { "n": int(x[0]), "nEmo": int(x[1]), "avg": x[2].tolist() } for x in perEmotionsLastDays ]
    # }
    # savingFileJson.write(f'{json.dumps(d)}\n')

    emlastD = [ [ x[1], *x[2] ] for x in perEmotionsLastDays ]
    pdList = [
        id, f'"{name}"', ip, nEdit,
        firstEditDate.replace(tzinfo=None).isoformat(), lastEditDate.replace(tzinfo=None).isoformat(),
        avgDiffTime,
        1 if gender == 0 else 0,
        1 if gender == 1 else 0,
        *[ 1 if r in roles else 0 for r in rolesNames ],
        *perTypeEdits, *perNamespaces,
        *[ x for l in emlastD for x in l ],
    ]
    savingFile.write(f"{','.join([ str(x) for x in pdList ])}\n")

    return True



filesList = files.getFileList(f'../dataset/min/{typeAction}/{lang}', '*.gz')
files.readFileSections(filesList, analyze)

savingFile.close()
# savingFileJson.close()
print("Done")
# %%
