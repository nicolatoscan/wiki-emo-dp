# %% import
from pathlib import Path
from typing import Counter, List
from tools import files, userdata
from datetime import datetime, timedelta
import numpy as np
from itertools import groupby
import json
# import pymongo

# %% load user data
typeAction = 'user'
lang = 'it'
uData = userdata.loadUserData(Path(f'../dataset/genders/genders-{lang}.tsv'))
print(f'Loaded {lang}')

# %% setup mongo
# dbColl = pymongo.MongoClient("mongodb://localhost:27017/")["wiki"][f"{typeAction}-{lang}"]

# %%
savingFile = open(f'{typeAction}-{lang}.csv', 'w')
savingFileJson = open(f'{typeAction}-{lang}.json', 'w')

def analyze(id: int, data: List[dict]) -> None:
    gender = -1
    roles = ['*']
    name = 'NOT FOUND'

    if id in uData:
        u = uData[id]
        name = u.name
        gender = u.gender
        roles = u.roles
    
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
            "user": vals[0]['user'],
            "timestamp": datetime.fromisoformat(vals[0]['timestamp'].replace('Z', '+00:00')),
        })

    # name =  revs[0]['user']['text'] if 'text' in revs[0]['user'] else revs[0]['user']['ip']
    nEdit = len(revs)
    firstEditDate = revs[0]['timestamp']
    lastEditDate = revs[-1]['timestamp']
    timeDiff = np.diff([ d['timestamp'] for d in revs ])
    avgDiffTime = None if len(timeDiff) == 0 else np.mean(timeDiff).total_seconds()

    # % of types
    nTypeEdits = Counter([t for r in revs for t in r['type']])
    perTypeEdits = [
        nTypeEdits['CREATION'] / nEdit,
        nTypeEdits['ADDITION'] / nEdit,
        nTypeEdits['MODIFICATION'] / nEdit,
        nTypeEdits['DELETION'] / nEdit,
        nTypeEdits['RESTORATION'] / nEdit
    ]

    # % of namespaces
    nNamespaces = Counter([d['pageNamespace'] for d in revs])
    perNamespaces = [
        nNamespaces[1] / nEdit,
        nNamespaces[2] / nEdit,
        nNamespaces[3] / nEdit,
        nNamespaces[5] / nEdit,
        nNamespaces[7] / nEdit,
        nNamespaces[9] / nEdit,
        nNamespaces[11] / nEdit,
        nNamespaces[13] / nEdit,
        nNamespaces[15] / nEdit,
        nNamespaces[101] / nEdit,
        nNamespaces[119] / nEdit,
        nNamespaces[711] / nEdit,
        nNamespaces[829] / nEdit,
    ]


    lastRev = revs
    perEmotionsLastDays = []
    for n in [ 10000, 365, 180, 90, 60, 30, 7 ]:
        d = lastEditDate - timedelta(days=n)
        lastRev = [ r for r in lastRev if r['timestamp'] > d ]
        nEmo = np.sum( [ r['nEmotions'] for r in lastRev ])
        avgEm = np.average( [ r['emotionsNorm'] for r in lastRev ], axis=0)

        perEmotionsLastDays.append( ( n, nEmo, avgEm ) )

    lineParams = [
        id,
        gender,
        ','.join(roles),
        name,
        nEdit,
        firstEditDate,
        lastEditDate,
        avgDiffTime,
        ','.join([ str(x) for x in perTypeEdits ]),
        ','.join([ str(x) for x in perNamespaces ]),
    ] + [ f"{x[0]}|{x[1]}|{','.join( [ str(i) for i in list(x[2]) ] )}"  for x in perEmotionsLastDays]
    savingFile.write('\t'.join( [str(x) for x in lineParams ] ) + '\n')

    d = {
        "id": id,
        "gender": gender,
        "roles": roles,
        "name": name,
        "nEdit": nEdit,
        "firstEditDate": firstEditDate.isoformat(),
        "lastEditDate": lastEditDate.isoformat(),
        "avgDiffTime": avgDiffTime,
        "editTypes": perTypeEdits,
        "namespaces": perNamespaces,
        "emotionsLastDays": [ { "n": int(x[0]), "nEmo": int(x[1]), "avg": x[2].tolist() } for x in perEmotionsLastDays ]
    }

    savingFileJson.write(f'{json.dumps(d)}\n')


filesList = files.getFileList(f'../dataset/min/{typeAction}/{lang}', '*.gz')
files.readFileSections(filesList, analyze)

savingFile.close()
savingFileJson.close()
print("Done")
# %%
