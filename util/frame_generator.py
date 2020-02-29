# -*- coding: utf-8 -*-
"""
開始時間と終了時間を与えると `n msec` でフレームを生成するイテレータ
"""

from datetime import timedelta

class FrameGenerator(object):
    """
    フレーム生成
    """
    def __init__(self, start_time, end_time, frame_rate=100):
        '''
        :param start_time: datetime.timedelta
        :param end_time: datetime.timedelta
        :param frame_rate: ms
        '''
        self.start_time = start_time
        self.end_time = end_time
        self.frame_rate = frame_rate
        self.flames = []

    def __iter__(self):
        duration = self.end_time - self.start_time
        n_frame = int(duration.total_seconds() // timedelta(milliseconds=self.frame_rate).total_seconds())
        self.flames = [self.start_time + timedelta(milliseconds=self.frame_rate * i) for i in range(1, n_frame + 1)]
        return self

    def next(self):
        # 全部出力したら終了
        if self.flames == []:
            raise StopIteration

        return self.flames.pop(0)
