# -*- coding: utf-8 -*-
"""
コンフィグファイルを渡すとファイル名の組みを返すイテレータ
"""

import csv

class FileReader(object):
    """
    コンフィグ読み込み
    """
    def __init__(self, config_file):
        '''
        コンストラクタ
        :param config_file: ファイルの組みが書かれたコンフィグ
        '''
        self.conf = config_file

    def __iter__(self):
        labels = []
        self.files = []
        with open(self.conf, 'r') as fi:
            for i, line in enumerate(csv.reader(fi)):
                if i == 0:
                    labels = line
                else:
                    contents = {}
                    for i, l in enumerate(labels):
                        contents[l] = line[i]
                    self.files.append(contents)
        return self

    def next(self):
        # 全部出力したら終了
        if self.files == []:
            raise StopIteration

        return self.files.pop(0)

if __name__ == '__main__':
    fr = FileReader('../files.conf')
    for i in fr:
        print(i)
