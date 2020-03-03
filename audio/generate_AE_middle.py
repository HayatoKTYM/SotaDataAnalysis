""""
python3
.wav から　スペクトログラムを生成し，AEの中間層出力を得るプログラム
フレームレートが20fpsであることに注意が必要
"""
import wave
import numpy as np
import torch
import os
import glob
import argparse
import torch
import sflib.speech.feature.autoencoder_pytorch.base as base
import sflib.sound.sigproc.spec_image as spec_image

generator = spec_image.SpectrogramImageGenerator() #spec生成オブジェクト
tr0006_18 = base.load(18, 'csj_0006', 'CSJ0006', map_location='cpu') #AE-model
ae2 = tr0006_18.autoencoder

def generate_spec(f,output):
    wf = wave.open(f)
    x = np.frombuffer(wf.readframes(wf.getnframes()), np.int16)

    generator = spec_image.SpectrogramImageGenerator()
    #spectrogramの作成
    result = generator.input_wave(x)
    print(len(result))
    power, feature = generate_feature(result)

    name = f.split('/')[-1].replace('.wav','.npy')
    np.save(os.path.join(output,name),feature)
    np.save(os.path.join(output.replace('/spec','/power'),name),power)

def generate_feature(image):
    power = []
    feature = []
    for i in range(len(image)):
        image_in = image[i].reshape(1, 512, 10)
        image_in = torch.tensor(image_in)
        # 中間層出力
        x, l2 = ae2.encode(image_in)

        power.append(l2[0].detach().data.numpy())
        feature.append(x[0].detach().data.numpy())
    return power,feature

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', '-i', type=str, default='/mnt/aoni02/katayama/dataset/DATA2019/wav',
                        help='specify the wav folder PATH')
    parser.add_argument('--out', '-o', type=str, default='/mnt/aoni02/katayama/dataset/DATA2019/spec/',
                       help='specify the label output folder PATH')
    args = parser.parse_args()
    print('Extaction Folder : {}'.format(args.dir))
    output = args.out
    if not os.path.isdir(output):
        os.mkdir(output)
        os.mkdir(output.replace('/spec','/power'))

    wav_files = sorted(glob.glob(os.path.join(args.dir,'*.wav')))
    for f in wav_files:
        generate_spec(f,output)
