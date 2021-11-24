from typing import Counter, List
from tools import arg
from tools import files
from datetime import datetime, timedelta
import numpy as np
from itertools import groupby

def analyze(id: int, data: List[dict]) -> None:
    """
    Id
    Nome
    Numero edit
    percentuale type actions
    percentuale namespace

    Gender
    Role

    First edit date
    Last edit date
    Avg time between edits

    perc emotions
    perc emotion last 2 month
    perc emotion last 1 month
    perc emotion last 10 edits
    perc emotion last 5 edits
    perc emotion last 1 edits
    """

    revs = []
    for k,vals in groupby(data,key=lambda x:x['id'].split('.')[0]):
        vals = [v for v in vals]
        emotions = np.sum([ [ int(e) for e in v['emotions'].split(',')[:-1] ] for v in vals ], axis=0)
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

    name =  revs[0]['user']['text'] if 'text' in revs[0]['user'] else revs[0]['user']['ip']
    nEdit = len(revs)
    firstEditDate = revs[0]['timestamp']
    lastEditDate = revs[-1]['timestamp']
    timeDiff = np.diff([ d['timestamp'] for d in revs ])
    avgDiffTime = np.mean(timeDiff)


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
    for n in [10000, 365, 180, 90, 60, 30, 7]:
        d = lastEditDate - timedelta(days=n)
        lastRev = [ r for r in lastRev if r['timestamp'] > d ]
        nEmo = np.sum( [ r['nEmotions'] for r in lastRev ])
        avgEm = np.average( [ r['emotionsNorm'] for r in lastRev ], axis=0)
        
        perEmotionsLastDays.append( ( n, nEmo, avgEm ) )

filesList = arg.getFiles()
files.readFileSections(filesList, analyze)