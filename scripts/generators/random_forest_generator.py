#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from nfstream import NFStreamer, NFPlugin
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import time
import datetime
import logging
import pickle

from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing import minmax_scale
from sklearn.feature_selection import mutual_info_classif
from sklearn.feature_selection import chi2
from sklearn.feature_selection import f_classif
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.tree import plot_tree
from sklearn.tree import _tree
from sklearn.utils import shuffle


class FlowSlicer(NFPlugin):
    def __feature_copy(self, flow):
        flow.udps.id = flow.id
        flow.udps.expiration_id = flow.expiration_id
        flow.udps.src_ip = flow.src_ip
        flow.udps.src_mac = flow.src_mac
        flow.udps.src_oui = flow.src_oui
        flow.udps.src_port = flow.src_port
        flow.udps.dst_ip = flow.dst_ip
        flow.udps.dst_mac = flow.dst_mac
        flow.udps.dst_oui = flow.dst_oui
        flow.udps.dst_port = flow.dst_port
        flow.udps.protocol = flow.protocol
        flow.udps.ip_version = flow.ip_version
        flow.udps.vlan_id = flow.vlan_id
        flow.udps.tunnel_id = flow.tunnel_id
        flow.udps.bidirectional_first_seen_ms = flow.bidirectional_first_seen_ms
        flow.udps.bidirectional_last_seen_ms = flow.bidirectional_last_seen_ms
        flow.udps.bidirectional_duration_ms = flow.bidirectional_duration_ms
        flow.udps.bidirectional_packets = flow.bidirectional_packets
        flow.udps.bidirectional_bytes = flow.bidirectional_bytes
        flow.udps.src2dst_first_seen_ms = flow.src2dst_first_seen_ms
        flow.udps.src2dst_last_seen_ms = flow.src2dst_last_seen_ms
        flow.udps.src2dst_duration_ms = flow.src2dst_duration_ms
        flow.udps.src2dst_packets = flow.src2dst_packets
        flow.udps.src2dst_bytes = flow.src2dst_bytes
        flow.udps.dst2src_first_seen_ms = flow.dst2src_first_seen_ms
        flow.udps.dst2src_last_seen_ms = flow.dst2src_last_seen_ms
        flow.udps.dst2src_duration_ms = flow.dst2src_duration_ms
        flow.udps.dst2src_packets = flow.dst2src_packets
        flow.udps.dst2src_bytes = flow.dst2src_bytes
        flow.udps.bidirectional_min_ps = flow.bidirectional_min_ps
        flow.udps.bidirectional_mean_ps = flow.bidirectional_mean_ps
        flow.udps.bidirectional_stddev_ps = flow.bidirectional_stddev_ps
        flow.udps.bidirectional_max_ps = flow.bidirectional_max_ps
        flow.udps.src2dst_min_ps = flow.src2dst_min_ps
        flow.udps.src2dst_mean_ps = flow.src2dst_mean_ps
        flow.udps.src2dst_stddev_ps = flow.src2dst_stddev_ps
        flow.udps.src2dst_max_ps = flow.src2dst_max_ps
        flow.udps.dst2src_min_ps = flow.dst2src_min_ps
        flow.udps.dst2src_mean_ps = flow.dst2src_mean_ps
        flow.udps.dst2src_stddev_ps = flow.dst2src_stddev_ps
        flow.udps.dst2src_max_ps = flow.dst2src_max_ps
        flow.udps.bidirectional_min_piat_ms = flow.bidirectional_min_piat_ms
        flow.udps.bidirectional_mean_piat_ms = flow.bidirectional_mean_piat_ms
        flow.udps.bidirectional_stddev_piat_ms = flow.bidirectional_stddev_piat_ms
        flow.udps.bidirectional_max_piat_ms = flow.bidirectional_max_piat_ms
        flow.udps.src2dst_min_piat_ms = flow.src2dst_min_piat_ms
        flow.udps.src2dst_mean_piat_ms = flow.src2dst_mean_piat_ms
        flow.udps.src2dst_stddev_piat_ms = flow.src2dst_stddev_piat_ms
        flow.udps.src2dst_max_piat_ms = flow.src2dst_max_piat_ms
        flow.udps.dst2src_min_piat_ms = flow.dst2src_min_piat_ms
        flow.udps.dst2src_mean_piat_ms = flow.dst2src_mean_piat_ms
        flow.udps.dst2src_stddev_piat_ms = flow.dst2src_stddev_piat_ms
        flow.udps.dst2src_max_piat_ms = flow.dst2src_max_piat_ms
        flow.udps.bidirectional_syn_packets = flow.bidirectional_syn_packets
        flow.udps.bidirectional_cwr_packets = flow.bidirectional_cwr_packets
        flow.udps.bidirectional_ece_packets = flow.bidirectional_ece_packets
        flow.udps.bidirectional_urg_packets = flow.bidirectional_urg_packets
        flow.udps.bidirectional_ack_packets = flow.bidirectional_ack_packets
        flow.udps.bidirectional_psh_packets = flow.bidirectional_psh_packets
        flow.udps.bidirectional_rst_packets = flow.bidirectional_rst_packets
        flow.udps.bidirectional_fin_packets = flow.bidirectional_fin_packets
        flow.udps.src2dst_syn_packets = flow.src2dst_syn_packets
        flow.udps.src2dst_cwr_packets = flow.src2dst_cwr_packets
        flow.udps.src2dst_ece_packets = flow.src2dst_ece_packets
        flow.udps.src2dst_urg_packets = flow.src2dst_urg_packets
        flow.udps.src2dst_ack_packets = flow.src2dst_ack_packets
        flow.udps.src2dst_psh_packets = flow.src2dst_psh_packets
        flow.udps.src2dst_rst_packets = flow.src2dst_rst_packets
        flow.udps.src2dst_fin_packets = flow.src2dst_fin_packets
        flow.udps.dst2src_syn_packets = flow.dst2src_syn_packets
        flow.udps.dst2src_cwr_packets = flow.dst2src_cwr_packets
        flow.udps.dst2src_ece_packets = flow.dst2src_ece_packets
        flow.udps.dst2src_urg_packets = flow.dst2src_urg_packets
        flow.udps.dst2src_ack_packets = flow.dst2src_ack_packets
        flow.udps.dst2src_psh_packets = flow.dst2src_psh_packets
        flow.udps.dst2src_rst_packets = flow.dst2src_rst_packets
        flow.udps.dst2src_fin_packets = flow.dst2src_fin_packets

    def on_init(self, packet, flow):
        self.__feature_copy(flow)

    def on_update(self, packet, flow):
        if flow.bidirectional_packets <= self.bidirectional_pkt_count:
            self.__feature_copy(flow)


