#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ELAN用の音声ファイルを作成(soxを使用)
"""
__author__ = "Yuto Akagawa"
__date__    = "20170801"

from argparse import ArgumentParser
import commands
import sys
import logging
from glob import glob


def mix_video(s_wav="",a_wav="", b_wav="", out_wav=""):
    if a_wav == "" or b_wav == "" :
        logging.exception("*** Setting the A and B wav files :: Argument setting incorrect ***")
    else:
        command = "sox -m " + s_wav + " " + a_wav + " " + b_wav + " " + out_wav
        print("Command >> {}".format(command))
        commands.getoutput(command)

if __name__ ==  "__main__" :
    files = glob("../../ELAN_data/elan_wav/20180629*wav")
    print(len(files))
    for i in range(0,len(files),3):
        out_wav = "../../dataset/mixwav/" + files[i].split("/")[-1].replace("A","out")
        mix_video(files[i],files[i+1],files[i+2],out_wav)
        print("mixed wav files ... >> ",out_wav)
