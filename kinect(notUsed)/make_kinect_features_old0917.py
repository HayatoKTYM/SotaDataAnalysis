# -*- coding: utf-8 -*-

"""
Kinectデータを加工する
"""
__preauthor__ = "Yuto Akagawa"
__date__    = "20170804"

__author__ = "Hayato Katayama"
__date__ = "20180917"

import os
import csv
import sys
import pandas as pd
from datetime import timedelta
import logging
sys.path.append("../util")
from time_keeper import TimeKeeper
from glob import glob

class MakeKinectFeatures(object):
    def __init__(self, UNIT=100, TK=None, INPUT=None, OUTDIR="../../dataset/kinect/"):
        '''
        コンストラクタ
        @param UNIT(int): フレーム幅[ms]
        @param TK(Timekeeper): 時間情報を管理しているモジュールのインスタンス
        @param INPUT(str): 入力ファイル(KINECT情報のraw data)のpath
        @param OUTDIR: 出力ファイルを吐き出すディレクトリpath
        '''
        self.frame_unit = timedelta(milliseconds = UNIT) # 推定単位[ms]
        if TK == None:
            logging.exception("*** TimeKeeperが設定されていません ***")
            sys.exit(1)
        if INPUT == None:
            logging.exception("*** 入力ファイルパスが設定されていません ***")
            sys.exit(1)
        TK.convert_kinect_timezone()
        self.start_time = TK.start_delta # RECORDING START から会話開始までの差分 (timedelta)
        self.end_time = TK.end_delta # RECORDING START から会話終了までの差分 (timedelta)
        self.duration = TK.duration  # 会話開始から会話終了までの差分 (timedelta)
        self.duration_sec = TK.duration_sec
        self.frame_len = int(self.duration_sec * 10) + 1
        self.my_time = TK.kinect_start_time # 収録開始の時刻 (timedelta)
        self.data = pd.read_csv(INPUT) # 読み込んだデータ(data frame)
        self.out_path = OUTDIR + TK.recording_datetime + ".kinect.csv" # 出力ファイルパス
        Pid = INPUT.split("/")[-1].split("-")[-1].split(".")[0]
        self.Aid = int(Pid.split("_")[0]) # 参加者AのID
        self.Bid = int(Pid.split("_")[1]) # 参加者BのID

    def make_features(self, SWAY=False, FACE=False):
        '''
        特徴量の作成
        @param SWAY(Boolean): 体の揺れに関する特徴を抽出するか
        @param FACE(Boolean): 顔向きに関する特徴を抽出するか
        '''
        if SWAY:
            print "is extracting the SWAY Info.."
            swayA, swayB = self.get_sway()
            print "== SWAY =="
            print swayA[0]
            print len(swayA)
            print swayB[0]
            print len(swayB)
        if FACE:
            print "is extracting the Face Info.."
            faceA, faceB = self.get_face_info()
            print "== FACE =="
            print faceA[0]
            print faceB[0]
        if SWAY and FACE:
            kinect_info = []
            count = 0
            for sA, sB, fA, fB in zip(swayA, swayB, faceA, faceB):
                if count == self.frame_len:
                    break
                l = sA
                l.extend(sB)
                l.extend(fA)
                l.extend(fB)
                kinect_info.append(l)
                count += 1
            f = open(self.out_path, 'w')
            writer = csv.writer(f, lineterminator='\n')
            writer.writerows(kinect_info)
            print "== KINECT INFO =="
            print len(kinect_info)
            f.close()

    def set_time(self, time):
        '''
        時間をtimedelta型に変換
        @param time(str): 変換する時間(ex."20170724190720732407")
        @return timedelta型に変換した時刻(timedelta)
        '''
        hours = int(time[8:10])
        minutes = int(time[10:12])
        seconds = int(time[12:14])
        microseconds = int(time[14:20])
        return timedelta(hours = hours, minutes = minutes, seconds = seconds, microseconds = microseconds)

    def calculate_delta_sway(self, sway_list, person):
        '''
        x, y, zそれぞれの動きの変化量をフレームごとに算出
        @param sway_list(list): 動きの情報[会話開始からのtime delta, 各部位の座標情報が入ったdict]
        @param person(str): 参加者(ex. A)
        @return delta_list(list): 動きの変化量
        '''
        delta_list = [["delta_x_" + person, "delta_y_" + person, "delta_z_" + person]]
        t = self.frame_unit
        init_flag = True
        while t <= self.duration + self.frame_unit:
            is_updated = False
            l = []
            delta = 0.0
            # the processing of calculate
            for v in sway_list:
                if v[0] >= (t + self.frame_unit):
                    break
                if v[0] > t:
                    if init_flag:
                        delta_list.append([0.0, 0.0, 0.0])
                        init_flag = False
                        presway = v[1]
                    else:
                        for column in ("x", "y", "z"):
                            for key in v[1][column]:
                                delta += abs(sway[column][key] - presway[column][key])
                            l.append(delta)
                        presway = sway
                        delta_list.append(l)
                    is_updated = True
                    break
                sway = v[1]
            else:
                for column in ("x", "y", "z"):
                    for key in v[1][column]:
                        delta += abs(sway[column][key] - presway[column][key])
                    l.append(delta)
                delta_list.append(l)
                break
            if not is_updated:
                delta_list.append([0.0, 0.0, 0.0])
            t += self.frame_unit
        return delta_list

    def get_sway(self):
        '''
        前フレームからの動きの変化量を参加者それぞれで算出
        @ return dsway_A(list): 参加者Aの動きの情報
        @ return dsway_B(list): 参加者Bの動きの情報
        '''
        self.columns_dict = {"x": [], "y": [], "z": []}
        for c in self.data.columns:
            if "color" in c or "yaw" in c:
                continue
            elif "_x" in c:
                self.columns_dict["x"].append(c)
            elif "_y" in c:
                self.columns_dict["y"].append(c)
            elif "_z" in c:
                self.columns_dict["z"].append(c)
        sway_list = {"A":[], "B":[]}
        f = False
        for i, v in self.data.iterrows():
            sway = {"x": {}, "y": {}, "z": {}}
            time = self.set_time(v["Time"]) - self.my_time
            if self.start_time <= time and time <= self.end_time:
                if v[" faceindex"] == self.Aid:
                    person_id = "A"
                elif v[" faceindex"] == self.Bid:
                    person_id = "B"
                else:
                    continue
                for x in self.columns_dict["x"]:
                    sway["x"][x] = float(v[x])
                for y in self.columns_dict["y"]:
                    sway["y"][y] = float(v[y])
                for z in self.columns_dict["z"]:
                    sway["z"][z] = float(v[z])
                sway_list[person_id].append([time - self.start_time, sway])
                f = True
        dsway_A = self.calculate_delta_sway(sway_list["A"], "A")
        dsway_B = self.calculate_delta_sway(sway_list["B"], "B")
        return dsway_A, dsway_B

    def calculate_face_info(self, face_list, person):
        '''
        顔向きに関する情報(デルタピッチ, ヨー)をフレームごとに算出
        @param face_list(list): 顔向き情報[会話開始からのtime delta, pitch, yaw]
        @param person(str): 参加者(ex. A)
        @return face_info_list: 顔向き情報
        '''
        ## face_list = [time, pitch, yaw]
        t = self.frame_unit
        init_flag = True
        face_info_list = [["delta_pitch_" + person, "yaw_" + person]]
        pitch = 0.0
        prepitch = 0.0
        yaw = 90.0
        while t <= self.duration + self.frame_unit:
            is_updated = False
            l = []
            # the processing of calculate
            for v in face_list:
                if v[0] >= (t + self.frame_unit):
                    break
                if v[0] > t:
                    if init_flag:
                        if v[2] == "none":
                            yaw = 90.0
                        face_info_list.append([0.0, yaw])
                        init_flag = False
                        if not v[1] == "none":
                            prepitch = v[1]
                    else:
                        delta_pitch = abs(pitch - prepitch)
                        face_info_list.append([delta_pitch, yaw])
                        prepitch = pitch
                    is_updated = True
                    break
                if not v[1] == "none":
                    pitch = float(v[1])
                if not v[2] == "none":
                    yaw = float(v[2])
            else:
                delta_pitch = abs(pitch - prepitch)
                face_info_list.append([delta_pitch, yaw])
                break
            if not is_updated:
                face_info_list.append([0.0, yaw])
            t += self.frame_unit
        return face_info_list

    def get_face_info(self):
        '''
        顔向きに関する情報(デルタピッチ, ヨー)を参加者それぞれで算出
        @return face_infoA(list): 顔向き情報A
        @return face_infoB(list): 顔向き情報B
        '''
        dpitch_list = []
        yaw_list = []
        face_listA = []
        face_listB = []
        for t, f_id, p, y in zip(self.data["Time"], self.data[" faceindex"], self.data[" face_pitch"], self.data[" face_yaw"]):
            time = self.set_time(t) - self.my_time
            if self.start_time <= time and time <= self.end_time:
                yaw = "none"
                pitch = p
                if not y == "none": # yaw (The relative angle with Sota)
                    yaw = abs(float(y) - 22.0)
                if not p == "none":
                    pitch = float(p)
                if f_id == self.Aid:
                    face_listA.append([time - self.start_time, pitch, yaw])
                elif f_id == self.Bid:
                    face_listB.append([time - self.start_time, pitch, yaw])
        face_infoA = self.calculate_face_info(face_listA, "A")
        face_infoB = self.calculate_face_info(face_listB, "B")
        return face_infoA, face_infoB

