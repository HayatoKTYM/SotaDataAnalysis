#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
ユーザA,Bの音声認識結果を抽出するスクリプト
何も発話していない部分は0 で埋めている
"""
from __future__ import print_function

__author__ = "Hayato Katayama"
__date__    = "20190304"

import pandas as pd
from datetime import timedelta
import os
import sys,time
import argparse
sys.path.append("..")
from util.frame_generator import FrameGenerator
from util.time_keeper import set_time, TimeKeeper
from util.file_reader import FileReader

from glob import glob

utterance_labels = ["None", "Passive", "Active", "Nod"]
target_labels = ["A", "B"]

class EventLog(object):

    def __init__(self, filename):
        self.raw_data = pd.read_csv(filename, header=None, names=('time', 'action', 'topic', 'target', 'utterance'),
                                    dtype={'time' : str, 'action' : str, 'topic' : str, 'target' : str, 'utterance' : str})
        self.start_row = 0
        self.end_row = 0
        self.start_time = 0
        self.end_time = 0
        self.datetime = ""  # 会話開始の時刻を識別子として利用
        self.data = self.split(filename)

    def split(self, filename):
        '''
        会話の開始(start)から終了(end)までのログを切り出す
        :return: 該当部分のログ (pandas.DataFrame)
        '''
        for i, v in self.raw_data.iterrows():
            if v['action'] == 'start':
                self.start_row  = i
                self.datetime = v['time'].split(".")[0]
                self.start_time = set_time(v['time'])
            elif v['action'] == 'end':
                self.end_row  = i
                self.end_time = set_time(v['time'])
                break

        return (self.raw_data[self.start_row:self.end_row+1].loc[(self.raw_data.action!="change_topic")])\
                    .loc[(self.raw_data.action!="change_genre")].loc[self.raw_data.utterance!="Recognizing"]\


    def to_list(self, dataframe):
        return dataframe.as_matrix().tolist()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', '-i', type=str, default='/mnt/aoni02/katayama/dataset/RawDATA/raw',
                        help='specify the conversaton folder PATH')
    parser.add_argument('--out', '-o', type=str, default='/mnt/aoni02/katayama/dataset/DATA2019/decode/',
                        help='specify the label output folder PATH')
    args = parser.parse_args()
    print('Extaction Folder : {}'.format(args.dir))
    print('Output Folder : {}'.format(args.out))
    directory = glob(os.path.join(args.dir,'*'))
    output = args.out
    if not os.path.isdir(output):
        os.mkdir(output)

    for i in directory:
        number = glob(os.path.join(i,"*"))
        for num in number:
            act_file = glob(num+"/*[!A].csv")[0]
            eventlog = EventLog(act_file)
            tk = TimeKeeper(act_file)

            fo = open(os.path.join(output, "{}.decode.csv".format(tk.recording_datetime)), "w")
            print("A,B", file=fo)
            f_genenrator = FrameGenerator(tk.start_time, tk.end_time,frame_rate=100)

            target = "A"
            action = ""
            utterance_ = ""
            lkcount = 0
            flag = 0
            event_list = eventlog.data.as_matrix().tolist()
            for f_time in f_genenrator:#フレーム単位ごとに
                log_time = set_time(event_list[0][0])#logにあるイベント

                if f_time >= log_time:
                    event = event_list.pop(0)
                    if event[1] == "SpReco":
                        person = {"A":1,"B":2}
                        utterance_ = event[4]#[0].encode('utf-8')

                        if person[event[3][0]] == 1:
                            print("{},{}".format(utterance_,"0"), file=fo)
                        else:
                            print("{},{}".format("0",utterance_), file=fo)
                    else:
                        print("{},{}".format('0',"0"), file=fo)

                else:
                    print("{},{}".format('0',"0"), file=fo)

            fo.close()


if __name__ == '__main__':
    main()
