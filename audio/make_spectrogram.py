#!/usr/bin/python3
# -*- coding: utf-8 -*-

import numpy as np
import wave
import sys,time
import cv2
import argparse
from glob import glob
import warnings
warnings.filterwarnings('ignore', category=FutureWarning)

# ファイルパスもしくは波形データ（数値）を受け取り、その波形のスペクトログラムを計算する
# スペクトログラムはself.img_arrayに格納される
#
#

class Generator:

    def __init__(self, fs, frame_size, frame_shift, chunk_size):
        self.fs = fs
        self.frame_size = frame_size
        self.frame_shift = frame_shift
        self.chunk_size = chunk_size
        self.win = np.hanning(frame_size)
        self.img_array = []
        self.grayscale = []
        self.start_frame = None
        self.end_frame = None

    def fromNumData(self, num_data):

        # for i in range(len(num_data)):	## 高域強調
        #     num_data[i] = num_data[i] - 0.97 * num_data[i-1]

        frame_start = 0
        frame_end = self.frame_size
        chunk = num_data[frame_start : frame_end]
        img_array = []

        while len(chunk) >= self.frame_size:
            chunk = chunk * self.win
            chunk = np.hstack ([chunk, np.zeros((self.chunk_size-self.frame_size))])
            if chunk.shape[0] != self.chunk_size:
                break
            else:
                # normalized, windowed frequencies in data chunk
                spec = np.fft.rfft(chunk) / self.chunk_size
                # get magnitude
                psd = abs(spec) + 1e-40
                # convert to dB scale
                #print(np.shape(psd))
                #psd = np.array(psd) + 0.00001
                psd = 20 * np.log10(psd)
                psd[psd == -np.inf] = 0
                psd[psd == np.inf] = 0
                #else: psd = 0 * np.array(psd)
                psd = np.asarray([psd])

                if img_array == []:
                    img_array = psd
                elif img_array.shape == (self.chunk_size,):
                    img_array = np.asarray([img_array])
                    img_array = np.r_[img_array, psd]
                else:
                    img_array = np.r_[img_array, psd]


            frame_start = frame_start + self.frame_shift
            frame_end = frame_end + self.frame_shift
            chunk = num_data[frame_start: frame_end]

        self.img_array = img_array

        self.grayscale = (img_array - np.min(img_array)) / (np.max(img_array) - np.min(img_array)) * 255

    def start_time2frame(self, start_time):
        self.start_frame = int(10 * start_time / (self.frame_shift * 1000 / self.fs) + 1)	##はじめに10かけているのは、qaのinputで100が1秒という風に合わせているから

    def end_time2frame(self, end_time):
        self.end_frame = int(10 * end_time / (self.frame_shift * 1000 / self.fs) - (self.frame_size * 1000 / self.fs)/(self.frame_shift * 1000 / self.fs))

    def fromFilePath(self, path):
        wf = wave.open(path, "rb")
        data = wf.readframes(wf.getnframes())
        num_data = np.fromstring(data, dtype = np.int16)
        wf.close()

        self.fromNumData(num_data)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', '-d', type=str, default='/mnt/aoni02/katayama/dataset/DATA2019/wav/*wav',
                        help='specify the conversaton folder PATH')
    parser.add_argument('--out', '-o', type=str, default='/mnt/aoni02/katayama/dataset/DATA2019/spectrogram/',
                        help='specify the label output folder PATH')

    print('Extaction Folder : {}'.format(args.dir))
    print('Output Folder : {}'.format(args.out))
    directory = glob(args.dir)
    output = args.out
    files = sorted(glob(directory))

    for i in range(0,len(files),2):
        start = time.time()
        output = output + files[i].split('/')[-1].split('.')[0]
        g = Generator(16000,800,160,1024)
        g.fromFilePath(files[i])
        cv2.imwrite(output+"_A.png",g.grayscale)
        g = Generator(16000,800,160,1024)
        g.fromFilePath(files[i+1])
        cv2.imwrite(output+"_B.png",g.grayscale)
        print('It took about',time.time()-start,'seconds')
        print("Generated >>",output)



