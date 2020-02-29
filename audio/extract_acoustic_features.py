# -*- coding: utf-8 -*-

"""
音響特徴量を抽出する
"""
__author__ = "Yuto Akagawa"
__date__    = "20170725"

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
sys.path.append("../util")
from time_keeper import TimeKeeper
from glob import glob

def write_data(data, output_path):
    f = open(output_path, 'w')
    writer = csv.writer(f, lineterminator='\n')
    writer.writerows(data)
    f.close()

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
    """
    ## soxを使う場合
    mfcc_dim = 12 #取得するMFCCの次元数
    command = "x2x +sf < " + audio_path + " | frame -l 400 -p 160 | mfcc -l 400 -f 16 -m 12 -n 20 -a 0.97 >" + output_path
    check = commands.getoutput(command)
    if check != "":
        logging.exception("*** Extracting MFCC :: " + check + " ***")
        sys.exit(1)
    mfcc = print_mfcc(output_path, mfcc_dim)
    mfcc_list = []
    for i in mfcc:
        l = []
        for j in i:
            l.append(float(j))
        mfcc_list.append(l)
    """
    ## sckits.talkboxを使う場合
    audio, fs, enc = wavread(audio_path)
    ceps, mspec, spec = mfcc(audio, nwin=256, nfft=512, fs=fs, nceps=12)
    mfcc = ceps.tolist()

    if WRITE:
        write_data(mfcc, output_path + ".csv")
    return mfcc

class ExtractAudioFeatures(object):
    def __init__(self, TK, APATH=None, BPATH=None, UNIT=10, WINDOW=50, OUTDIR="../../../audio/", WRITE=False):
        self.outpath = OUTDIR + TK.recording_datetime + ".audio.csv" # この後ろに.f0などの識別子をつける必要がある
        print self.outpath
        self.duration_sec = TK.duration_sec
        self.unit = UNIT
        self.frame_len = int(self.duration_sec * 100 / self.unit)
        self.audioApath = APATH
        self.audioBpath = BPATH
        self.write = WRITE
        self.window = WINDOW
        self.EP = ExtractProsodic()
        self.ED = ExtractDelta(UNIT=UNIT, WINDOW=WINDOW, OUTDIR=OUTDIR)
        self.EI = ExtractInside(UNIT=UNIT)

    def adjust_length(self, list_data):
        while 1:
            if len(list_data) > self.frame_len * self.unit:
                list_data.pop(-1)
            elif len(list_data) < self.frame_len * self.unit:
                if type(list_data[-1]) == list:
                    list_data.append([0.0 for i in list_data[-1]])
                else:
                    list_data.append(0.0)
            else:
                break
        return list_data

    def get_features(self):
            person_key = {self.audioApath: "A", self.audioBpath: "B"}
            header_info = {"A": [], "B": []}
            mfcc = {"A": [], "B": []}
            f0 = {"A": [], "B": []}
            power = {"A": [], "B": []}
            dmfcc = {"A": [], "B": []}
            df0 = {"A": [], "B": []}
            dpower = {"A": [], "B": []}
            ave_mfcc = {"A": [], "B": []}
            ave_f0 = {"A": [], "B": []}
            ave_power = {"A": [], "B": []}
            rec_mfcc = {"A": [], "B": []}
            rec_f0 = {"A": [], "B": []}
            rec_power = {"A": [], "B": []}
            for path in self.audioApath, self.audioBpath:
                p = person_key[path]
                header_info[p] = ["recent_mfcc1_"+ p, "recent_mfcc2_"+ p, "recent_mfcc3_"+ p, "recent_mfcc4_"+ p, "recent_mfcc5_"+ p, "recent_mfcc6_"+ p, "recent_mfcc7_"+ p, "recent_mfcc8_"+ p, "recent_mfcc9_"+ p, "recent_mfcc10_"+ p, "recent_mfcc11_"+ p, "recent_mfcc12_"+ p, "average_mfcc1_"+ p, "average_mfcc2_"+ p, "average_mfcc3_"+ p, "average_mfcc4_"+ p, "average_mfcc5_"+ p, "average_mfcc6_"+ p, "average_mfcc7_"+ p, "average_mfcc8_"+ p, "average_mfcc9_"+ p, "average_mfcc10_"+ p, "average_mfcc11_"+ p, "average_mfcc12_"+ p, "delta_mfcc1_"+ p, "delta_mfcc2_"+ p, "delta_mfcc3_"+ p, "delta_mfcc4_"+ p, "delta_mfcc5_"+ p, "delta_mfcc6_"+ p, "delta_mfcc7_"+ p, "delta_mfcc8_"+ p, "delta_mfcc9_"+ p, "delta_mfcc10_"+ p, "delta_mfcc11_"+ p, "delta_mfcc12_"+ p, "recent_f0_"+ p, "average_f0_"+ p, "delta_f0_"+ p, "recent_power_"+ p, "average_power_"+ p, "delta_power_"+ p]
                self.EP.set_sound(path)
                mfcc[p] = get_mfcc(path)
                mfcc[p] = self.adjust_length(mfcc[p])
                f0[p] = self.EP.get_f0()
                f0[p] = self.adjust_length(f0[p])
                power[p] = self.EP.get_power()
                power[p] = self.adjust_length(power[p])
                print "####" + p + "####"
                print "##MFCC POWER F0###"
                print len(mfcc[p]), len(power[p]), len(f0[p])
                dmfcc[p] = self.ED.extract_delta(mfcc[p])
                #dmfcc[p] = self.adjust_length(dmfcc[p])
                print "*** dmfcc ***"
                print "rows:", len(dmfcc[p]), " columns:", len(dmfcc[p][-1])
                ave_mfcc[p], rec_mfcc[p] = self.EI.extract_inside_features(mfcc[p])
                #ave_mfcc[p] = self.adjust_length(ave_mfcc[p])
                #rec_mfcc[p] = self.adjust_length(rec_mfcc[p])
                print "*** average mfcc ***"
                print "rows:", len(ave_mfcc[p]), " columns:", len(ave_mfcc[p][-1])
                print "*** rec mfcc ***"
                print "rows:", len(rec_mfcc[p]), " columns:", len(rec_mfcc[p][-1])
                df0[p] = self.ED.extract_delta(f0[p])
                #df0[p] = self.adjust_length(df0[p])
                print "*** df0 ***"
                print "rows:", len(df0[p]), " columns:1"
                ave_f0[p], rec_f0[p] = self.EI.extract_inside_features(f0[p])
                #ave_f0[p] = self.adjust_length(ave_f0[p])
                #rec_f0[p] = self.adjust_length(rec_f0[p])
                print "*** average f0 ***"
                print "rows:", len(ave_f0[p]), " columns:1"
                print "*** rec f0 ***"
                print "rows:", len(rec_f0[p]), " columns:1"
                dpower[p] = self.ED.extract_delta(power[p])
                #dpower[p] = self.adjust_length(dpower[p])
                print "*** dpower ***"
                print "rows:", len(dpower[p]), " columns:1"
                ave_power[p], rec_power[p] = self.EI.extract_inside_features(power[p])
                #ave_power[p] = self.adjust_length(ave_power[p])
                #rec_power[p] = self.adjust_length(rec_power[p])
                print "*** average power ***"
                print "rows:", len(ave_power[p]), " columns:1"
                print "*** rec power ***"
                print "rows:", len(rec_power[p]), " columns:1"
                print ""
                rec_mfcc[p] = np.array(rec_mfcc[p])
                ave_mfcc[p] = np.array(ave_mfcc[p])
                dmfcc[p] = np.array(dmfcc[p])
                rec_f0[p] = np.array(rec_f0[p])
                ave_f0[p] = np.array(ave_f0[p])
                df0[p] = np.array(df0[p])
                rec_power[p] = np.array(rec_power[p])
                ave_power[p] = np.array(ave_power[p])
                dpower[p] = np.array(dpower[p])

            if self.write:
                audio_info = np.c_[rec_mfcc["A"], ave_mfcc["A"], dmfcc["A"], rec_f0["A"], ave_f0["A"], df0["A"], rec_power["A"], ave_power["A"], dpower["A"], rec_mfcc["B"], ave_mfcc["B"], dmfcc["B"], rec_f0["B"], ave_f0["B"], df0["B"], rec_power["B"], ave_power["B"], dpower["B"]]
                audio_info = audio_info.tolist()
                audio_info.insert(0, header_info["A"] + header_info["B"])
                print ""
                print "=== audio_info ==="
                print "rows(including the header):", len(audio_info), " columns:", len(audio_info[-1])
                write_data(audio_info, self.outpath)

