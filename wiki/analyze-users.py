# %%
from tqdm import tqdm
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# %%
typeAction = 'user'
lang = 'it'

# %% load file
df = pd.read_csv(f'../dataset/df/{typeAction}-{lang}.csv')
df['firstEditDate'] = df['firstEditDate'].apply(lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M:%S').timestamp())
df['lastEditDate'] = df['lastEditDate'].apply(lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M:%S').timestamp())
df['avgDiffTime'] = df['lastEditDate'] - df['firstEditDate']
# %%
means = [
    df.loc[df['female'] == 1]['POS'].mean(),
    df.loc[df['male'] == 1]['POS'].mean(),
]
errs = [
    df.loc[df['female'] == 1]['POS'].var(),
    df.loc[df['male'] == 1]['POS'].var(),
]

datetime.strptime