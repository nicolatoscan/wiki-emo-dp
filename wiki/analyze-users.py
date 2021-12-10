# %%
from tqdm import tqdm
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from enum import Enum
from scipy import stats

# %%
lang = 'it'
emotions = ["TOT", "POS", "NEG", "E0", "E1", "E2", "E3", "E4", "E5", "E6", "E7"]
lastDays = [ 10000, 365, 180, 90, 60, 30, 7 ]
colsEmo = [ f"{'' if n == 10000 else n}{e}" for n in lastDays for e in emotions]
class Emotions(Enum):
    TOT = 0
    POS = 1
    NEG = 2
    ANGER = 3
    ANTICIPATION = 4
    DISGUST = 5
    FEAR = 6
    JOY = 7
    SADNESS = 8
    SURPRISE = 9
    TRUST = 10
    def __int__(self):
        return self.value


def loadFile(file: str) -> pd.DataFrame:
    df = pd.read_csv(file)
    # df = pd.read_csv(f'../dataset/df/{typeAction}-{lang}.csv')
    df['firstEditDate'] = df['firstEditDate'].apply(lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M:%S').timestamp())
    df['lastEditDate'] = df['lastEditDate'].apply(lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M:%S').timestamp())
    df['avgDiffTime'] = df['lastEditDate'] - df['firstEditDate']
    df = df.loc[(df['bot'] == 0) & (df['id'] > 0) & (df['ip'] == "None")]
    return df

def getLangDf(lang: str) -> pd.DataFrame:
    print(f"Loading {lang}")
    dfUser = loadFile(f'../dataset/df/user-{lang}.csv')
    dfReply = loadFile(f'../dataset/df/reply-{lang}.csv')
    dfReply.rename(columns={
        "nEdit": "nReply",
        **{ ce:f"R{ce}" for ce in colsEmo }
    }, inplace=True)
    dfReply.drop(columns=[
            'name', 'ip', 'firstEditDate', 'lastEditDate', 'avgDiffTime',
            'female', 'male', '*', 'accountcreator', 'autoconfirmed',
            'autopatrolled', 'bot', 'botadmin', 'bureaucrat', 'checkuser',
            'confirmed', 'flow-bot', 'interface-admin', 'ipblock-exempt',
            'mover', 'rollbacker', 'sysop', 'user',
            'CREATION', 'ADDITION', 'MODIFICATION', 'DELETION', 'RESTORATION',
            'namespace 1', 'namespace 2', 'namespace 3', 'namespace 5', 'namespace 7', 'namespace 9', 'namespace 11', 'namespace 13', 'namespace 15', 'namespace 101', 'namespace 119', 'namespace 711', 'namespace 829'
        ], inplace=True)
    df = pd.merge(dfUser, dfReply, on='id')
    df['lang'] = lang
    return df

# %% load file
df = pd.concat([getLangDf(lang) for lang in ['it', 'es']])

# %% some data
lastDate = int(df['lastEditDate'].max())
df['active'] = df['lastEditDate'] > (lastDate - 3600*24*180)
df['agespan'] = df['lastEditDate'] - df['firstEditDate']

# %% negative received for less edits
editThreasholds = [1, 3, 5, 10, 30, 50, 100]

rNegLess = []
rNegMore = []
rPosLess = []
rPosMore = []

for N in editThreasholds:
    lessThanN = df.loc[(df['nEdit'] <= N) & (df['active'] == False)]
    moreThanN = df.loc[df['nEdit'] >  N]

    rNegLess.append(lessThanN['RNEG'].mean())
    rNegMore.append(moreThanN['RNEG'].mean())
    rPosLess.append(lessThanN['RPOS'].mean())
    rPosMore.append(moreThanN['RPOS'].mean())

# %% plot
x = np.arange(len(editThreasholds))
width = 0.35
fig, ax = plt.subplots()
rects1 = ax.bar(x - width/2, rNegLess, width, label='Less than N edits')
rects2 = ax.bar(x + width/2, rNegMore, width, label='More than N edits')
# Add some text for labels, title and custom x-axis tick labels, etc.
ax.set_ylabel('Number of edits')
# ax.set_title('Scores by group and gender')
ax.set_xticks(x)
ax.set_xticklabels(editThreasholds)
ax.legend()

# %% norm
print(df.loc[df['male'] == 1]['POS'].mean())
print(df.loc[df['female'] == 1]['POS'].mean())
print(df.loc[df['male'] == 1]['RPOS'].mean())
print(df.loc[df['female'] == 1]['RPOS'].mean())

# %% male and female drop out
# %%
print(stats.pearsonr(df['NEG'], df['RNEG']))
print(stats.pearsonr(df['POS'], df['RPOS']))
print(stats.pearsonr(df['NEG'], df['RPOS']))
print(stats.pearsonr(df['POS'], df['RNEG']))
# %%
df[['POS', 'RPOS', 'RNEG']].corr().to_csv('dio.csv')
df[['NEG', 'RPOS', 'RNEG']].corr().to_csv('bubu.csv')

# %%
corr = df.rename(columns={
    "POS": "Pos. sent",
    "RPOS": "Pos. received",
    "NEG": "Neg. sent",
    "RNEG": "Neg. received",
})[['Pos. sent','Pos. received', 'Neg. sent', 'Neg. received']].corr()

corr.values[[np.arange(corr.shape[0])]*2] = np.nan
corr.style\
    .background_gradient(cmap='Reds').set_precision(2)\
    .highlight_null(null_color='#f1f1f1')


# %%
df[['POS', 'NEG', 'RPOS', 'RNEG', 'active']].corr().to_csv('corr.csv')
# %%
activeDropped = df.loc[
    (df['lastEditDate'] - df['firstEditDate'] > 3600*24*180)
    & (df['nEdit'] > 6)
    & (df['active'] == False)
]
activeNotDropped = df.loc[
    (df['lastEditDate'] - df['firstEditDate'] > 3600*24*180)
    & (df['nEdit'] > 6)
    & (df['active'] == True)
]
# %%
print(activeDropped['R7NEG'].mean())
print(activeNotDropped['RNEG'].mean())

# %%

print(("n", "nAngryActive", "happy", "angry"))
print(df.loc[df['active'] == True ].shape[0] / df.shape[0])
ns = [n / 1000 for n in range(1, 51)]
sen = []
rec = []
for e in ['NEG', 'RNEG']:
    print(e)
    for n in tqdm(ns):
        rNegMean = df[e].mean() + n
        happy = df.loc[df[e] <= rNegMean]
        angry = df.loc[df[e] > rNegMean]

        nActive = df.loc[df['active'] == True].shape[0]
        nHappyActive = happy.loc[happy['active'] == True].shape[0]
        nAngryActive = angry.loc[angry['active'] == True].shape[0]

        if e == 'NEG':
            sen.append(nAngryActive / angry.shape[0])
        else:
            rec.append(nAngryActive / angry.shape[0])

        

        # print((
        #     n,
        #     nAngryActive,
        #     nHappyActive / happy.shape[0],
        #     nAngryActive / angry.shape[0],
        # ))

# %% plot
plt.plot(ns, rec, label='Received')
plt.plot(ns, sen, '--', label='Sent')
plt.ylabel('Active users / users selected')
plt.xlabel('Negative emotions threashold above the average')
plt.legend()
plt.show()

# %%
# activeUsers = df.loc[df['active'] == True].shape[0] / df.shape[0]
activeMale = df.loc[(df['male'] == 1) & (df['active'] == True)].shape[0] / df.loc[df['male'] == 1].shape[0]
activeFemale = df.loc[(df['female'] == 1) & (df['active'] == True)].shape[0] / df.loc[df['female'] == 1].shape[0]
activeKnown = df.loc[(df['male'] | df['female'] == 1) & (df['active'] == True)].shape[0] / df.loc[df['male'] | df['female'] == 1].shape[0]


labels = ['Known', 'Female', 'Male']

x = np.arange(len(labels))  # the label locations
fig, ax = plt.subplots()

bars = ax.bar(
    x,
    [activeKnown, activeFemale, activeMale],
    color=['tab:gray', 'tab:orange', 'tab:blue']
)

for bar, pattern in zip(bars, ['x', '/', '+']):
    bar.set_hatch(pattern)

ax.set_ylabel('Active users')
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.legend()



# %%
secInYear = 3600 * 24 * 365
dfDropped = df.loc[(df['active']== True) & (df['nEdit'] > 5)]
print(f"Male  : {dfDropped.loc[dfDropped['male'] == True]['agespan'].mean() / secInYear}")
print(f"FeMale: {dfDropped.loc[dfDropped['female'] == True]['agespan'].mean() / secInYear}")
# %%

# %%
