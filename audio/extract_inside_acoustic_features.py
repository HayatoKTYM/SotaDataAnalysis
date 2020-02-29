# -*- coding: utf-8 -*-

"""
推定フレーム内で抽出可能な特徴を算出する
"""
__author__ = "Yuto Akagawa"
__date__    = "20170819"

import os
import csv
import sys
from scipy import stats
import numpy as np
import pprint 

class ExtractInside(object):
    def __init__(self, UNIT=10):
        self.unit = UNIT

    def extract_inside_features(self, raw, WRITE=False, AVEOUT=None, RECOUT=None):
        '''
        平均値を抽出する
        @param raw(list): 計算前のデータ
        @return ave(list): 抽出した情報
        '''
        ave = [] # 平均値を格納する
        recent = [] # 直近の特徴を取得
        ## rawが多次元配列ならば、要素のindexが同じものでlistを作成
        if type(raw[0]) == list: # raw=>多次元
            data = zip(*raw)
            for d in data:
                ave.append(self.calculate_average(d))
                recent.append(self.calculate_recent(d))
            ave = list(map(list, zip(*ave)))
            recent = list(map(list, zip(*recent)))
        else: # raw=>1次元
            data = raw
            ave = self.calculate_average(data)
            recent = self.calculate_recent(data)
            ave_out = [[i] for i in ave]
            recent_out = [[i] for i in recent]
        if WRITE and not AVEOUT == None:
            self.write_data(ave_out, AVEOUT)
        if WRITE and not RECOUT == None:
            self.write_data(recent_out, RECOUT)
        return ave, recent 

    def calculate_average(self, data):
        '''
        平均を計算する
        @param data(list): 計算するデータ(ex. [22, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14])
        @return ave(list): 計算結果
        '''
        ave = []
        for i in range(0, len(data) - self.unit + 1, self.unit):
            l = [data[i + j] for j in range(self.unit)]
            ave.append(np.average(np.array(l)))
        return ave

    def calculate_recent(self, data):
        '''
        直近の値を取得
        @param data(list): 計算するデータ(ex. [22, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14])
        @return recent(list): 計算結果
        '''
        recent = []
        for i in range(0, len(data) - self.unit + 1, self.unit):
            recent.append(data[i + (self.unit - 1)])
        return recent

    def write_data(self, data, out_file):
        '''
        csv形式でデータを書き出す
        @param data(list): 書き出すデータ
        @param out_file(str): 書き出しファイル名
        '''
        with open(out_file, 'w') as f:
            writer = csv.writer(f, lineterminator='\n') 
            writer.writerows(data) 

if __name__ == '__main__':
    data = [22, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] 
    data2 = [[22,11], [1,10], [2,21], [3,5], [4,11], [5,22], [6,5], [7,8], [8,9], [9,18], [10,16], [11,22], [12,13], [13,21], [14,15]]
    print data
    EA = ExtractInside(UNIT=2)
    ave, rec = EA.extract_inside_features(data, WRITE=False, AVEOUT="test_ave2.csv", RECOUT="test_rec2.csv")
    print len(ave)
    pprint.pprint(ave)
    print len(rec)
    pprint.pprint(rec)


