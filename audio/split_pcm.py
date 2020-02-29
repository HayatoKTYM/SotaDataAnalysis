# -*- coding: utf-8 -*-
"""
python3.5
音声ファイルの切り出し
pcm -> wav
"""

import subprocess
import sys
import os
import argparse
from glob import glob

sys.path.append('../')
from util.time_keeper import TimeKeeper

########################
# config
SAMPLING_RATE = 16000
CH = 1
BITS = 16
ch2spkr = {"ch1": "A", "ch2": "B"}


def split_pcm(input_file, output_file, start, duration):
    cmd = "sox -r {} -c {} -b {} -e signed-integer -t raw {} {} trim {} {}".format(
        SAMPLING_RATE, CH, BITS, input_file, output_file, start, duration)
    print(cmd)
    try:
        res = subprocess.run(cmd, shell=True)
    except Exception as e:
        print("Runtime Error.")
        print(e)

def mix_wav(wav_s,wav_a,wav_b,output,CH=3):
    """A,B,Sys の音声を混ぜる [基本ELAN用]

    Arguments:
        wav_s {[str]} -- sys wav
        wav_a {[str]} -- userA wav
        wa_b {[str]} -- userB wav
    """
    cmd = "sox -m {} {} {} -c {} {}".format(
        wav_s, wav_a, wav_b, CH, output
    )
    print(cmd)
    try:
        res = subprocess.run(cmd, shell=True)
    except Exception as e:
        print("Runtime Error.")
        print(e)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', '-i', type=str, default='/mnt/aoni02/katayama/dataset/RawDATA',
                        help='specify the conversation folder PATH')
    parser.add_argument('--out', '-o', type=str, default='/mnt/aoni02/katayama/dataset/DATA2019/wav/',
                        help='specify the output folder PATH')
    parser.add_argument('--mix', '-m', type=str, default=True,
                        help='mix 3 wav or not')
    parser.add_argument('--ch', '-c', type=str, default=1,
                        help='mono(1) or streo(3)')
    args = parser.parse_args()
    print('Extaction Folder : {}'.format(args.dir))
    print('Output Folder : {}'.format(args.out))
    directory = sorted(glob(os.path.join(args.dir,'*')))
    output = args.out
    if not os.path.isdir(output):
        os.mkdir(output)
        os.mkdir(output.replace('wav','sys_wav',1))
        os.mkdir(output.replace('wav','mix_wav',1))

    for i in directory:
        number = sorted(glob(i + "/*"))
        for num in number:
            act_file = glob(num + "/*[!A].csv")[0]
            pcm_file = glob(num + "/000*")
            vad_file = pcm_file[0] + '/vad.txt'
            pcm_a = pcm_file[0] + "/ch1.pcm"
            pcm_b = pcm_file[0] + "/ch2.pcm"
            pcm_s = pcm_file[0] + "/ch0.pcm"
            #時間同期を取るclass(TimeKeeper)
            TK = TimeKeeper(act_file)
            wav_start = TK.get_diff_sound(vad_file)

            #出力PATHの指定 & 変換の実行
            out_file_A = os.path.join(output, TK.recording_datetime + ".A" + ".wav")
            split_pcm(pcm_a, out_file_A, wav_start, TK.duration_sec)
            out_file_B = os.path.join(output, TK.recording_datetime + ".B" + ".wav")
            split_pcm(pcm_b, out_file_B, wav_start, TK.duration_sec)
            out_file_S = os.path.join(output.replace('wav','sys_wav',1) , TK.recording_datetime + ".S" + ".wav")
            split_pcm(pcm_s, out_file_S, wav_start, TK.duration_sec)
            print("Genetared >> ", out_file_S)

            if args.mix:
                output_mix = os.path.join(output.replace('wav','mix_wav',1), TK.recording_datetime + ".mix" + ".wav")
                mix_wav(wav_s=out_file_S, wav_a=out_file_A, wav_b=out_file_B, output=output_mix,CH=args.ch)