if __name__ == '__main__':
    """
    kinect_dir = sys.argv[1]
    label_dir = sys.argv[2]
    wav_dir = sys.argv[3]

    # configure fileから複数のファイルを読み込む場合
    f = open('../files.conf', 'r')
    reader = csv.reader(f)
    header = next(reader)
    for row in reader:
        kinect_setting = kinect_dir + row[1] # KINECTのsettingファイルパス
        act = label_dir + row[2] # Dialog Actのログファイルパス
        a_path = wav_dir + row[5]
        b_path = wav_dir + row[6]
        TK = TimeKeeper(kinect_setting, act)
        EA = ExtractAudioFeatures(TK, APATH=a_path, BPATH=b_path, WRITE=True)
        EA.get_features()
    f.close()
    """
    wav_dir = glob("../../dataset/wav/20180629*")
    #print(wav_dir)
    cnt=0
    directory = glob('../../data/0629*')
    #print(directory)
    for i in directory:
        number = glob(i+"/*")
        #print(number[0])
        for num in number:
            setting_file = glob(num+"/*a.txt")[0]
            act_file = glob(num+"/*[!A].csv")[0]
            wav_a = wav_dir[cnt]
            wav_b = wav_dir[cnt+1]
            # 一つのファイルを読み込む場合
            kinect_setting = setting_file # KINECTのsettingファイルパス
            act = act_file # Dialog Actのログファイルパス
            TK = TimeKeeper(kinect_setting, act)
            #person_id = sys.argv[3].split(".")[-2]
            EA = ExtractAudioFeatures(TK, APATH=wav_a, BPATH=wav_b, WRITE=True)
            EA.get_features()
            cnt+=2
