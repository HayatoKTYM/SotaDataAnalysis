#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
import sys
import pandas as pd
import argparse

sys.path.append("..")
from util.frame_generator import FrameGenerator
from util.time_keeper import TimeKeeper, set_time
from util.file_reader import FileReader

from glob import glob

# ---- config ----
mic2spkr = {"0": "sota",
            "1": "A",
            "2": "B"}

class ActLog(object):
    """
    コマンドログ
    """

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

        return self.raw_data[self.start_row:self.end_row+1].loc[(self.raw_data.utterance!="NONE")].loc[(self.raw_data.action!='SpReco')].loc[(self.raw_data.utterance!="Recognizing")]

    def to_list(self, dataframe):
        return dataframe.as_matrix().tolist()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', '-d', type=str, default='/mnt/aoni02/katayama/dataset/RawDATA/*',
                        help='specify the conversaton folder PATH')
    parser.add_argument('--out', '-o', type=str, default='/mnt/aoni02/katayama/dataset/DATA2019/vad/',
                        help='specify the LLD output folder PATH')
    args = parser.parse_args()
    directory = glob(args.dir)

    for i in directory[:1]:
        number = glob(i+"/*")
        for num in number[:1]:
            act_file = glob(num+"/*[!A].csv")[0]
            file_a = glob(num+"/000*")
            vad_file = file_a[0]+"/vad.txt"

            TK = TimeKeeper(act_file)
            act_log = ActLog(act_file)
            robot_event_list = act_log.to_list(act_log.data)

            spkr_event_list = []
            with open(vad_file, "r") as f:
                for line in f:
                    spkr_event_list.append(line.rstrip().split(' '))

            #fo = open(output+"{}.vad.csv".format(TK.recording_datetime), "w")
            print("{},{},{},{}".format('event' ,'utter_R', 'utter_A', 'utter_B'))

            # 初期化
            robot_utter = "0"
            A_utter = "0"
            B_utter = "0"
            utterance = ""

            # イテレータを生成
            f_generator = FrameGenerator(TK.start_time , TK.end_time)

            for f_time in f_generator:
                # ロボットの発話区間の最新状態を更新
                while set_time(robot_event_list[0][0]) <= f_time :
                    event =  robot_event_list.pop(0)
                    print(event[4].decode('utf-8'))
                    if event[1] != "SpeakEnd":
                        robot_utter = "1"
                        utterance = event[4]
                    else:
                        robot_utter = "0"
                        utterance = ""

                # 人間の発話区間の最新状態を更新
                while set_time(spkr_event_list[0][0]) <= f_time :
                    event =  spkr_event_list.pop(0)
                    if event[1] == "1":
                        if event[2] == "ON":
                            A_utter = "1"
                        else:
                            A_utter = "0"
                    elif event[1] == "2":
                        if event[2] == "ON":
                            B_utter = "1"
                        else:
                            B_utter = "0"
                #print("{},{},{},{}".format(event,robot_utter, A_utter, B_utter))

            #fo.close()
            print("Generated >> ..")
    print("finished!")
