#!/bin/bash

# Raw data のpath
#in_path=/Volumes/Samsung_T5/prj-woz/data
in_path=/Users/hayato/Desktop/data_sample0229 #ここは適宜指定してください
raw_path="$in_path/raw"

# openface のmodels のpath
model_path=/Users/hayato/openface/models #ここは適宜指定してください

source activate py2
#ラベルの作成
out_path="$in_path/label"
cd ./label
python generate_label.py -i $raw_path -o $out_path
#ラベルの作成
out_path="$in_path/decode"
cd ../label
python generate_speechrecognition.py -i $raw_path -o $out_path
#VADの作成
cd ../audio
out_path="$in_path/vad"
python vad_label.py -i $raw_path -o $out_path

#python2 >> python3
source activate py3.5
#wavの作成
cd ../audio
out_path="$in_path/wav"
python split_pcm.py -i $raw_path -o $out_path

#目線動画の作成
cd ../video
out_path="$in_path/mp4"
python split_avi.py -i $raw_path -o $out_path

#画像の切り出し，顔，目画像も
cd ../video
raw_path="$in_path/mp4"
out_path="$in_path/img"
python split_eyeimage.py -i $raw_path -o $out_path -m $model_path

#LLD の抽出
cd ../audio
raw_path="$in_path/wav"
out_path="$in_path/lld"
python extract_lld.py -i $raw_path -o $out_path

# 全ての特徴量結合
cd ../util
out_path="$in_path/feature"
python feature_extractor.py -i $in_path -o $out_path

echo finish!
