#!/bin/bash

# コンフィグファイル 
CONFIG=./emobase2010_csv_lld.conf

# 元データの格納場所
DATADIR=$HOME/Desktop/0131

# CSVファイルの保存先
CSVDIR=$HOME/Desktop/0131

for TARGET in `ls ${DATADIR}/*.wav`; do
  FILEBASE=`basename ${TARGET} | sed 's/\.[^\.]*$//'`
  OUTPUT="${CSVDIR}/${FILEBASE}.audio.csv"
  bash $HOME/Downloads/openSMILE-2.3.0/SMILExtract -C ${CONFIG} -I ${TARGET} -O ${OUTPUT} 
done
