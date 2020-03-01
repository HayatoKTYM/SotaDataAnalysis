#!/usr/bin/python3
# -*- coding: utf-8 -*-

__author__ = "Hayato Katayama"
__date__    = "20190304"
"""
python3
mp4 から 画像を切り出すプログラム
画像 >> 顔画像(96,96) >> 目画像(32,96)
"""
import cv2, os, glob
import subprocess
import openface
import numpy as np
import argparse

def split_eyeimage(movie_file,out,align):
    """
    動画を読み込んで画像を切り出す(一応保存)
    画像から顔を検出して切り出す(一応保存)
    目の部分を切り取る(要保存)

    @param: movie_file (.mp4)
    動画(mp4)を画像(png)に変換したものを保存する
    同directory内のfaceフォルダに顔画像を保存する(96*96)
    同directory内のeyeフォルダに顔画像を保存する(96*32)

    """
    #movie -> image
    path = os.path.join(out,movie_file.split("/")[-1].split(".")[0])

    split_png(movie_file,path)
    #image -> face & eye image

    facepath = path.replace('img', 'face', 1)
    if not os.path.exists(facepath):
        os.mkdir(facepath)
    eyepath = path.replace('img', 'eye', 1)
    if not os.path.exists(eyepath):
        os.mkdir(eyepath)

    for f in sorted(glob.glob(os.path.join(path,'*png'))):
        face, eye = getRep(f,align=align)
        cv2.imwrite(f.replace('img', 'face'), face)
        cv2.imwrite(f.replace('img', 'eye'), eye)


# movie >> image
def split_png(f,out):
    """
    @param movie path
    return save path
    """

    if not os.path.exists(out):
        os.mkdir(out)

    command = "ffmpeg -i " + f + " -ss 0 -r 10 -f image2 " + out + "/%05d.png"  # 0秒からフレームレート10でpngとして取り出す
    subprocess.run(command, shell=True)
    print(command)
    return 1

black_face = np.zeros(96 * 96).reshape(96, 96, 1)
black_eye = np.zeros(32 * 96).reshape(32, 96, 1)

def getRep(imgPath,align):
    """
    @param path
    return face image & eye image
    """
    bgrImg = cv2.imread(imgPath)
    if bgrImg is None:
        raise Exception("Unable to load image: {}".format(imgPath))
    rgbImg = cv2.cvtColor(bgrImg, cv2.COLOR_BGR2RGB)
    bb = align.getLargestFaceBoundingBox(rgbImg)

    if bb is None:
        return black_face, black_eye

    landmarks = align.findLandmarks(rgbImg, bb)
    landmarks_np = np.array(landmarks, dtype=np.float32)
    max_pt = np.max(landmarks_np, axis=0)
    min_pt = np.min(landmarks_np, axis=0)
    norm_landmarks = (landmarks_np - min_pt) / (max_pt - min_pt)  # 正規化
    norm_landmarks = norm_landmarks.reshape(136).tolist()
    alignedFace = align.align(96, rgbImg, bb, landmarkIndices=openface.AlignDlib.OUTER_EYES_AND_NOSE)  # 正規化,顔切り出し

    gray_image = cv2.cvtColor(alignedFace, cv2.COLOR_BGR2GRAY)  # グレースケール化
    hist_eq = cv2.equalizeHist(gray_image)  # ヒストグラム平坦化
    eye_image = hist_eq[:32, :]
    return hist_eq, eye_image

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', '-i', type=str, default='/mnt/aoni02/katayama/dataset/DATA2019/mp4',
                        help='specify the mp4 folder PATH')
    parser.add_argument('--model', '-m', type=str, default='/mnt/aoni02/katayama/openface/models',
                        help='specify the openface model PATH')
    parser.add_argument('--out', '-o', type=str, default='/mnt/aoni02/katayama/dataset/DATA2019/img/',
                       help='specify the label output folder PATH')
    args = parser.parse_args()
    print('Extaction Folder : {}'.format(args.dir))
    output = args.out
    if not os.path.isdir(output):
        os.mkdir(output)
        os.mkdir(output.replace('/img','/face'))
        os.mkdir(output.replace('/img','/eye'))

    modelDir = os.path.join(args.model)
    dlibModelDir = os.path.join(modelDir, 'dlib')
    openfaceModelDir = os.path.join(modelDir, 'openface')
    align = openface.AlignDlib(os.path.join(dlibModelDir, "shape_predictor_68_face_landmarks.dat"))

    mp4files = sorted(glob.glob(os.path.join(args.dir, '*mp4')))
    for f in mp4files:
        split_eyeimage(f, output,align=align)
