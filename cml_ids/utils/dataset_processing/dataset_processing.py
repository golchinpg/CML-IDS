#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import math

from sklearn.utils import shuffle
from sklearn.model_selection import train_test_split


class DatasetPreprocess:
    """Process the flow-based dataset.
    """

    def __init__(self) -> None:
        print("Start processing datasets.")

    def labeling_entry(self, dataset_day, src_ip, dst_ip):
        """Label the flow entry of the CIC-IDS2017 dataset.

        Parameters
        ----------
        dataset_day: str {"Monday", "Tuesday", "Thursday", "Friday"}
            The week day of the dataset.
        src_ip: str
            The source IP address of the flow entry.
        dst_ip: str
            The destination IP address of the flow entry.
        """
        if dataset_day == "Monday":
            label = "Benign"
        elif dataset_day == "Tuesday":
            if (src_ip == "172.16.0.1"):
                label = "Attack"
            else:
                label = "Benign"
        elif dataset_day == "Wednesday":
            if (src_ip == "172.16.0.1"):
                label = "Attack"
            else:
                label = "Benign"
        elif dataset_day == "Thursday":
            if (src_ip == "172.16.0.1") or (src_ip == "192.168.10.8"):
                label = "Attack"
            else:
                label = "Benign"
        elif dataset_day == "Friday":
            if ((src_ip == "192.168.10.12" and dst_ip == "52.6.13.28")
                    or (src_ip == "192.168.10.50" and dst_ip == "172.16.0.1")
                    or (src_ip == "172.16.0.1" and dst_ip == "192.168.10.50")
                    or (src_ip == "192.168.10.17" and dst_ip == "52.7.235.158")
                    or (src_ip == "192.168.10.8" and dst_ip == "205.174.165.73")
                    or (src_ip == "192.168.10.5" and dst_ip == "205.174.165.73")
                    or (src_ip == "192.168.10.14" and dst_ip == "205.174.165.73")
                    or (src_ip == "192.168.10.9" and dst_ip == "205.174.165.73")
                    or (src_ip == "205.174.165.73" and dst_ip == "192.168.10.8")
                    or (src_ip == "192.168.10.15" and dst_ip == "205.174.165.73")):
                label = "Attack"
            else:
                label = "Benign"
        elif dataset_day == "Unseen":
            label = "Attack"
        else:
            raise ValueError(
                "The given week day name is incorrect. Please give a week day from 'Tuesday', 'Wednesday', 'Thursday' or 'Friday'. Note the capitalization of the first letter.")
        return label

    def preprocess(self, dataset_path, save_path, packet_count, drop_features=None, drop_features_wildcards=None):
        """Label each flow entry and remove the unused features and convert the values of the "Label" column.

        "Benign" -> 0; "Attack" -> 1

        Parameters
        ----------        
        dataset_path: str
            The flow-based dataset path (.csv). 
        save_path: str
            The path to store the processed dataset.
        packet_count: int
            Number of bidirectional packets within a flow,
        drop_features: list, default: None
            The list contains all feature names to drop. 
        drop_features_wildcards: list, default: None
            The list contains all wirdcards of dropped features

        Returns
        -------
        DataFrame
            The processed flow-based dataset.

        """
        df = pd.read_csv(dataset_path)

        print(f"The original size of flow-based dataset: {len(df)}.")

        # remove flow entry with less than <packet_count>
        df = df[df["bidirectional_packets"] == packet_count]
        print(
            f"Number of flows with more than or equal to {packet_count}: {len(df)}.")

        # drop rows containing missing data
        df = df.dropna()

        # label flow entry (have to be executed before droping features)
        if "Tuesday" in dataset_path:
            day = "Tuesday"
        elif "Wednesday" in dataset_path:
            day = "Wednesday"
        elif "Thursday" in dataset_path:
            day = "Thursday"
        elif "Friday" in dataset_path:
            day = "Friday"
        else:
            raise TypeError(
                "Please give the dataset path containing 'Tuesday', 'Wednesday', 'Thursday', or 'Friday'.")
        df["Label"] = df.apply(lambda x: self.labeling_entry(
            dataset_day=day, src_ip=x["src_ip"], dst_ip=x["dst_ip"]), axis=1)

        # drop unneeded feature
        if drop_features != None:
            df = df.drop(drop_features, axis=1)

        # drop unneeded feature matching any wildcard
        wildcard_drop_feature_list = []
        if drop_features_wildcards != None:
            for feature in df.columns:
                for wildcard in drop_features_wildcards:
                    if wildcard in feature:
                        wildcard_drop_feature_list.append(feature)
        df = df.drop(wildcard_drop_feature_list, axis=1)

        # round down the bidirectional_mean_ps feature
        # why? computing the mean of 8 packets can be done in P4
        df["bidirectional_mean_ps"] = df["bidirectional_mean_ps"].apply(
            lambda x: math.floor(x))

        # set index=False to avoid reading the first column as Unnamed: 0
        df.to_csv(save_path, index=False)
        return df

    def merge(self, dataset_path_list, save_path):
        """Merge datasets and shuffle to generate the unified training dataset.

        Parameters
        ----------  
        dataset_path_list: list
            List of dataset pathes that are merged.
        save_path: str
            The path to store the merged dataset.

        Returns
        -------
        DataFrame
            The unified training dataset.
        """
        # append all dataset into the list
        sum_length = 0
        df_list = []
        for path in dataset_path_list:
            df = pd.read_csv(path)
            df_list.append(df)
            sum_length += len(df)

        print(sum_length)
        df_merged = pd.concat(df_list)
        df_merged = shuffle(df_merged)

        print(
            f"Merged and schuffled datasets. The size of the final unified dataset is: {len(df_merged)}")
        # set index=False to avoid reading the first column as Unnamed: 0
        df_merged.to_csv(save_path, index=False)
        return df_merged

    def split_dataset(self, dataset_path, test_size=0.2):
        """Split dataset.

        Parameters
        ----------
        dataset_path: str
            Path of the training dataset

        Returns
        -------
        DataFrame (pandas):
            Training dataset (X).
        DataFrame (pandas):
            Testing dataset (X).
        DataFrame (pandas):
            Training dataset (y, label).
        DataFrame (pandas):
            Testing dataset (y, label).
        DataFrame (pandas):
            Validation dataset (X).
        DataFrame (pandas):
            Validation dataset (y, label).
        """

        df = pd.read_csv(dataset_path)

        # check the type of "Label" feature. If it's string ("Benign"/"Attack"), convert it to 0/1
        val_label = df["Label"][0]
        if type(val_label) is str:
            # convert "Benign"/"Attack" to 0/1
            label_mapping = {"Benign": 0, "Attack": 1}
            df["Label"] = df["Label"].map(label_mapping)
        elif type(val_label) is int:
            pass
        else:
            raise TypeError("The value of 'Label' feature should be integer.")

        X_tot, X_test, y_tot, y_test = train_test_split(
            df.iloc[:, :-1], df['Label'], test_size=test_size, random_state=42, stratify=df['Label'])
        X_train, X_val, y_train, y_val = train_test_split(
            df.iloc[:, :-1], df['Label'], test_size=test_size, random_state=42, stratify=df['Label'])

        for col in X_train.columns:
            if 'Unnamed' in col:
                X_train = X_train.drop(col, axis=1)
                X_test = X_test.drop(col, axis=1)
                X_val = X_val.drop(col, axis=1)
        self.input_dim = X_train.shape[1]
        print(X_train.columns)
        print(self.input_dim)
        return (X_train, X_test, y_train, y_test, X_val, y_val)
    
    def balance_dataset(self, dataset_path, save_path):
        """Balance the dataset based on their label
        
        Parameters
        ----------
        dataset_path: str
            Path of the imbalanced dataset.
        save_path: str
            Path for saving the balacned dataset.

        Returns
        -------
        DataFrame
            The balanced dataset.
        """
        df = pd.read_csv(dataset_path)
        df_benign = df[df["Label"] == "Benign"]
        df_attack = df[df["Label"] == "Attack"]

        # sample dataset based on the minmum flow number of benign of attack
        benign_count = len(df_benign)
        attack_count = len(df_attack)
        if benign_count > attack_count:
            min_count = attack_count
            df_benign = df_benign.sample(min_count).reset_index(drop=True)
        else:
            min_count = benign_count
            df_attack = df_attack.sample(min_count).reset_index(drop=True)
        
        df = pd.concat([df_benign, df_attack])
        df = shuffle(df)
        print(f"Dataset is balanced and shuffled with the size of {2 * min_count}.")

        # set index=False to avoid reading the first column as Unnamed: 0
        df.to_csv(save_path, index=False)
        return df
        
        
