#!/usr/bin/python3
# -*- coding: utf-8 -*-
__author__ = "Hayato Katayama"
__date__    = "20190304"
"""
python3
目画像 >> 視線ラベルの推定
"""
import glob
import cv2, os
import pandas as pd
import keras
from keras.models import load_model
import argparse

def predict_gaze(INPUT_FILES,model):
    """
    @param 1対話分の画像
    return 各画像の予測ラベル(正解ラベル)
    """
    label = []
    for file in INPUT_FILES:
        img = cv2.imread(file, 0).reshape(1, 32, 96, 1)
        prob = model.predict(img / 255.0)
        prob = 1 if prob[0] > 0.5 else 0
        label.append(prob)
    return label


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', '-i', type=str, default='/mnt/aoni02/katayama/dataset/DATA2019/eye',
                        help='specify the conversaton folder PATH')
    parser.add_argument('--out', '-o', type=str, default='/mnt/aoni02/katayama/dataset/DATA2019/gaze/',
                        help='specify the output folder PATH')
    parser.add_argument('--model', '-m', type=str,
                        default='/mnt/aoni02/katayama/short_project/proken2018_B/target/gazemodel_128.h5',
                        help='specify the gaze model PATH')
    args = parser.parse_args()
    output = args.out
    if not os.path.isdir(output):
        os.mkdir(output)

    print('Extaction Folder : {}'.format(args.dir))
    directory = args.dir
    folders = sorted(glob.glob(os.path.join(directory,'*')))

    model = load_model(args.model)
    for dir in folders:
        files = sorted(glob.glob(os.path.join(dir,'*png')))
        label = predict_gaze(files,model=model)
        df = pd.DataFrame({'path': files, 'gaze': label})
        path = dir.replace('eye', 'gaze')
        OUTPUT = path + '.gaze.csv'
        df.to_csv(OUTPUT, index=False)
        print('Generated>>',OUTPUT)
