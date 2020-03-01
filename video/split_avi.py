#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
AVI形式の動画ファイルを指定された開始時刻と
動画の時間を基に切り出して吐き出す
(出力はMP4形式推奨)
"""
__author__ = "Hayato Katayama"
__date__    = "20190304"

import subprocess
import sys
import os
import logging
import glob
import argparse
sys.path.append('..')

from util.time_keeper import TimeKeeper




def split_video(INPUT="", OUTPUT="", START="0.0", DURATION="0.0"):
    if INPUT == "" or OUTPUT == "" or DURATION == "0.0":
        logging.exception("*** Cutting the video :: Argument setting incorrect ***")
    else:
        command = "ffmpeg -y -ss " + START + " -i " + INPUT + " -t " + DURATION + " -r 10 " + OUTPUT
        #command = "ffmpeg -ss " + START + " -i " + INPUT + " -t " + DURATION + " -r 10 -c:v copy " + OUTPUT
        print("Command >> {}".format(command))
        subprocess.run(command, shell=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', '-i', type=str, default='/mnt/aoni02/katayama/dataset/RawDATA/',
                        help='specify the conversaton folder PATH')
    parser.add_argument('--out', '-o', type=str, default='/mnt/aoni02/katayama/dataset/DATA2019/mp4/',
                        help='specify the label output folder PATH')
    args = parser.parse_args()
    print('Extaction Folder : {}'.format(args.dir))
    print('Output Folder : {}'.format(args.out))
    directory = os.path.join(args.dir,'*')
    output = args.out
    if not os.path.isdir(output):
        os.mkdir(output)

    folders = sorted(glob.glob(directory))
    for dir in folders:
        files = sorted(glob.glob(os.path.join(dir, '*')))
        for file in files:
            act_file = glob.glob(file + "/*[!A].csv")[0]
            movie_file = glob.glob(file + "/*.avi")[0]

            TK = TimeKeeper(act_file)
            movie_start = TK.get_diff_movie(movie_file)

            output_file = os.path.join(output, TK.recording_datetime + ".mp4")
            split_video(INPUT=movie_file, OUTPUT=output_file, START=str(movie_start), DURATION=str(TK.duration_sec))

            print("Output >> {}".format(output_file))
