# -*- coding: utf-8 -*-

"""
音響情報のデルタを算出する
"""
__author__ = "Yuto Akagawa"
__date__    = "20170816"

import os
import csv
import sys
from scipy import stats
import pprint 

class ExtractDelta(object):
    def __init__(self, UNIT=100, WINDOW=50, OUTDIR="../dataset/audio/"):
        self.output_dir = OUTDIR
        self.unit = UNIT
        self.window = WINDOW

    def extract_delta(self, raw, WRITE=False, OUTFILE=None):
        '''
        デルタを抽出する
        @param raw(list): デルタ計算前のデータ
        @return delta(list): 抽出したデルタ情報
        '''
        delta = [] # デルタ情報を格納
        ## rawが多次元配列ならば、要素のindexが同じものでlistを作成
        if type(raw[0]) == list: # raw=>多次元
            data = zip(*raw)
            for d in data:
                delta.append(self.calculate_delta(d))
            delta = list(map(list, zip(*delta)))
        else: # raw=>1次元
            data = raw
            delta = self.calculate_delta(data)
            delta_out = [[i] for i in delta]
        if WRITE and not OUTFILE == None:
            self.write_data(delta_out, OUTFILE)
        return delta 

    def calculate_delta(self, data):
        '''
        デルタを計算する
        @param data(list): 計算するデータ(ex. [22, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14])
        @return delta(list): 計算結果
        '''
        delta = []
        window_list = [0 for i in range(self.window)]
        threshold = self.unit
        index_list = map(lambda i: i + 1, range(self.window))
        for count, i in enumerate(range(-self.window, len(data) - self.window + 1)):
            if i < 0:
                window_list.append(data[i + self.window])
                window_list.pop(0)
            else:
                window_list = data[i + 1: i + 1 + self.window]
                if not len(window_list) == self.window:
                    break
            if count == threshold - 1:
                slope, intercept, r_value, _, _ = stats.linregress(index_list, window_list)
                delta.append(slope)
                threshold += self.unit
        return delta

    def write_data(self, data, out_file):
        '''
        csv形式でデータを書き出す
        @param data(list): 書き出すデータ
        @param out_file(str): 書き出しファイル名
        @param MULTI(Boolean): 多次元配列ならTrue, 1次元配列ならFalse
        '''
        with open(out_file, 'w') as f:
            writer = csv.writer(f, lineterminator='\n') 
            writer.writerows(data) 

if __name__ == '__main__':
    data = [22, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] 
    data2 = [[22,11], [1,10], [2,21], [3,5], [4,11], [5,22], [6,5], [7,8], [8,9], [9,18], [10,16], [11,22], [12,13], [13,21], [14,15]]
    print data
    ED = ExtractDelta(UNIT=2, WINDOW=5, OUTDIR="../../")
    delta = ED.extract_delta(data, WRITE=False, OUTFILE="test_delta_audio4.csv")
    pprint.pprint(delta)

