from glob import glob
import pandas as pd
import numpy as np
import os

PATH = '/Volumes/Samsung_T5/prj-woz/data/20200222'
vad_files = sorted(glob(os.path.join(PATH,'vad/*csv')))
label_files = sorted(glob(os.path.join(PATH,'label/*csv')))
#vad_files = sorted(glob('/Volumes/Samsung_T5/prj-woz/data/vad/*csv'))
#label_files = sorted(glob('/Volumes/Samsung_T5/prj-woz/data/label/*csv'))

print('file length is {} and {}'.format(len(vad_files), len(label_files)))
for vf, lf in zip(vad_files,label_files):
    print(lf)
    df = pd.read_csv(lf)
    output = vf.split('/')[-1].split('.cs')[0]
    os.makedirs('/Volumes/Samsung_T5/prj-woz/data/text',exist_ok=True)
    f = open('/Volumes/Samsung_T5/prj-woz/data/text/{}.txt'.format(output),'w')
    start = 0
    nod_flag = False
    act_flag = False
    init_flag = True
    target_start = 0
    pre_t = df.values[0][-2]
    print('first position is {}'.format(pre_t))
    for act,act_detail,target,_ in df.values:
            
        t = target
        if act in ['Passive','Active'] : #開始
            u_start = start
            u_action = act
            u_action_detail = act_detail + target
            act_flag = True
        #elif act_detail == 'SpeakEnd' : #終了
        elif _ == '0' and act_flag:
            act_flag = False
            u_end = start
            print('{},{},{},{}'.format(u_action,u_action_detail,u_start,u_end),file=f)

        elif act == 'Nod' : #開始
            nod_flag = True
            u_start = start 
            u_action_detail = 'nod'+target
        elif nod_flag: #終了
            nod_flag = False
            u_end = start
            print('Nod,{},{},{}'.format(u_action_detail,u_start,u_end),file=f)

        if pre_t != t:
            #print(pre_t,t)
            target_end = start
            
            target_detail = 'look'+pre_t
            print('look,{},{},{}'.format(target_detail,target_start,target_end),file=f)
            target_start = start
            pre_t = t

        start = start + 100
    else:# 最後のLook漏れを補正 
        target_end = start
        target_detail = 'look'+pre_t
        print('look,{},{},{}'.format(target_detail,target_start,target_end),file=f)
        
    df = pd.read_csv(vf)
    # ut を計算
    u_t = np.clip(1.0 - (df['utter_A'] + df['utter_B']),0,1)
    df['u_t'] = u_t
    start = 0
    u_flag,a_flag,b_flag = [False]*3
    ut_flag = False
    for u,a,b,ut in df.values:
        if u == 1 and not u_flag: #開始
            u_flag = True
            u_start = start 
        elif u == 0 and u_flag: #終了
            u_flag = False
            u_end = start
            print('VAD_S,1,{},{}'.format(u_start,u_end),file=f)

        if a == 1 and not a_flag: #開始
            a_flag = True
            a_start = start 
        elif a == 0 and a_flag: #終了
            a_flag = False
            a_end = start
            print('VAD_A,1,{},{}'.format(a_start,a_end),file=f)

        if b == 1 and not b_flag: #開始
            b_flag = True
            b_start = start 
        elif b == 0 and b_flag: #終了
            b_flag = False
            b_end = start
            print('VAD_B,1,{},{}'.format(b_start,b_end),file=f)
            
        if ut == 1 and not ut_flag: #開始
            ut_flag = True
            ut_start = start 
        elif ut == 0 and ut_flag: #終了
            ut_flag = False
            ut_end = start
            print('u_t,1,{},{}'.format(ut_start,ut_end),file=f)
        start = start + 100

    f.close()
