import numpy as np

class MakeLabelDataset(object):
    """
    ELAN により作成された アノテーションファイルからラベルを抽出するclass
    """
    def __init__(self, xml_path=''):
        import xml.etree.ElementTree as ET
        # XML file の読み込み
        self.trees = ET.parse(xml_path)
        self.root = self.trees.getroot()
        
    def __call__(self, video_frames, frame_milisec_duration):
        """
        XML File からラベルを抽出する
        param: continued_time 動画自体の時間
        param: frame_milisec_duration 画像1枚あたりのながさ 1fpsなら1000[ms]
        """
        id2time = self.get_time(self.root, frame_milisec_duration)
        StateLabel = [0] * video_frames
        cnt = 0
        pre_start = 0
        for neighbor in self.root.iter('ALIGNABLE_ANNOTATION'):
            
            start = int(id2time[neighbor.attrib['TIME_SLOT_REF1']])
            end = int(id2time[neighbor.attrib['TIME_SLOT_REF2']])
            if pre_start > start:  # pre-startのほうが大きければ、次の注釈層に移動
                cnt += 1
                break
            pre_start = start
            if end > video_frames:
                print('over time')
                break
            for i in range(start, end):
                try:
                    StateLabel[i] = 1
                except:
                    print(start, end, cnt)
        
        from collections import Counter
        print(Counter(StateLabel))
        
        return np.array(StateLabel, dtype=np.int32)
        
    def get_time(self, root, frame_milisec_duration) -> dict:
        """
        ANNOTATION_ID と time の対応を取る函数
        """
        id2time = dict()
        for neighbor in root.iter('TIME_SLOT'):
            id = neighbor.attrib['TIME_SLOT_ID']
            time = neighbor.attrib['TIME_VALUE']
            id2time[id] = int(time) // frame_milisec_duration
        return id2time