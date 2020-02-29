# -*- coding: utf-8 -*-
"""
音響特徴量を抽出する
"""
__author__ = "Hayato Katayama"
__date__    = "20181128"

import sys
from Tkinter import *
import tkSnack
import csv
import commands
import pprint
import logging
import numpy as np
from print_mfcc import print_mfcc
from extract_delta_acoustic_features import ExtractDelta
from extract_inside_acoustic_features import ExtractInside
from scikits.audiolab import wavread
from glob import glob

class ExtractProsodic:
    def __init__(self):
        root = Tk()
        tkSnack.initializeSnack(root)
        self.mysound = tkSnack.Sound()

    def set_sound(self, path):
        self.mysound.read(path)

    def get_f0(self, WRITE=False, OUTPATH=None):
        f0 = self.mysound.pitch()
        ### TODO 一次元配列
        f0 = [float(i) for i in f0]
        f0_out = [[float(i)] for i in f0]
        if WRITE:
            write_data(f0_out, OUTPATH)
        return f0

    def get_power(self, WRITE=False, OUTPATH=None):
        power = self.mysound.power()
        power = [float(i) for i in power]
        power_out = [[float(i)] for i in power]
        if WRITE:
            write_data(power_out, OUTPATH)
        return power


def get_mfcc(audio_path, WRITE=False):
    from scikits.talkbox.features import mfcc # ここでimportしないとerror
    ## sckits.talkboxを使う場合
    audio, fs, enc = wavread(audio_path)
    ceps, mspec, spec = mfcc(audio, nwin=256, nfft=512, fs=fs, nceps=12)
    mfcc = ceps.tolist()
    return mfcc

def write_data(data, out_path):
    print(out_path + ' is generated..')
    f = open(out_path, 'w')
    writer = csv.writer(f, lineterminator='\n')
    writer.writerows(data)
    f.close()

def ajust_frame(file):
    Feature = list()
    EP = ExtractProsodic()
    EP.set_sound(file)
    f0 = EP.get_f0()
    power = EP.get_power()
    mfcc = get_mfcc(file)
    frame_len = min(len(f0),len(power),len(mfcc))
    print(frame_len)
    out_path = '/Users/dialog/Desktop/data2018/dataset/audio_feature/' + \
                                        file.split('/')[-1].replace('wav','csv')

    p = file.split('/')[-1].split('.')[1]#AorB
    title = ["recent_mfcc1_"+ p, "recent_mfcc2_"+ p, "recent_mfcc3_"+ p, "recent_mfcc4_"+ p, \
            "recent_mfcc5_"+ p, "recent_mfcc6_"+ p, "recent_mfcc7_"+ p, "recent_mfcc8_"+ p, \
            "recent_mfcc9_"+ p, "recent_mfcc10_"+ p, "recent_mfcc11_"+ p, "recent_mfcc12_"+ p,\
            "power_"+ p, "f0_"+ p]

    for i in range(frame_len):
        try:
            feature = mfcc[i]
            feature.extend([power[i],f0[i]])
            if len(feature) != 14: print(i)
            Feature.append(feature)
        except:
            print(f0[i],power[i])
    Feature.insert(0,title)
    write_data(Feature, out_path)

if __name__ == '__main__':
    files = glob('/Users/dialog/Desktop/data2018/dataset/wav/*wav')
    for i in range(len(files)):
        ajust_frame(files[i])
