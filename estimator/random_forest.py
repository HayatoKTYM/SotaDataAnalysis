# -*- coding: utf-8 -*-
"""
ランダムフォレストによる振る舞い推定
"""

from __future__ import print_function
from argparse import ArgumentParser
from sklearn.model_selection import KFold
from sklearn.ensemble import RandomForestClassifier
import sys
sys.path.append("..")
from util.feature_extractor import FeatureExtractor
from sklearn import neural_network
from sklearn import svm
from sklearn.metrics import classification_report, precision_recall_fscore_support, accuracy_score
from collections import Counter
import numpy as np
import glob


action2id = {
    "None": 0,
    "Active": 1,
    "Passive": 2,
    "Other": 3,
    "Nod": 4,
}

target2id = {
    "A": 0,
    "B": 1,
}

# label2id = {
#     ("None", "A"): 0,
#     ("None", "B"): 1,
#     ("Active", "A"): 2,
#     ("Active", "B"): 3,
#     ("Passive", "A"): 4,
#     ("Passive", "B"): 5,
#     ("Other", "A"): 6,
#     ("Other", "B"): 7,
#     ("Nod", "A"): 8,
#     ("Nod", "B"): 9
#
# }

label2id = {
    ("None", "A"): 0,
    ("None", "B"): 0,
    ("Active", "A"): 1,
    ("Active", "B"): 1,
    ("Passive", "A"): 1,
    ("Passive", "B"): 1,
    ("Other", "A"): 1,
    ("Other", "B"): 1,
    ("Nod", "A"): 1,
    ("Nod", "B"): 1,
    ("Continue", "A"): 2,
    ("Continue", "B"): 2,

}


if __name__ == '__main__':
    parser = ArgumentParser()

    parser.add_argument("-d", "--datadir", type=str, metavar="DIRECTORY", required=False, default='../../dataset/feature',
                        help="feature data directory")

    args = parser.parse_args()

    datafiles = glob.glob("{}/*.csv".format(args.datadir))

    kf = KFold(n_splits=4)
    #kf = KFold(n_splits=5)
    precisions = []
    recalls = []
    f1s = []
    accuracies = []
    for train_idx, test_idx in kf.split(datafiles[1:5]):####
        print(train_idx, test_idx)
        #print(1)
        # training
        train_feature = []
        train_label = []
        for i in train_idx:
            #train_file = datafiles[7+i]
            train_file = datafiles[i+1]
            print(train_file)
            extractor = FeatureExtractor(train_file)
            f_count = 0

            for f_list in extractor:
                #print(f_count)
                f_count += 1
                action = f_list[0]
                target = f_list[1]
                vad = f_list[2:5]
                mfcc_A = f_list[5:41]
                f0_A = f_list[41:44]
                power_A = f_list[44:47]
                mfcc_B = f_list[47:83]
                f0_B = f_list[83:86]
                power_B = f_list[86:89]
                k_delta_A = f_list[89:92]
                k_delta_B = f_list[92:95]
                k_pitch_A = f_list[95]
                k_yaw_A = f_list[96]
                k_pitch_B = f_list[97]
                k_yaw_B = f_list[98]
                # feature = vad + f0_A + f0_B + power_A + power_B
                # feature = mfcc_A + mfcc_B
                feature = f_list[2:]
                train_label.append(label2id[(action, target)])
                train_feature.append(feature)
        X = np.asarray(train_feature, dtype=np.float32)
        X = np.nan_to_num(X)
        Y = np.asarray(train_label)
        print("training start.")
        label_counter = Counter(train_label)
        class_weight = {i:(float(len(train_label)) / label_counter[i]) ** 1.1 for i in sorted(set(train_label))}
        print(label_counter)
        clf = RandomForestClassifier(n_jobs=-1, n_estimators=100, random_state=100,
                                     class_weight=class_weight, max_depth=2)
        #clf = neural_network.MLPClassifier(hidden_layer_sizes=(50,), verbose=True, batch_size=100)
        #clf = svm.SVC()
        if hasattr(clf, "class_weight") and clf.class_weight == class_weight:
            print("class weight = {}".format(class_weight))

        clf.fit(X, Y)
        print("training done.")
        # test
        test_feature = []
        test_label = []
        for i in test_idx:
            #test_file = datafiles[7+i]
            test_file = datafiles[i+1]
            extractor = FeatureExtractor(test_file)
            for f_list in extractor:
                for f_list in extractor:
                    action = f_list[0]
                    target = f_list[1]
                    vad = f_list[2:5]
                    mfcc_A = f_list[5:41]
                    f0_A = f_list[41:44]
                    power_A = f_list[44:47]
                    mfcc_B = f_list[47:83]
                    f0_B = f_list[83:86]
                    power_B = f_list[86:89]
                    k_delta_A = f_list[89:92]
                    k_delta_B = f_list[92:95]
                    k_pitch_A = f_list[95]
                    k_yaw_A = f_list[96]
                    k_pitch_B = f_list[97]
                    k_yaw_B = f_list[98]
                    # feature = vad + f0_A + f0_B + power_A + power_B
                    # feature = mfcc_A + mfcc_B
                    feature = f_list[2:]
                    if action == "Continue": action = "None"  # ContinueをNoneに統合
                    test_label.append(label2id[(action, target)])
                    test_feature.append(feature)
        X = np.asarray(test_feature, dtype=np.float32)
        X = np.nan_to_num(X)

        y_true = np.asarray(test_label)
        y_pred = clf.predict(X)
        y_pred[y_pred==label2id[("Continue", "A")]] = label2id[("None", "A")]  # ContinueをNoneに統合
        y_pred[y_pred==label2id[("Continue", "B")]] = label2id[("None", "B")]  # ContinueをNoneに統合
        report = classification_report(y_true, y_pred)
        print(report)
        precision, recall, f1, support = precision_recall_fscore_support(y_true, y_pred, average='weighted')
        accuracy = accuracy_score(y_true, y_pred)
        precisions.append(precision)
        recalls.append(recall)
        f1s.append(f1)
        accuracies.append(accuracy)
        print("Accuracy: {}".format(accuracy))

    average_precision = np.mean(precisions)
    average_recall = np.mean(recalls)
    average_f1 = np.mean(f1s)
    average_accuracy = np.mean(accuracies)
    print(average_precision, average_recall, average_f1, average_accuracy)
