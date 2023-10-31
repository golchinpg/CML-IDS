#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import time
import datetime
import logging

from sklearn.preprocessing import minmax_scale
from sklearn.feature_selection import mutual_info_classif
from sklearn.feature_selection import chi2
from sklearn.feature_selection import f_classif
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance


from .dataset_processing import DatasetPreprocess

class FeatureSelection:
    """Select the most relevant features.
    """

    def __init__(self) -> None:
        print("Start building RF classifier for DP-IDS.")

    def compute_feature_importances(self, dataset_path, feature_scores_save_path, logging_path, logging_info, repeat_time=1):
        """ Compute the most relavant features.

        Parameters
        ----------
        dataset_path: str
            Path for training dataset.
        feature_scores_save_path: str
            Path for saving computation score of feature importance
        logging_path: str, default: None
            Path for logging.
        logging_info: str
            Information for the logging
        repeat_time: int, default: 1
            The computation rounds for the feature score.

        Returns
        -------
        DataFrame:
            Feature scores.
        """
        start_computing = time.time()
        logging.basicConfig(
            filename=logging_path, filemode='a', level=logging.INFO)
        logging.info(
            "**************************************************************************************")
        logging.info(
            "**************************************************************************************")
        logging.info(logging_info)
        logging.info(
            f"The computation of feature importance procedure starts at {time.asctime(time.localtime(start_computing))}")

        # read the preprocessed data
        dataProc = DatasetPreprocess()
        X_train, X_val, y_train, y_val, X_tot, y_tot = dataProc.split_dataset(
            dataset_path=dataset_path, test_size=0.3)

        features = X_train.columns
        features_num = len(features)

        # 1: Mutual Information
        mutual_info = np.zeros(features_num)
        for i in range(repeat_time):
            # record logging
            start_timestamp = time.time()
            logging.info(
                f"Mutual information: {i+1} starts {time.asctime(time.localtime(start_timestamp))}")
            mutual_info = mutual_info + \
                minmax_scale(mutual_info_classif(X_train, y_train))
            # record logging
            end_timestamp = time.time()
            logging.info(
                f"Mutual information: {i+1} ends {time.asctime(time.localtime(end_timestamp))}")
            logging.info(
                f"Mutual information: {i+1} takes time {datetime.timedelta(seconds=(end_timestamp - start_timestamp))} ")
        mutual_info = mutual_info / repeat_time
        mutual_info_serie = pd.Series(
            mutual_info, index=features, name="mutual_information_score")

        # 2: chi2
        # error: input feature values should be non-negative
        # chi2_info = chi2(X_train, y_train)
        # chi2_info = minmax_scale(chi2_info)
        # chi2_info_serie = pd.Series(
        #     chi2_info, index=features, name="chi2_score")

        # 3: tree-based impurity importance (Extemely Randomized Trees)
        clf = ExtraTreesClassifier(n_estimators=100, max_depth=10, n_jobs=-1)
        impurity_info = np.zeros(features_num)
        for i in range(repeat_time):
            # record logging
            start_timestamp = time.time()
            logging.info(
                f"Impurity importance: {i+1} starts {time.asctime(time.localtime(start_timestamp))}")
            clf = clf.fit(X_train, y_train)
            impurity_info = impurity_info + \
                minmax_scale(clf.feature_importances_)
            # record logging
            end_timestamp = time.time()
            logging.info(
                f"Impurity importance: {i+1} ends {time.asctime(time.localtime(end_timestamp))}")
            logging.info(
                f"Impurity importance: {i+1} takes time {datetime.timedelta(seconds=(end_timestamp - start_timestamp))}")
        impurity_info = impurity_info / repeat_time
        impurity_info_serie = pd.Series(
            impurity_info, index=features, name="impurity_score")

        # 4: RF-based feature importance
        # 5: permutation-based feature importance
        rf = RandomForestClassifier(n_estimators=100, max_depth=10, n_jobs=-1)
        rf_importance = np.zeros(features_num)
        permutation_info = np.zeros(features_num)
        for i in range(repeat_time):
            # record logging
            start_timestamp = time.time()
            logging.info(
                f"Random forest importance: {i+1} starts {time.asctime(time.localtime(start_timestamp))}")
            rf = rf.fit(X_train, y_train)
            rf_importance = rf_importance + \
                minmax_scale(rf.feature_importances_)
            # record logging
            end_timestamp = time.time()
            logging.info(
                f"Random forest importance: {i+1} ends {time.asctime(time.localtime(end_timestamp))}")
            logging.info(
                f"Random forest importance: {i+1} takes time {datetime.timedelta(seconds=(end_timestamp - start_timestamp))}")
            # record logging
            start_timestamp = time.time()
            logging.info(
                f"Permutation importance: {i+1} starts {time.asctime(time.localtime(start_timestamp))}")
            permutation_info = permutation_info + \
                minmax_scale(permutation_importance(
                    rf, X_val, y_val, n_repeats=5).importances_mean)
            # record logging:
            end_timestamp = time.time()
            logging.info(
                f"Permutation importance: {i+1} ends {time.asctime(time.localtime(end_timestamp))}")
            logging.info(
                f"Permutation importance: {i+1} takes time {datetime.timedelta(seconds=(end_timestamp - start_timestamp))}")
        rf_importance = rf_importance / repeat_time
        permutation_info = permutation_info / repeat_time
        rf_importance_serie = pd.Series(
            rf_importance, index=features, name="rf_based_score")
        permutation_info_serie = pd.Series(
            permutation_info, index=features, name="permutation_score")

        # final importance score: sum of the scores in terms of different metrics
        final_score = minmax_scale(
            mutual_info + impurity_info + rf_importance + permutation_info)
        final_score_serie = pd.Series(
            final_score, index=features, name="final_importance_score")

        # concatenate feature importance series to dataframe
        df = pd.concat([mutual_info_serie, impurity_info_serie,
                        rf_importance_serie, permutation_info_serie, final_score_serie], axis=1)

        df = df.sort_values(
            by=["final_importance_score"], ascending=False)

        end_computing = time.time()
        logging.info(
            f"The computation of feature importance procedure ends at {time.asctime(time.localtime(end_computing))}")
        logging.info(
            f"The computation of feature importance procedure takes time {datetime.timedelta(seconds=(end_computing - start_computing))}")
        logging.info(f"The final order of features: {df.index}\n\n\n")
        # set index=False to avoid reading the first column as Unnamed: 0
        df.to_csv(feature_scores_save_path, index=True)
        return df

    def refine_dataset(self, feature_scores_path, dataset_path, dataset_relevant_save_path, relevant_features_num):
        """Build the training dataset with the relevant features. 

        Parameters
        ----------
        feature_scores_path: str
            Path of feature scores.
        dataset_path: str
            Path of training dataset with full features.
        dataset_relevant_save_path: str
            Path of saving dataset with relevant features
        relevant_features_num: int
            Number of extracted relevant features.
        """
        # get the relevant features
        feature_scores_df = pd.read_csv(feature_scores_path, index_col=0)
        relevant_features = feature_scores_df.iloc[:relevant_features_num, :]

        # read the preprocessed dataset with full compatibal features
        df = pd.read_csv(dataset_path)
        # save the dataset with the relevant features
        relevant_features_index = relevant_features.index.tolist()
        df = df[relevant_features_index + ["Label"]]
        # set index=False to avoid reading the first column as Unnamed: 0
        df.to_csv(dataset_relevant_save_path, index=False)

    def plot_relevant_features(self, feature_scores_path, fig_path, relevant_features_num):
            """Plot the feature scores of the relevant features.

            Parameters
            ----------
            feature_scores_path: str
                Path of feature scores.
            fig_path: str
                Path of saving figures.
            relevant_features_num:
                Number of extrcated relevant features.
            """
            # get the relevant features
            feature_scores_df = pd.read_csv(feature_scores_path, index_col=0)
            relevant_features = feature_scores_df.iloc[:relevant_features_num, :]
            ax = relevant_features.plot(kind="bar", figsize=(
                15, 5), rot=70)
            ax.legend(["Mutual Information Score",
                       "Tree-based Impurity Score",
                       "Random Forest-based Score",
                       "Permutation Score",
                       "Final Score"])
            ax.set_xlabel("Feature Name", fontsize=12)
            ax.set_ylabel("Feature Importance Score", fontsize=12)
            ax.figure.savefig(fig_path, dpi=300, bbox_inches="tight")