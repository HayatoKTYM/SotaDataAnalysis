#!/usr/bin/python3
# -*- coding:utf-8 -*-
__author__ = 'Hayato Katayama'
"""
LLDを抽出するプログラム
.wav を 指定すると抽出されるが，事前にopensmile をインストールしておく必要あり
入力 : wav/*wav
出力 : LLD/*csv
"""
import subprocess
import os
from glob import glob
import pandas as pd
import argparse

order = 'bash /Users/hayato/Downloads/openSMILE-2.3.0/SMILExtract '
config = '-C /Users/hayato/Downloads/openSMILE-2.3.0/emobase2010_csv_lld.conf '
columns = [str(i+1) for i in range(228)]

def extract_lld(INPUT:str,OUTPUT:str):
    """
    :param INPUT: 入力ファイルPATH (.wav)
    :param OUTPUT: 出力ファイルPATH (.csv)
    :return:
    """
    cmd =  order + config + '-I ' + INPUT + ' -O ' + OUTPUT
    print(cmd)
    try:
        res = subprocess.run(cmd, shell=True)
    except Exception as e:
        print("Runtime Error.")

def concat_lld(INPUT_A:str,INPUT_B:str):
    """
    :param INPUT_A: AのLLD抽出ファイル
    :param INPUT_B: BのLLD抽出ファイル
    :return:
    """
    df_A = pd.read_csv(INPUT_A)
    df_B = pd.read_csv(INPUT_B)
    assert len(df_A) == len(df_B), print('Not a property file, you specify A & B LLD files?')

    df = pd.concat([df_A,df_B],axis=1)
    df.columns = columns
    return df

if __name__ == '__main__':
    """
    1. A,Bの音声からLLD特徴量抽出
    2. A,Bの特徴量ファイルをconcat
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', '-i', type=str, default='/mnt/aoni02/katayama/dataset/DATA2019/wav',
                        help='specify the wav folder PATH')
    parser.add_argument('--out', '-o', type=str, default='/mnt/aoni02/katayama/dataset/DATA2019/lld',
                        help='specify the LLD output folder PATH')
    args = parser.parse_args()
    print('Extaction Folder : {}'.format(args.dir))
    print('Output Folder : {}'.format(args.out))
    output = args.out
    if not os.path.isdir(output):
        os.mkdir(output)

    wav_files = sorted(glob(os.path.join(args.dir,'*.wav')))
    for wav_f in wav_files:
        INPUT = wav_f
        OUTPUT = INPUT.replace('.wav','.lld.csv').replace('/wav','/lld')
        extract_lld(INPUT=INPUT,OUTPUT=OUTPUT)

    lld_files = sorted(glob(os.path.join(output,'*csv')))
    for i in range(0,len(lld_files),2):
        df = concat_lld(INPUT_A = lld_files[i],INPUT_B = lld_files[i+1])
        if not os.path.isdir(output.replace('/lld','/lld_all')):
            os.mkdir(output.replace('/lld','/lld_all'))
        df.to_csv(lld_files[i].replace('.A','.LLD').replace('/lld/','/lld_all/'),index=False)
        print('generated>>',lld_files[i])