if __name__ == '__main__':
    """
    kinect_dir = sys.argv[1]
    label_dir = sys.argv[2]
    # 複数のファイルを処理する場合
    f = open('../files.conf', 'r')
    reader = csv.reader(f)
    header = next(reader)
    d = timedelta(0)
    for row in reader:
        kinect_setting = kinect_dir + "/" + row[1] # KINECTのsettingファイルパス
        act = label_dir + "/" + row[2] # Dialog Actのログファイルパス
        ipath = kinect_dir + "/" + row[0] # KINECT情報のログファイルパス
        print kinect_setting
        print act
        print ipath
        TK = TimeKeeper(kinect_setting, act)
        MK = MakeKinectFeatures(TK=TK, INPUT=ipath)
        print "== A:ID =="
        print MK.Aid
        print "== B:ID =="
        print MK.Bid
        print "== START =="
        print MK.start_time
        print "== END =="
        print MK.end_time
        print "== OUT =="
        print MK.out_path
        print "== DURATION =="
        print MK.duration
        d += MK.duration
        print "****************"
        MK.make_features(SWAY=True, FACE=True)
    f.close()
    print "*** Overall conversation time ***"
    print d
    """
    dir = glob('../../*6*')
    #print(len(dir))
    directory=[]
    for i in dir:
        if i[-3] == "6":
            directory.append(i)
    #print(directory)
    for i in directory:
        number = glob(i+"/*")
        #print(number[0])
        for num in number:
            setting_file = glob(num+"/*a.txt")[0]
            act_file = glob(num+"/*[!A].csv")[0]
            kinect_file = glob(num+"/*A.csv")[0]
            # １つのファイルを処理する場合
            kinect_setting = setting_file # KINECTのsettingファイルパス
            act = act_file # Dialog Actのログファイルパス
            TK = TimeKeeper(kinect_setting, act)
            ipath = kinect_file # KINECT情報のログファイルパス
            MK = MakeKinectFeatures(TK=TK, INPUT=ipath)
            print "== A:ID =="
            print MK.Aid
            print "== B:ID =="
            print MK.Bid
            print "== START =="
            print MK.start_time
            print "== END =="
            print MK.end_time
            print "== OUT =="
            print MK.out_path
            print "== DURATION =="
            print MK.duration
            print "****************"
            MK.make_features(SWAY=True, FACE=True)
