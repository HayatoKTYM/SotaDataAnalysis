# -*- coding: utf-8 -*-
"""
データ加工用に使用する時間を取得する
"""

__author__ = "Hayato Katayama"
__date__    = "20190304"

import csv
import sys
from datetime import timedelta


def set_time(time):
    '''
    strの時間表現をdatetime.timedelta型に変換する
    ex) time = "20170724190720.732407"
    '''
    microsec_len = len(time.split(".")[1])
    hours = int(time[8:10])
    minutes = int(time[10:12])
    seconds = int(time[12:14])
    microseconds = int(time.split(".")[1] + "0" * (6 - microsec_len))  # 桁が足りない場合に0埋めをする
    return timedelta(hours=hours, minutes=minutes, seconds=seconds, microseconds=microseconds)

class TimeKeeper:
    def __init__(self, act_file):
        self.diff_sound = 0  # 音声ファイルとの差分時間[s]
        self.diff_movie = 0  # カメラ映像との差分時間[s]
        self.start_time = 0
        self.recording_datetime = 0
        self.end_time = 0
        self.get_time(act_file)
        self.duration_sec = (self.end_time - self.start_time).total_seconds()

    def set_time(self, time):
        '''
        strの時間表現をdatetime.timedelta型に変換する
        ex) time = "20170724190720.732407"
        '''
        microsec_len = len(time.split(".")[1])
        hours = int(time[8:10])
        minutes = int(time[10:12])
        seconds = int(time[12:14])
        microseconds = int(time.split(".")[1] + "0" * (6 - microsec_len))  # 桁が足りない場合に0埋めをする
        return timedelta(hours=hours, minutes=minutes, seconds=seconds, microseconds=microseconds)

    def get_time(self, act_file):
        """
        各ファイルからstart/end時間抽出
        act_file (.csv)
        """
        init_flag = False
        f = open(act_file, 'r')
        reader = csv.reader(f)
        for row in reader:
            if 'start' in row:
                self.start_time = self.set_time(row[0])
                self.recording_datetime = row[0].split('.')[0]
                init_flag = True
            elif 'end' in row and init_flag:
                self.end_time = self.set_time(row[0])
                init_flag = False
                break
        f.close()

    def get_diff_sound(self, vad_file):
        """
        音声ファイルとの差分を抽出
        vad_file (.txt)
        """
        f = open(vad_file, 'r')
        time = f.readlines()[0].split()[0]
        start = self.set_time(time)
        diff_start = self.start_time - start

        return diff_start.total_seconds()

    def get_diff_movie(self, movie_file):
        """
        videoファイルとの差分を抽出
        movie_file (.avi)
        """
        time = movie_file.split('/')[-1].split('.')[0]
        time = time.replace('_', '', 5)
        time = time.replace('_', '.', 1)
        start = self.set_time(time)
        diff_start = self.start_time - start

        return diff_start.total_seconds()

#確認用
if __name__ == '__main__':
    TK = TimeKeeper(act_file='/Volumes/Untitled/WOZRawData/0703/03/201907031506.csv')
    print(TK.start_time)
    print(TK.end_time)
    print(TK.duration_sec)
    wav_start = TK.get_diff_sound('/Volumes/Untitled/WOZRawData/0703/03/00000124/vad.txt')
    print(wav_start)
    movie_start = TK.get_diff_movie('/Volumes/Untitled/WOZRawData/0710/03/2018_07_10_19_42_09_484071.avi')
    print(movie_start)
