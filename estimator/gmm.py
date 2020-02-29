# -*- coding: utf-8 -*-
"""
GMMによるイベント検出
異常検知？
"""
from __future__ import print_function
from argparse import ArgumentParser
from sklearn.model_selection import KFold
from sklearn.ensemble import RandomForestClassifier
import sys
sys.path.append("..")

from util.feature_extractor import FeatureExtractor
from sklearn import neural_network
from sklearn import svm, mixture, decomposition, discriminant_analysis
from sklearn.metrics import classification_report, precision_recall_fscore_support, accuracy_score,\
    precision_recall_curve, average_precision_score
from collections import Counter
import numpy as np
import glob
import matplotlib.pyplot as plt


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
    ("Continue", "A"): 1,
    ("Continue", "B"): 1,

}


if __name__ == '__main__':
    parser = ArgumentParser()

    parser.add_argument("-d", "--datadir", type=str, metavar="DIRECTORY", required=False, default='../../dataset/feature',
                        help="feature data directory")

    args = parser.parse_args()

    datafiles = glob.glob("{}/*.csv".format(args.datadir))

    kf = KFold(n_splits=4)
    precisions = []
    recalls = []
    f1s = []
    accuracies = []
    count = 0
    for train_idx, test_idx in kf.split(datafiles[1:5]):
        count += 1
        decomp = decomposition.PCA(n_components=20)
        # decomp = discriminant_analysis.LinearDiscriminantAnalysis(n_components=30)
        print(train_idx, test_idx)
        # training
        train_feature = []
        train_label = []
        triger_feature = []
        triger_label = []
        for i in train_idx:
            train_file = datafiles[1+i]
            extractor = FeatureExtractor(train_file)
            f_count = 0
            for f_list in extractor:
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
                # feature = f0_A + f0_B + power_A + power_B
                feature = f_list[5:89]
                train_label.append(label2id[(action, target)])
                train_feature.append(feature)
                feature_vec = np.asarray(feature, dtype=np.float32)
                if np.sum(np.where(np.isnan(feature_vec))) != 0:
                    print(np.where(np.isnan(feature_vec)))
                    print(feature)
                    import sys
                    sys.exit()
                if label2id[(action, target)] == 1:
                    triger_feature.append(feature)
                    triger_label.append(label2id[(action, target)])
            # X = np.asarray(train_feature, dtype=np.float32)

        X = np.asarray(triger_feature, dtype=np.float32)
        X_ALL = np.asarray(train_feature, dtype=np.float32)
        decomp.fit(X_ALL)
        X = decomp.transform(X)
        # X = np.nan_to_num(X)
        # print(np.where(np.isnan(X)))
        Y = np.asarray(train_label)
        # Y = np.asarray(triger_label)
        print("training start.")
        label_counter = Counter(train_label)
        class_weight = {i:float(len(train_label)) / label_counter[i] for i in sorted(set(train_label))}
        print(label_counter)
        # clf = RandomForestClassifier(n_jobs=-1, n_estimators=100, random_state=100,
        #                              class_weight=class_weight, max_depth=3)
        # clf = neural_network.MLPClassifier(hidden_layer_sizes=(50,), verbose=True, batch_size=100)
        # clf = svm.SVC()
        gmm = mixture.GaussianMixture(n_components=2, covariance_type='full', verbose=1)

        gmm.fit(X)
        print("training done.")
        # test
        test_feature = []
        test_label = []
        for i in test_idx:
            test_file = datafiles[1+i]
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
                    # feature = f0_A + f0_B + power_A + power_B
                    feature = f_list[5:89]
                    if action == "Continue":
                        action = "None"
                    test_label.append(label2id[(action, target)])
                    test_feature.append(feature)
        X = np.asarray(test_feature, dtype=np.float32)
        X = decomp.transform(X)
        proba = gmm.predict_proba(X)
        score = gmm.score_samples(X)
        # print(proba)
        # print(score)
        y_test = np.asarray(test_label, dtype=np.float32)
        # y_test = np.asarray(train_label, dtype=np.float32)
        y_score = score
        precision, recall, th = precision_recall_curve(y_test, y_score)
        # print(th)
        average_precision = average_precision_score(y_test, y_score)

        plt.step(recall, precision, color='b', alpha=0.2,
                 where='post')
        plt.clf()
        # plt.scatter(recall, precision)
        plt.fill_between(recall, precision, step='post', alpha=0.2,
                         color='b')

        plt.xlabel('Recall')
        plt.ylabel('Precision')
        plt.ylim([0.0, 1.05])
        plt.xlim([0.0, 1.0])
        plt.title('2-class Precision-Recall curve: AUC={0:0.2f}'.format(
            average_precision))
        plt.savefig("{}-fold.prcurve.png".format(count))
