#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import time
import datetime
import logging
import pickle

from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, plot_confusion_matrix
from sklearn.tree import plot_tree


class DPIDSBuilder:
    """The builder for generating CP-IDS RF classifier.
    """

    def __init__(self) -> None:
        print("Start building RF classifier for DP-IDS.")

    def get_best_estimator(self, cv_results_dir, params, X_train, y_train):
        """Compute the best random forest estimator.

        Parameters
        ----------
        cv_results_dir: str
            Directary of saveing CV results.
        params: dict
            Hyperparameters for the CV.
        X_train: DataFrame (pandas)
            Training dataset without label.
        y_train: DataFrame (pandas)
            Training dataset of the label.

        Returns
        -------
        str:
            CV result path.

        """
        clf = RandomForestClassifier(n_jobs=-1)

        # use grid search to find the best hyperparamters
        grid_search = GridSearchCV(
            estimator=clf, param_grid=params, cv=5, n_jobs=-1, verbose=1, scoring="f1_macro")
        grid_search.fit(X_train, y_train)

        # save the results of each combination
        df = pd.DataFrame(grid_search.cv_results_)
        for param in params.keys():
            cv_results_dir = cv_results_dir + \
                param + '_' + str(params[param])

        cv_results_path = cv_results_dir + ".csv"
        df.to_csv(cv_results_path)

        print("Best score: " + str(grid_search.best_score_))
        print("Best parameters: " + str(grid_search.best_params_))

        # # get the best estimator
        # best_estimator = grid_search.best_estimator_
        # return best_estimator
        
        return cv_results_path
    

    def plot_cv_results(self, cv_results_path, params, fig_name):
        """Plot the CV results.
        
        Parameters
        ----------
        cv_results_path: str
            Path of the cv results.
        params: dict
            Hyperparameters for the CV.        
        fig_name: str
            Name of the CV result figure.
        """

        df = pd.read_csv(cv_results_path, index_col="param_max_depth")
        df["mean_test_score"].plot(style=".-", 
                                title=f"F1-score related to the maximum depth of trees", 
                                xlabel="depth of trees", 
                                ylabel="macro f1-score", 
                                xticks=params["max_depth"], 
                                rot=1)
        fig_save_path = cv_results_path + fig_name
        plt.savefig(fig_save_path)


    def train_rf(self, rf_serialization_path, n_estimators, max_depth, X_train, y_train):
        """Train and save the RF model.
        
        Parameters
        ----------
        rf_serialization_path: str
            Path for saving serialized RF. 
        n_estimators: int
            The number of trees in the RF.
        max_depth: int
            The maximum depth of the tree in the RF.
        X_train: DataFrame (pandas)
            Training dataset without label.
        y_train: DataFrame (pandas)
            Training dataset of the label.
        """
        rf = RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth, n_jobs=-1)
        rf.fit(X_train, y_train)
        self.save_rf(rf_serialization_path, rf)

    def save_rf(self, rf_serialization_path, rf_estimator):
        """Serialize and save the random forest estimator into file.

        Parameters
        ----------
        rf_serialization_path: str
            Path of saving the serialized RF.
        rf_estimator: 
            The RF estimator.
        """
        with open(rf_serialization_path, "wb") as f:
            pickle.dump(rf_estimator, f)
    
    def load_rf(self, rf_serialization_path):
        """Load the RF model.
        
        Parameters
        ----------
        rf_serialization_path: str
            Path of the trained RF. 
        
        Returns
        -------
        RF model
        """
        with open(rf_serialization_path, "rb") as f:
            rf = pickle.load(f)
        return rf
    
    def plot_trees(self, save_path, rf_serialization_path, features):
        """Save the figures of trees.

        Parameters
        ----------
        save_path: str
            Path for saving trees.
        rf_serialization_path:
            Path for random forest estiamtor.
        features: list
            List of the features used for training. 
        """
        # load rf estimator
        rf_estimator = self.load_rf(rf_serialization_path)

        plt.figure(figsize=(95, 25))

        for i in range(len(rf_estimator.estimators_)):
            plot_tree(rf_estimator.estimators_[i],
                      feature_names=features,
                      class_names=['Benign', 'Attack'],
                      filled=True, impurity=True,
                      rounded=True)
            plt.savefig(save_path + "dt_" + str(i + 1) + ".png", dpi=200)

    
    def test(self, rf_serialization_path, dataset_path):
        """Test the performance of RF model.
        
        Parameters
        ----------
        rf_serialization_path: str
            Path of the trained RF.

        dataset_path: str
            Path of testing dataset.
        """
        rf = self.load_rf(rf_serialization_path)
        df = pd.read_csv(dataset_path)
        label_mapping = {"Benign": 0, "Attack": 1}
        df["Label"] = df["Label"].map(label_mapping)
        y = df["Label"]
        X = df.drop(["Label"], axis=1)

        y_predict = rf.predict(X)
        print(classification_report(y, y_predict))
        plot_confusion_matrix(rf, X, y, display_labels=["Benign", "Attack"])
    
