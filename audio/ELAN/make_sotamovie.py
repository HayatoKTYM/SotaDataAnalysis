__author__ = "Hayato Katayama"
__date__    = "20181023"

from argparse import ArgumentParser
import commands
import sys
import logging
from glob import glob

def make_video(wav="", movie="", out_wav=""):
    if wav == "" or movie == "" :
        logging.exception("*** Setting the WAV and MOVIE files :: Argument setting incorrect ***")
    else:
        command = "ffmpeg -i "+ movie + " -i "+ wav + " " + out_wav
        print("Command >> {}".format(command))
        commands.getoutput(command)

if __name__ ==  "__main__" :
    wav_files = glob("../../dataset/mixwav/*wav")
    movie_files = glob("../../dataset/mp4/*mp4")
    print(len(wav_files)==len(movie_files))

    for i in range(len(wav_files)):
        out_wav = movie_files[i].split('/')[-1].split('.')[0]

        if out_wav != wav_files[i].split('/')[-1].split('.')[0]:
            print("error")
        out_wav = "../../ELAN_data/SotaMovie/"+out_wav+"_movie.mp4"
        make_video(wav_files[i],movie_files[i],out_wav)
