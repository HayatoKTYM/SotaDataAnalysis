# -*- coding: utf-8 -*-

"""
mfccファイルの中身を確認する
"""
__author__ = "Yuto Akagawa"
__date__    = "20170801"

import os
import os.path
import csv
import sys
import struct
import logging
import numpy as np


def print_mfcc(mfcc_path, dimension):
    mfccfile = mfcc_path
    dim = int(dimension)
    mfcc = []

    f = open(mfccfile, "rb")
    while True:
        b = f.read(4)
        if b == "": break;
        val = struct.unpack("f", b)[0]
        mfcc.append(val)
    f.close()
    mfcc = np.array(mfcc)
    numframe = len(mfcc) / dim

    if numframe * dim != len(mfcc):
        error_log = "#mfcc:%d #frame:%d m:%d" % (len(mfcc), numframe, dim)
        logging.exception("*** Print MFCC :: " + error_log + " ***")
        sys.exit(1)

    mfcc = mfcc.reshape(numframe, dim)
    mfcc_data = []
    for i in range(len(mfcc)):
        txt = ",".join("%.5f" % x for x in mfcc[i,]) 
        t = txt.split(",")
        mfcc_data.append(t)
    return mfcc_data

if __name__ == '__main__':
    print print_mfcc(sys.argv[1], sys.argv[2])
