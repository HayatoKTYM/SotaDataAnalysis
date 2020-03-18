def del_duplication(df):
    """
    重複を消す関数
    """
    y = []
    flag = False
    for i in range(len(df)):
        # 1 なら 最初の 1 だけ残す (行動開始点)
        if df['active_add'].values[i]: 
            if flag:
                y.append(0)
            else:
                y.append(1)
                flag = True
        else: # "0" ならそのまま
            flag = False
            y.append(0)
    return y

from label_maker import MakeLabelDataset
import pandas as pd
import numpy as np
import glob

feature_files = sorted(glob.glob('/Volumes/Samsung_T5/prj-woz/data/feature/*csv'))[13:]
files = sorted(glob.glob('/Volumes/Samsung_T5/prj-woz/ELAN/*eaf'))

import os
os.makedirs('/Volumes/Samsung_T5/prj-woz/data/feature_elan/',exist_ok=True)

FEATURE_PATH = '/Volumes/Samsung_T5/prj-woz/data/feature/'
import datetime
now = datetime.datetime.now()
fo = open('log_{}.txt'.format(now.strftime('%Y%m%d_%H%M%S')),'w')
for f in files:
    f_name = FEATURE_PATH +  os.path.basename(f).split('.')[0] + '.feature.csv'
    
    print(f_name,file=fo)
    make_data = MakeLabelDataset(f)
    df = pd.read_csv(f_name)
    label = make_data(len(df),100)
    y = df['action'].map(lambda x:1 if x == 'Active' else 0)
    
    df['elan_active'] = np.minimum(label + y.values,1)
    df['active_add'] = np.logical_or(y,df['elan_active'])
    df['active_add'] = del_duplication(df)
    print('ELAN active cnt is {}, max is {}, and diff to wizards label is {}'.format(df['elan_active'].sum(),df['elan_active'].max(),df['active_add'].sum()-y.sum()),file=fo)
    df.to_csv(f_name.replace('/feature','/feature_elan',1),index=False)
fo.close()
