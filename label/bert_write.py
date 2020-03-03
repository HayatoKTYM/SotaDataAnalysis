"""
python3
文 >> bert(784dim) に変換するプログラム
bert-as-server を立ち上げておく必要がある．

下のように，sys,A,Bの発話が並んでいる
sys| A| B
----------
 ~ | ~| ~
"""
from bert_serving.client import BertClient
import numpy as np
import pandas as pd
import os

text_list = [
     'こんにちは',
         'おはよう',
             'こんばんは',
                 'お腹すいた',
                     'ご飯食べたい',
                         '明日晴れてると良いな',
                             '明日の天気はどうだろうか',
                                 '雨降ったら嫌やな'
                                 ]

def generate_bert_feature(text_list,output):
    with BertClient(port=5555, port_out=5556) as bc:
        text_vecs = bc.encode(text_list)
        print(text_vecs.shape)
        #np.savetxt('/mnt/aoni02/katayama/text_vecs_chibadai.csv', text_vecs, delimiter=',')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', '-i', type=str, default='/mnt/aoni02/katayama/dataset/DATA2019/decode',
                        help='specify the wav folder PATH')
    parser.add_argument('--out', '-o', type=str, default='/mnt/aoni02/katayama/dataset/DATA2019/bert/',
                       help='specify the label output folder PATH')
    args = parser.parse_args()
    print('Extaction Folder : {}'.format(args.dir))
    output = args.out
    if not os.path.isdir(output):
        os.mkdir(output)
    files = sorted(glob.glob(os.path.join(args.dir,'*csv')))
    for f in files:
        df = pd.read_csv(f)
        text_list = df.values.reshape(-1).tolist()
        output = os.path.join(output,f.split('/')[-1].replace('.csv','.npy'))
        generate_bert_feature(text_list,output)
        print('Generated>>',output)