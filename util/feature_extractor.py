# -*- coding: utf-8 -*-
"""
python3
全ての特徴量をconcatしたファイルを生成する
label/
decode/
vad/
gaze/
"""
import os
import glob
import pandas as pd
from argparse import ArgumentParser

def concat_feature(lf=None, df=None, vf=None, gf=None):
    df_label = pd.read_csv(lf)
    df_decode = pd.read_csv(df)
    df_vad = pd.read_csv(vf)
    #df_gaze = pd.read_csv(gf)

    assert len(df_label) == len(df_decode), print('cannot concat files.')
    df = pd.concat([df_label, df_decode, df_vad],axis=1)
    df = df.fillna(0)
    return df

if __name__ == '__main__':
    parser = ArgumentParser()

    parser.add_argument("-i", "--dir", type=str, metavar="DIRECTORY", required=False, default='/Volumes/Untitled/WOZData',
                        help="data directory")
    parser.add_argument("-o", "--out", type=str, metavar="DIRECTORY", required=False,
                        help="output directory", default="/Volumes/Untitled/WOZData/feature")
    parser.add_argument("--debug", required=False,
                        help="is debug", action='store_true')

    args = parser.parse_args()

    label_files = sorted(glob.glob(os.path.join(args.dir,'label/*.csv')))
    decode_files = sorted(glob.glob(os.path.join(args.dir, 'decode/*.csv')))
    vad_files = sorted(glob.glob(os.path.join(args.dir,'vad/*.csv')))
    #gaze_files = sorted(glob.glob(os.path.join(args.datadir, '/gaze/*.csv')))

    output = args.out
    if not os.path.isdir(output):
        os.mkdir(output)

    for lf, df, vf in zip(label_files, decode_files, vad_files):
        print(lf.split('.')[-3].split('/')[-1])
        if lf.split('.')[-3].split('/')[-1]  \
           == vf.split('.')[-3].split('/')[-1]  \
           == df.split('.')[-3].split('/')[-1]:
           #== gf.split('.')[-3].split('/')[-1] \


            datetime = lf.split('.')[-3].split('/')[-1]
            OUTPUT = "{}/{}.feature.csv".format(output, datetime)

            concat_df = concat_feature(lf,df,vf)
            concat_df.to_csv(OUTPUT,index=False)
        else:
            print('error')
