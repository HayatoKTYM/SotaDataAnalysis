# -*- coding: utf-8 -*-
"""
音声ファイルの切り出し
pcm -> wav
"""

from __future__ import print_function
from argparse import ArgumentParser
import subprocess
import sys

sys.path.append('..')

from util.time_keeper import TimeKeeper

from glob import glob
########################
# config
SAMPLING_RATE = 16000
CH = 1
BITS = 16
ch2spkr = {"ch0": "S" ,"ch1": "A", "ch2": "B"}
########################

def split_pcm(input_file, output_file, start, duration):
    cmd = "sox -r {} -c {} -b {} -e signed-integer -t raw {} {} trim {} {}".format(
        SAMPLING_RATE, CH, BITS, input_file, output_file, start, duration)
    try:
        res = subprocess.check_call(cmd, shell=True)
    except:
        print("Runtime Error.")

if __name__ == '__main__':
    """
    parser = ArgumentParser()

    parser.add_argument("-i", "--input", type=str, metavar="FILE", required=True,
                        help="input file")
    parser.add_argument("-o", "--outdir", type=str, metavar="DIRECTORY", required=False,
                        help="output directory", default=".")
    parser.add_argument("-k", "--kinect", type=str, metavar="FILE", required=True,
                        help="KINECT config file")
    parser.add_argument("-a", "--act", type=str, metavar="FILE", required=True,
                        help="action log file")
    args = parser.parse_args()
    """
    directory = glob('../../data/070*')
    print(directory)

    for i in directory:
        number = glob(i+"/*")
        #print(number[0])
        for num in number:
            setting_file = glob(num+"/*a.txt")[0]
            act_file = glob(num+"/*[!A].csv")[0]
            #print(setting_file)
            file_a = glob(num+"/000*")
            #vad_file = file_a[0]+"/vad.txt"
            pcm_s = file_a[0]+"/ch0.pcm"
            #pcm_b = file_a[0]+"/ch2.pcm"
            TK = TimeKeeper(setting_file, act_file)
            #mic_ch = args.input.split("/")[-1].split("_")[-1].split(".")[0]
            out_file = "../../ELAN_data/elan_wav/" + TK.recording_datetime + ".S" + ".wav"
            split_pcm(pcm_s, out_file, TK.start_delta_sec, TK.duration_sec)
            pcm_a = file_a[0] + "/ch1.pcm"
            out_file = "../../ELAN_data/elan_wav/" + TK.recording_datetime + ".A" + ".wav"
            split_pcm(pcm_a, out_file, TK.start_delta_sec, TK.duration_sec)
            pcm_b = file_a[0]+"/ch2.pcm"
            out_file = "../../ELAN_data/elan_wav/" + TK.recording_datetime + ".B"  + ".wav"
            split_pcm(pcm_b, out_file, TK.start_delta_sec, TK.duration_sec)