class RFGenerator:

    __slots__ = ('id',
                 'expiration_id',
                 'src_ip',
                 'src_mac',
                 'src_oui',
                 'src_port',
                 'dst_ip',
                 'dst_mac',
                 'dst_oui',
                 'dst_port',
                 'protocol',
                 'ip_version',
                 'vlan_id',
                 'tunnel_id',
                 'bidirectional_first_seen_ms',
                 'bidirectional_last_seen_ms',
                 'bidirectional_duration_ms',
                 'bidirectional_packets',
                 'bidirectional_bytes',
                 'src2dst_first_seen_ms',
                 'src2dst_last_seen_ms',
                 'src2dst_duration_ms',
                 'src2dst_packets',
                 'src2dst_bytes',
                 'dst2src_first_seen_ms',
                 'dst2src_last_seen_ms',
                 'dst2src_duration_ms',
                 'dst2src_packets',
                 'dst2src_bytes',
                 'bidirectional_min_ps',
                 'bidirectional_mean_ps',
                 'bidirectional_stddev_ps',
                 'bidirectional_max_ps',
                 'src2dst_min_ps',
                 'src2dst_mean_ps',
                 'src2dst_stddev_ps',
                 'src2dst_max_ps',
                 'dst2src_min_ps',
                 'dst2src_mean_ps',
                 'dst2src_stddev_ps',
                 'dst2src_max_ps',
                 'bidirectional_min_piat_ms',
                 'bidirectional_mean_piat_ms',
                 'bidirectional_stddev_piat_ms',
                 'bidirectional_max_piat_ms',
                 'src2dst_min_piat_ms',
                 'src2dst_mean_piat_ms',
                 'src2dst_stddev_piat_ms',
                 'src2dst_max_piat_ms',
                 'dst2src_min_piat_ms',
                 'dst2src_mean_piat_ms',
                 'dst2src_stddev_piat_ms',
                 'dst2src_max_piat_ms',
                 'bidirectional_syn_packets',
                 'bidirectional_cwr_packets',
                 'bidirectional_ece_packets',
                 'bidirectional_urg_packets',
                 'bidirectional_ack_packets',
                 'bidirectional_psh_packets',
                 'bidirectional_rst_packets',
                 'bidirectional_fin_packets',
                 'src2dst_syn_packets',
                 'src2dst_cwr_packets',
                 'src2dst_ece_packets',
                 'src2dst_urg_packets',
                 'src2dst_ack_packets',
                 'src2dst_psh_packets',
                 'src2dst_rst_packets',
                 'src2dst_fin_packets',
                 'dst2src_syn_packets',
                 'dst2src_cwr_packets',
                 'dst2src_ece_packets',
                 'dst2src_urg_packets',
                 'dst2src_ack_packets',
                 'dst2src_psh_packets',
                 'dst2src_rst_packets',
                 'dst2src_fin_packets')

    def __init__(self) -> None:
        print("Start building Random Forest")

    def __label_flow(self, src_ip, dst_ip, day):
        ''' label the flow with 1 for "Attack" and 0 for "Benign"
        '''
        if day == "monday":
            return 0
        elif day == "tuesday":
            if src_ip == "172.16.0.1":
                return 1
            else:
                return 0
        elif day == "wednesday":
            if (src_ip == "172.16.0.1"):
                return 1
            else:
                return 0
        elif day == "thursday":
            if (src_ip == "172.16.0.1") or (src_ip == "192.168.10.8"):
                return 1
            else:
                return 0
        elif day == "friday":
            if ((src_ip == '192.168.10.12' and dst_ip == '52.6.13.28')
                    or (src_ip == '192.168.10.50' and dst_ip == '172.16.0.1')
                    or (src_ip == '172.16.0.1' and dst_ip == '192.168.10.50')
                    or (src_ip == '192.168.10.17' and dst_ip == '52.7.235.158')
                    or (src_ip == '192.168.10.8' and dst_ip == '205.174.165.73')
                    or (src_ip == '192.168.10.5' and dst_ip == '205.174.165.73')
                    or (src_ip == '192.168.10.14' and dst_ip == '205.174.165.73')
                    or (src_ip == '192.168.10.9' and dst_ip == '205.174.165.73')
                    or (src_ip == '205.174.165.73' and dst_ip == '192.168.10.8')
                    or (src_ip == '192.168.10.15' and dst_ip == '205.174.165.73')):
                return 1
            else:
                return 0

    def __map_udps_features(self):
        feature_dict = {}
        for feature in self.__slots__:
            udps_feature = "udps." + feature
            feature_dict[udps_feature] = feature
        return feature_dict

    def to_flow(self, pcap_path, save_path):
        ''' Aggregate packets into flows
        '''
        my_streamer = NFStreamer(source=pcap_path,
                                 n_dissections=0,
                                 accounting_mode=3,
                                 statistical_analysis=True)
        my_streamer.to_csv(path=save_path,
                           columns_to_anonymize=[],
                           flows_per_file=0,
                           rotate_files=0)
        print("Aggregated packets into flows without slicing.")

    def to_flow_sliced(self, pcap_path, save_path, limit):
        ''' Aggregate packets into flows containing the first n packets
        '''
        my_streamer = NFStreamer(source=pcap_path,
                                 n_dissections=0,
                                 accounting_mode=3,
                                 udps=FlowSlicer(
                                     bidirectional_pkt_count=limit),
                                 statistical_analysis=True,
                                 splt_analysis=limit)
        df = my_streamer.to_pandas(columns_to_anonymize=[])
        # eliminate the non-udps features whose values are computed from the entire flow
        # (the last three features are splt features from plt_analysis)
        df = df.iloc[:, len(self.__slots__):]
        # change the names of columns (delete "udps.")
        df.rename(columns=self.__map_udps_features(), inplace=True)

        # split features of early statstical analysis.
        split_columns = feature_to_split = [
            'splt_direction', 'splt_ps', 'splt_piat_ms']
        for feature in split_columns:
            split_data = df[feature].str.split(",", n=limit, expand=True)
            for i in range(limit):
                # delete '[', ']' and ' ' in each splitted feature
                df[feature + '_' +
                    str(i+1)] = split_data[i].str.strip("[ ]")
        df = df.drop(split_columns, axis=1)
        df.to_csv(save_path, index=False)
        print(
            f"Aggregated packets into flows with slicing (first {limit} packets).")

    def preprocess_single_file(self, csv_path, save_path, day, drop_columns=None, categorical_columns=None, splt_columns=None):
        ''' Preprocess the flows.

        Drop flow entries containing missing data. Delete unneeded features. One-hot coding for
        categorical features. Label each flow with 1 for "Attack" and 0 for "Benign"

        '''
        df = pd.read_csv(csv_path)

        # drop rows containing missing data
        df = df.dropna()

        # add 1 for each splt feature to avoid -1 which is hard to be handled in p4
        if (splt_columns != None):
            df[splt_columns] = df[splt_columns] + 1

        # one-hot coding for categorical columns
        if categorical_columns != None:
            df = pd.get_dummies(df, columns=categorical_columns)

        # label each flow entry (This code should be placed after dealing with categorical and split columns)
        df["Label"] = df.apply(
            lambda x: self.__label_flow(x["src_ip"], x["dst_ip"], day), axis=1)

        # drop unneeded columns (has to be processed after label flows,
        # in case dopped columns have features used to label flows)
        if drop_columns != None:
            df = df.drop(drop_columns, axis=1)

        # convert the unit of time related features from millisecond to microsecond which is used in P4
        time_features = []
        for feature in df.columns:
            if "ms" in feature:
                time_features.append(feature)
        df[time_features] = df[time_features] * 1000
        print("The unit of time related features have to be converted to microsecond")

        # set index=False to avoid reading the first column as Unnamed: 0
        df.to_csv(save_path, index=False)
        print(f"Preprocessed the {day} flow file. Labeled each flow.")
        return df

    def preprocess_files_to_one_balanced(self, csv_pathes, save_path, packets_num, drop_columns=None, categorical_columns=None, splt_columns=None):
        ''' Preprocess mutiple files and concatenate them to one file

        Drop flow entries containing missing data. Delete unneeded features. One-hot coding for
        categorical features. Label each flow with 1 for "Attack" and 0 for "Benign"

        '''
        # label each dataset
        for path in csv_pathes:
            if "Tuesday" in path:
                df_tues = pd.read_csv(path)
                # extract the flows with {packets_num} bidirectional packets
                df_tues = df_tues[df_tues["bidirectional_packets"]
                                  == packets_num]
                df_tues["Label"] = df_tues.apply(lambda x: self.__label_flow(
                    x["src_ip"], x["dst_ip"], "tuesday"), axis=1)
                print("Tuesday dataset has been labeled")
            elif "Wednesday" in path:
                df_wed = pd.read_csv(path)
                # extract the flows with {packets_num} bidirectional packets
                df_wed = df_wed[df_wed["bidirectional_packets"] == packets_num]
                df_wed["Label"] = df_wed.apply(lambda x: self.__label_flow(
                    x["src_ip"], x["dst_ip"], "wednesday"), axis=1)
                print("Wednesday dataset has been labeled")
            elif "Thursday" in path:
                df_thurs = pd.read_csv(path)
                # extract the flows with {packets_num} bidirectional packets
                df_thurs = df_thurs[df_thurs["bidirectional_packets"]
                                    == packets_num]
                df_thurs["Label"] = df_thurs.apply(lambda x: self.__label_flow(
                    x["src_ip"], x["dst_ip"], "thursday"), axis=1)
                print("Thursday dataset has been labeled")
            elif "Friday" in path:
                df_fri = pd.read_csv(path)
                # extract the flows with {packets_num} bidirectional packets
                df_fri = df_fri[df_fri["bidirectional_packets"] == packets_num]
                df_fri["Label"] = df_fri.apply(lambda x: self.__label_flow(
                    x["src_ip"], x["dst_ip"], "friday"), axis=1)
                print("Friday dataset has been labeled")

        ######################################### balance each dataset (benign flows == attack flows) #########################################
        # balance Tuesday
        df_tues_grouped = df_tues.groupby("Label")
        min_sample_num = df_tues_grouped.size().min()
        df_tues_grouped = pd.DataFrame(df_tues_grouped.apply(
            lambda x: x.sample(min_sample_num).reset_index(drop=True)))
        # shuffle the dataset (after grouped, the first half has label 0, the last half has label 1)
        df_tues_grouped = shuffle(df_tues_grouped)

        # balance Wednesday
        df_wed_grouped = df_wed.groupby("Label")
        df_wed_grouped = pd.DataFrame(df_wed_grouped.apply(
            lambda x: x.sample(min_sample_num).reset_index(drop=True)))
        # shuffle the dataset (after grouped, the first half has label 0, the last half has label 1)
        df_wed_grouped = shuffle(df_wed_grouped)

        # balance Thursday
        df_thurs_grouped = df_thurs.groupby("Label")
        df_thurs_grouped = pd.DataFrame(df_thurs_grouped.apply(
            lambda x: x.sample(min_sample_num).reset_index(drop=True)))
        # shuffle the dataset (after grouped, the first half has label 0, the last half has label 1)
        df_thurs_grouped = shuffle(df_thurs_grouped)

        # balance Friday
        df_fri_grouped = df_fri.groupby("Label")
        df_fri_grouped = pd.DataFrame(df_fri_grouped.apply(
            lambda x: x.sample(min_sample_num).reset_index(drop=True)))
        # shuffle the dataset (after grouped, the first half has label 0, the last half has label 1)
        df_fri_grouped = shuffle(df_fri_grouped)

        ######################################### preprocess datasets #########################################
        # concatenate dataset and label set
        df = pd.concat([df_tues_grouped, df_wed_grouped,
                       df_thurs_grouped, df_fri_grouped])

        # drop rows containing missing data
        df = df.dropna()

        df_label = df["Label"]
        df = df.drop("Label", axis=1)

        # add 1 for each splt feature to avoid -1 which is hard to be handled in p4
        if (splt_columns != None):
            df[splt_columns] = df[splt_columns] + 1

        # one-hot coding for categorical columns
        if categorical_columns != None:
            df = pd.get_dummies(df, columns=categorical_columns)

        # drop unneeded columns
        if drop_columns != None:
            df = df.drop(drop_columns, axis=1)

        # add label column to concatenated dataset
        df.insert(len(df.columns), "Label", df_label)

        # convert the unit of time related features from millisecond to microsecond which is used in P4
        time_features = []
        for feature in df.columns:
            if "ms" in feature:
                time_features.append(feature)
        df[time_features] = df[time_features] * 1000

        print("The unit of time related features have to be converted to microsecond")

        # shuffle final concatenated dataset
        df = shuffle(df)

        # set index=False to avoid reading the first column as Unnamed: 0
        df.to_csv(save_path, index=False)
        return df

    def _extract_no_duplicate(self, df):
        ''' Remove the duplicated flow entries. Balance the dataset to the same number of attacks and benigns
        '''
        # get the benign and attack dataset
        df_benign = df[df["Label"] == 0]
        df_attack = df[df["Label"] == 1]

        # cut the replicated flow entries for benign
        df_benign_no_dup = df_benign[df_benign.duplicated(
            keep='first').map({True: False, False: True})]
        # the number of attack flows is less than the number of benign flows without duplicates

        # the number of the sample is equal to the number attack
        sample_num = len(df_attack)
        print(
            f"Sample number (Number of attack flow without duplicated entries): {sample_num}")
        # sample the no duplicates benign and attack dataset
        # set drop=True to remove the orignal index after sampling
        df_benign_no_dup = df_benign_no_dup.sample(
            sample_num).reset_index(drop=True)

        # concatenate df_benign_no_dup and df_attack and shuffle them
        df = pd.concat([df_benign_no_dup, df_attack])
        df = shuffle(df)
        return df

    def preprocess_files_balanced_each_no_duplicate(self, csv_pathes, save_path, packets_num, drop_columns=None, categorical_columns=None, splt_columns=None):
        ''' Preprocess mutiple files and concatenate them to one file

            Generate concatenated dataset without dulicates for attack flows. The number of attack flow entries of
            each day is the same and also same as the benign flow entries. The result only contains the flow entries
            with {packets_num} bidirectional packets.

        '''
        # label each dataset
        for path in csv_pathes:
            if "Tuesday" in path:
                df_tues = pd.read_csv(path)
                # extract the flows with {packets_num} bidirectional packets
                df_tues = df_tues[df_tues["bidirectional_packets"]
                                  == packets_num]
                df_tues["Label"] = df_tues.apply(lambda x: self.__label_flow(
                    x["src_ip"], x["dst_ip"], "tuesday"), axis=1)
                print("Tuesday dataset has been labeled")
            elif "Wednesday" in path:
                df_wed = pd.read_csv(path)
                # extract the flows with {packets_num} bidirectional packets
                df_wed = df_wed[df_wed["bidirectional_packets"] == packets_num]
                df_wed["Label"] = df_wed.apply(lambda x: self.__label_flow(
                    x["src_ip"], x["dst_ip"], "wednesday"), axis=1)
                print("Wednesday dataset has been labeled")
            elif "Thursday" in path:
                df_thurs = pd.read_csv(path)
                # extract the flows with {packets_num} bidirectional packets
                df_thurs = df_thurs[df_thurs["bidirectional_packets"]
                                    == packets_num]
                df_thurs["Label"] = df_thurs.apply(lambda x: self.__label_flow(
                    x["src_ip"], x["dst_ip"], "thursday"), axis=1)
                print("Thursday dataset has been labeled")
            elif "Friday" in path:
                df_fri = pd.read_csv(path)
                # extract the flows with {packets_num} bidirectional packets
                df_fri = df_fri[df_fri["bidirectional_packets"] == packets_num]
                df_fri["Label"] = df_fri.apply(lambda x: self.__label_flow(
                    x["src_ip"], x["dst_ip"], "friday"), axis=1)
                print("Friday dataset has been labeled")

        ################################################ Balance each dataset ################################################
        # In each day dataset, the number of attack flows with duplicates is less than the number of benign flows without
        # duplicates. The benign flows without duplicates are downsampled to the same number of the attack flows with duplicates
        # Why? balance the dataset while keeping the attack flows as much as possible

        # remove duplicated flow entries
        df_tues = self._extract_no_duplicate(df_tues)
        print(f"Tuesday balanced dataset: {len(df_tues)} flows")
        df_wed = self._extract_no_duplicate(df_wed)
        print(f"Tuesday balanced dataset: {len(df_wed)} flows")
        df_thurs = self._extract_no_duplicate(df_thurs)
        print(f"Tuesday balanced dataset: {len(df_thurs)} flows")
        df_fri = self._extract_no_duplicate(df_fri)
        print(f"Tuesday balanced dataset: {len(df_fri)} flows")

        # extract benign and attack flows for each day dataset
        df_tues_benign = df_tues[df_tues["Label"] == 0]
        df_tues_attack = df_tues[df_tues["Label"] == 1]
        df_wed_benign = df_wed[df_wed["Label"] == 0]
        df_wed_attack = df_wed[df_wed["Label"] == 1]
        df_thurs_benign = df_thurs[df_thurs["Label"] == 0]
        df_thurs_attack = df_thurs[df_thurs["Label"] == 1]
        df_fri_benign = df_fri[df_fri["Label"] == 0]
        df_fri_attack = df_fri[df_fri["Label"] == 1]

        # get the minimum number of attack flow entries
        min_attack_num = min([len(df_tues_attack), len(
            df_wed_attack), len(df_thurs_attack), len(df_fri_attack)])

        # sample each benign and attack dataset
        df_tues_benign = df_tues_benign.sample(
            min_attack_num).reset_index(drop=True)
        df_tues_attack = df_tues_attack.sample(
            min_attack_num).reset_index(drop=True)
        df_wed_benign = df_wed_benign.sample(
            min_attack_num).reset_index(drop=True)
        df_wed_attack = df_wed_attack.sample(
            min_attack_num).reset_index(drop=True)
        df_thurs_benign = df_thurs_benign.sample(
            min_attack_num).reset_index(drop=True)
        df_thurs_attack = df_thurs_attack.sample(
            min_attack_num).reset_index(drop=True)
        df_fri_benign = df_fri_benign.sample(
            min_attack_num).reset_index(drop=True)
        df_fri_attack = df_fri_attack.sample(
            min_attack_num).reset_index(drop=True)

        # concatenate datasets and shuffle them
        df_tues = pd.concat([df_tues_benign, df_tues_attack])
        df_tues = shuffle(df_tues)
        df_wed = pd.concat([df_wed_benign, df_wed_attack])
        df_wed = shuffle(df_wed)
        df_thurs = pd.concat([df_thurs_benign, df_thurs_attack])
        df_thurs = shuffle(df_thurs)
        df_fri = pd.concat([df_fri_benign, df_fri_attack])
        df_fri = shuffle(df_fri)

        print(
            f"datasets have been sampled to {min_attack_num} attack and benign flow entries")

        ######################################### preprocess datasets #########################################
        # concatenate dataset and label set
        df = pd.concat([df_tues, df_wed, df_thurs, df_fri])

        # drop rows containing missing data
        df = df.dropna()

        df_label = df["Label"]
        df = df.drop("Label", axis=1)

        # add 1 for each splt feature to avoid -1 which is hard to be handled in p4
        if (splt_columns != None):
            df[splt_columns] = df[splt_columns] + 1

        # one-hot coding for categorical columns
        if categorical_columns != None:
            df = pd.get_dummies(df, columns=categorical_columns)

        # drop unneeded columns
        if drop_columns != None:
            df = df.drop(drop_columns, axis=1)

        # add label column to concatenated dataset
        df.insert(len(df.columns), "Label", df_label)

        # convert the unit of time related features from millisecond to microsecond which is used in P4
        time_features = []
        for feature in df.columns:
            if "ms" in feature:
                time_features.append(feature)
        df[time_features] = df[time_features] * 1000

        print("The unit of time related features have to be converted to microsecond")

        # shuffle final concatenated dataset
        df = shuffle(df)

        # set index=False to avoid reading the first column as Unnamed: 0
        df.to_csv(save_path, index=False)
        return df

    def preprocess_file_no_duplicate(self, csv_pathes, save_path, packets_num, drop_columns=None, categorical_columns=None, splt_columns=None):
        ''' Preprocess mutiple files and concatenate them to one file

            Generate concatenated dataset without dulicates for attack flows. The number of attack flow entries of
            each day is the same as the benign flow entries. The result only contains the flow entries
            with {packets_num} bidirectional packets.
        '''
        # label each dataset
        for path in csv_pathes:
            if "Tuesday" in path:
                df_tues = pd.read_csv(path)
                # extract the flows with {packets_num} bidirectional packets
                df_tues = df_tues[df_tues["bidirectional_packets"]
                                  == packets_num]
                df_tues["Label"] = df_tues.apply(lambda x: self.__label_flow(
                    x["src_ip"], x["dst_ip"], "tuesday"), axis=1)
                print("Tuesday dataset has been labeled")
                # drop unneeded columns (has to be placed after labeling flow, in order to find dulicated flow entires)
                if drop_columns != None:
                    df_tues = df_tues.drop(drop_columns, axis=1)
            elif "Wednesday" in path:
                df_wed = pd.read_csv(path)
                # extract the flows with {packets_num} bidirectional packets
                df_wed = df_wed[df_wed["bidirectional_packets"] == packets_num]
                df_wed["Label"] = df_wed.apply(lambda x: self.__label_flow(
                    x["src_ip"], x["dst_ip"], "wednesday"), axis=1)
                print("Wednesday dataset has been labeled")
                # drop unneeded columns (has to be placed after labeling flow, in order to find dulicated flow entires)
                if drop_columns != None:
                    df_wed = df_wed.drop(drop_columns, axis=1)
            elif "Thursday" in path:
                df_thurs = pd.read_csv(path)
                # extract the flows with {packets_num} bidirectional packets
                df_thurs = df_thurs[df_thurs["bidirectional_packets"]
                                    == packets_num]
                df_thurs["Label"] = df_thurs.apply(lambda x: self.__label_flow(
                    x["src_ip"], x["dst_ip"], "thursday"), axis=1)
                print("Thursday dataset has been labeled")
                # drop unneeded columns (has to be placed after labeling flow, in order to find dulicated flow entires)
                if drop_columns != None:
                    df_thurs = df_thurs.drop(drop_columns, axis=1)
            elif "Friday" in path:
                df_fri = pd.read_csv(path)
                # extract the flows with {packets_num} bidirectional packets
                df_fri = df_fri[df_fri["bidirectional_packets"] == packets_num]
                df_fri["Label"] = df_fri.apply(lambda x: self.__label_flow(
                    x["src_ip"], x["dst_ip"], "friday"), axis=1)
                print("Friday dataset has been labeled")
                # drop unneeded columns (has to be placed after labeling flow, in order to find dulicated flow entires)
                if drop_columns != None:
                    df_fri = df_fri.drop(drop_columns, axis=1)

        ################################################ Balance each dataset ################################################
        # In each day dataset, the number of attack flows with duplicates is less than the number of benign flows without
        # duplicates. The benign flows without duplicates are downsampled to the same number of the attack flows with duplicates
        # Why? balance the dataset while keeping the attack flows as much as possible

        df_tues = self._extract_no_duplicate(df_tues)
        print(f"Tuesday balanced dataset: {len(df_tues)} flows")
        df_wed = self._extract_no_duplicate(df_wed)
        print(f"Tuesday balanced dataset: {len(df_wed)} flows")
        df_thurs = self._extract_no_duplicate(df_thurs)
        print(f"Tuesday balanced dataset: {len(df_thurs)} flows")
        df_fri = self._extract_no_duplicate(df_fri)
        print(f"Tuesday balanced dataset: {len(df_fri)} flows")

        ######################################### preprocess datasets #########################################
        # concatenate dataset and label set
        df = pd.concat([df_tues, df_wed,
                       df_thurs, df_fri])

        # drop rows containing missing data
        df = df.dropna()

        # move "Label" column at the end.
        # this line has been placed before one-hot encoding.
        df_label = df["Label"]
        df = df.drop("Label", axis=1)

        # add 1 for each splt feature to avoid -1 which is hard to be handled in p4
        if (splt_columns != None):
            df[splt_columns] = df[splt_columns] + 1

        # one-hot coding for categorical columns
        if categorical_columns != None:
            df = pd.get_dummies(df, columns=categorical_columns)

        # convert the unit of time related features from millisecond to microsecond which is used in P4
        time_features = []
        for feature in df.columns:
            if "ms" in feature:
                time_features.append(feature)
        df[time_features] = df[time_features] * 1000
        print("The unit of time related features have to be converted to microsecond")

        # add label column to concatenated dataset
        df.insert(len(df.columns), "Label", df_label)

        # shuffle final concatenated dataset
        df = shuffle(df)

        # set index=False to avoid reading the first column as Unnamed: 0
        df.to_csv(save_path, index=False)
        return df

    def split_dataset(self, dataset_path, test_size=0.3, val_size=None):
        ''' Split the dataset into train, test and validation sets.
        '''
        df = pd.read_csv(dataset_path)
        X_train, X_test, y_train, y_test = train_test_split(df.iloc[:, :-1],
                                                            df.iloc[:, -1],
                                                            test_size=test_size,
                                                            random_state=42)
        if val_size != None:
            X_train, X_val, y_train, y_val = train_test_split(X_train,
                                                              y_train,
                                                              test_size=val_size,
                                                              random_state=8)
        # print(f"X_train shape: {X_train.shape}")
        # print(f"y_train shape: {y_train.shape}")
        # print(f"X_test shape: {X_test.shape}")
        # print(f"y_test shape: {y_test.shape}")

        if val_size != None:
            print(f"X_val shape: {X_val.shape}")
            print(f"y_val shape: {y_val.shape}")
            return (X_train, X_val, X_test, y_train, y_test, y_val)
        else:
            return (X_train, X_test, y_train, y_test)

    def compute_feature_importances(self, data_path, feature_scores_save_path, type_str, repeat_time=1, record_logging=False, logging_path=None):
        ''' Get the most relavant features
        '''
        if record_logging:
            start_computing = time.time()
            logging.basicConfig(
                filename=logging_path, filemode='a', level=logging.INFO)
            logging.info(
                "**************************************************************************************")
            logging.info(
                "**************************************************************************************")
            logging.info(type_str)
            logging.info(
                f"The computation of feature importance procedure starts at {time.asctime(time.localtime(start_computing))}")

        # read the preprocessed data
        X_train, X_val, y_train, y_val = self.split_dataset(
            dataset_path=data_path, test_size=0.3)

        features = X_train.columns
        features_num = len(features)

        # 1: Mutual Information
        mutual_info = np.zeros(features_num)
        for i in range(repeat_time):
            # record logging
            if record_logging:
                start_timestamp = time.time()
                logging.info(
                    f"Mutual information: {i+1} starts {time.asctime(time.localtime(start_timestamp))}")
            mutual_info = mutual_info + \
                minmax_scale(mutual_info_classif(X_train, y_train))
            # record logging
            if record_logging:
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
            if record_logging:
                start_timestamp = time.time()
                logging.info(
                    f"Impurity importance: {i+1} starts {time.asctime(time.localtime(start_timestamp))}")
            clf = clf.fit(X_train, y_train)
            impurity_info = impurity_info + \
                minmax_scale(clf.feature_importances_)
            # record logging
            if record_logging:
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
            if record_logging:
                start_timestamp = time.time()
                logging.info(
                    f"Random forest importance: {i+1} starts {time.asctime(time.localtime(start_timestamp))}")
            rf = rf.fit(X_train, y_train)
            rf_importance = rf_importance + \
                minmax_scale(rf.feature_importances_)
            # record logging
            if record_logging:
                end_timestamp = time.time()
                logging.info(
                    f"Random forest importance: {i+1} ends {time.asctime(time.localtime(end_timestamp))}")
                logging.info(
                    f"Random forest importance: {i+1} takes time {datetime.timedelta(seconds=(end_timestamp - start_timestamp))}")
            # record logging
            if record_logging:
                start_timestamp = time.time()
                logging.info(
                    f"Permutation importance: {i+1} starts {time.asctime(time.localtime(start_timestamp))}")
            permutation_info = permutation_info + \
                minmax_scale(permutation_importance(
                    rf, X_val, y_val, n_repeats=5).importances_mean)
            # record logging:
            if record_logging:
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

        if record_logging:
            end_computing = time.time()
            logging.info(
                f"The computation of feature importance procedure ends at {time.asctime(time.localtime(end_computing))}")
            logging.info(
                f"The computation of feature importance procedure takes time {datetime.timedelta(seconds=(end_computing - start_computing))}")
            logging.info(f"The final order of features: {df.index}\n\n\n")

        df.to_csv(feature_scores_save_path)
        return df

    def get_relevant_features(self, feature_scores_path, original_dataset_path, dataset_relevant_save_path, fig_path, relevant_features_num, fig_title, plot_relevant_feature=False):
        ''' Save the data of the relevant features.
        '''
        # get the relevant features
        feature_scores_df = pd.read_csv(feature_scores_path, index_col=0)
        relevant_features = feature_scores_df.iloc[:relevant_features_num, :]

        # read the preprocessed data
        df = pd.read_csv(original_dataset_path)
        # save data of the relevant features
        relevant_features_index = relevant_features.index.tolist()
        df = df[relevant_features_index + ["Label"]]
        df.to_csv(dataset_relevant_save_path, index=False)

        # plot relevant feature importance scores
        if plot_relevant_feature:
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

    def get_best_estimator(self, cv_results_path, params, X_train, y_train):
        ''' Compute the best random forest estimator
        '''
        clf = RandomForestClassifier(n_jobs=-1)

        # use grid search to find the best hyperparamters
        grid_search = GridSearchCV(
            estimator=clf, param_grid=params, cv=5, n_jobs=-1, verbose=1, scoring="f1_macro")
        grid_search.fit(X_train, y_train)

        # save the results of each combination
        df = pd.DataFrame(grid_search.cv_results_)
        for param in params.keys():
            cv_results_path = cv_results_path + '_' + \
                param + '_' + str(params[param])

        cv_results_path = cv_results_path + ".csv"
        df.to_csv(cv_results_path)

        print("Best score: " + str(grid_search.best_score_))
        print("Best parameters: " + str(grid_search.best_params_))

        # get the best estimator
        best_estimator = grid_search.best_estimator_
        return best_estimator, cv_results_path

    def plot_trees(self, save_path, rf_estimator, features):
        '''
        '''
        plt.figure(figsize=(95, 25))

        for i in range(len(rf_estimator.estimators_)):
            plot_tree(rf_estimator.estimators_[i],
                      feature_names=features,
                      class_names=['Benign', 'Attack'],
                      filled=True, impurity=True,
                      rounded=True)
            plt.savefig(save_path + "/dt_" + str(i + 1) + ".png", dpi=200)

    def save_rf(self, rf_serialization_path, rf_estimator):
        ''' Save the random forest estimator into file
        '''
        with open(rf_serialization_path, "wb") as f:
            pickle.dump(rf_estimator, f)
