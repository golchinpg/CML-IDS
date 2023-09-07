#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import pickle
import socket
import struct
import grpc
from time import sleep

from sklearn.tree import _tree

import p4runtime_lib.bmv2
import p4runtime_lib.helper
from p4runtime_lib.error_utils import printGrpcError
from p4runtime_lib.switch import ShutdownAllSwitchConnections


class Controller():

    def __init__(self, p4info_helper, switch, bmv2_json_path, data_plane_estimator_path) -> None:
        self.p4info_helper = p4info_helper
        self.switch = switch
        self.bmv2_json_path = bmv2_json_path
        # load the data plane estimator from file
        with open(data_plane_estimator_path, "rb") as f:
            self.data_plane_estimator = pickle.load(f)
        # TODO load the control plane estimator from file (if it's possible, why? modularity is better)

    def _ip2int(self, ip_addr):
        ''' Convert ip address to int
        '''
        return struct.unpack("!I", socket.inet_aton(ip_addr))[0]

    def write_table_entry(self, table_name_f, match_fields_f, action_name_f, action_params_f):
        ''' Write a signle table entry into the switch.
        '''
        table_entry = self.p4info_helper.buildTableEntry(
            table_name=table_name_f,
            match_fields=match_fields_f,
            action_name=action_name_f,
            action_params=action_params_f
        )
        self.switch.WriteTableEntry(table_entry)

    def read_table_entries(self):
        ''' Read the table entries
        '''
        count = 0
        print(f'\n----- Reading tables rules for {self.switch.name} -----')
        for response in self.switch.ReadTableEntries():
            for entity in response.entities:
                entry = entity.table_entry
                print(entry)
                print('-----')
                count = count + 1

        print(f"Total number of table entries: {count}")

    def write_table_entries_rf(self, packet_num_in_flow, feature_to_id_dict_serialization_path, relevant_features_list_serialization_path):
        ''' Generate and install table entries of random forest estimator to the switch.
        '''
        # read the feature to id dictionary
        with open(feature_to_id_dict_serialization_path, "rb") as f:
            feature_to_id_dict = pickle.load(f)

        # read the relevant features
        with open(relevant_features_list_serialization_path, "rb") as f:
            relevant_features = pickle.load(f)

        # parse the tree stucture to table entries
        for i, dt in enumerate(self.data_plane_estimator.estimators_):
            dt_structure = dt.tree_
            # add the table entry for the root node (dummy root node index = 0, real root node index = 1)
            root_feature_name = relevant_features[dt_structure.feature[0]]
            root_feature_id = feature_to_id_dict[root_feature_name]
            root_threshold = int(np.around(dt_structure.threshold[0], 1) * 10)
            # table entry for the root node
            self.write_table_entry(
                table_name_f=f"MyIngress.table_cmp_feature_tree_{i+1}_level_{0}",
                match_fields_f={
                    "meta.current_node_id": 0,
                    "meta.feature_larger_than_thr": 0
                },
                action_name_f="MyIngress.compare_feature",
                action_params_f={
                    "feature_id": root_feature_id,
                    "threshold": root_threshold,
                    "next_node_id": 1,
                    "packets_count": packet_num_in_flow,
                })

            def traversal_tree(node_index, depth, tree_index):
                # if the node is not the leaf node, then generate the rules. Otherwise, do nothing.
                if dt_structure.feature[node_index] != _tree.TREE_UNDEFINED:
                    # get children node index
                    # Cast them from numpy.longlong to int. (why? buildTableEntry of p4infor helper only supports string and int)
                    left_child_index = int(
                        dt_structure.children_left[node_index])
                    right_child_index = int(
                        dt_structure.children_right[node_index])

                    # if the left child is not a leaf node, compare the feature and update the node index
                    if (dt_structure.feature[left_child_index] != _tree.TREE_UNDEFINED):
                        # get the left child node feature name and id
                        left_child_feature_name = relevant_features[
                            dt_structure.feature[left_child_index]]
                        left_child_feature_id = feature_to_id_dict[left_child_feature_name]
                        # get the threshold of left child node
                        # feature value is ten times the original value (improve the precision)
                        left_child_threshold = int(np.around(
                            dt_structure.threshold[left_child_index], 1) * 10)

                        # table entry for the left child node (not leaf node)
                        # index 0 is the index of the dummy root node, thus, the node index has to be added with 1 for each node
                        self.write_table_entry(
                            table_name_f=f"MyIngress.table_cmp_feature_tree_{i+1}_level_{depth}",
                            match_fields_f={
                                "meta.current_node_id": node_index + 1,
                                "meta.feature_larger_than_thr": 1
                            },
                            action_name_f="MyIngress.compare_feature",
                            action_params_f={
                                "feature_id": left_child_feature_id,
                                "threshold": left_child_threshold,
                                "next_node_id": left_child_index,
                                "packets_count": packet_num_in_flow,
                            })

                    # if the left child is a leaf node, classify the flow
                    else:
                        # determine the class of left child node
                        if dt_structure.value[left_child_index][0][0] > dt_structure.value[left_child_index][0][1]:
                            left_child_class_id = 0
                        else:
                            left_child_class_id = 1
                        # keep three decimal place to improve the precision
                        leaf_gini = int(np.around(
                            dt_structure.impurity[left_child_index], 3) * 1000)
                        # table entry for the left child node (leaf node)
                        # index 0 is the index of the dummy root node, thus, the node index has to be added with 1 for each node
                        self.write_table_entry(
                            table_name_f=f"MyIngress.table_cmp_feature_tree_{i+1}_level_{depth}",
                            match_fields_f={
                                "meta.current_node_id": node_index + 1,
                                "meta.feature_larger_than_thr": 1
                            },
                            action_name_f="MyIngress.classify_flow",
                            action_params_f={
                                "tree_index": tree_index,
                                "class": left_child_class_id,
                                "gini_value": leaf_gini
                            })

                    # if the right child is not a leaf node, compare the feature and update the node index
                    if (dt_structure.feature[right_child_index] != _tree.TREE_UNDEFINED):
                        # get the right child node feature name and id
                        right_child_feature_name = relevant_features[
                            dt_structure.feature[right_child_index]]
                        right_child_feature_id = feature_to_id_dict[right_child_feature_name]
                        # get the threshold of right child node
                        # feature value is ten times the original value (improve the precision)
                        right_child_threshold = int(np.around(
                            dt_structure.threshold[right_child_index], 1) * 10)
                        # table entry for the right child node (not leaf node)
                        # index 0 is the index of the dummy root node, thus, the node index has to be added with 1 for each node
                        self.write_table_entry(
                            table_name_f=f"MyIngress.table_cmp_feature_tree_{i+1}_level_{depth}",
                            match_fields_f={
                                "meta.current_node_id": node_index + 1,
                                "meta.feature_larger_than_thr": 2
                            },
                            action_name_f="MyIngress.compare_feature",
                            action_params_f={
                                "feature_id": right_child_feature_id,
                                "threshold": right_child_threshold,
                                "next_node_id": right_child_index,
                                "packets_count": packet_num_in_flow,
                            })

                    # if the right child is a leaf node, classify the flow
                    else:
                        # determine the class of right child node
                        if dt_structure.value[right_child_index][0][0] > dt_structure.value[right_child_index][0][1]:
                            right_child_class_id = 0
                        else:
                            right_child_class_id = 1
                        # keep three decimal place to improve the precision
                        leaf_gini = int(np.around(
                            dt_structure.impurity[right_child_index], 3) * 1000)
                        # table entry for the left right node (leaf node)
                        # index 0 is the index of the dummy root node, thus, the node index has to be added with 1 for each node
                        self.write_table_entry(
                            table_name_f=f"MyIngress.table_cmp_feature_tree_{i+1}_level_{depth}",
                            match_fields_f={
                                "meta.current_node_id": node_index + 1,
                                "meta.feature_larger_than_thr": 2
                            },
                            action_name_f="MyIngress.classify_flow",
                            action_params_f={
                                "tree_index": tree_index,
                                "class": right_child_class_id,
                                "gini_value": leaf_gini
                            })

                    # for debug
                    # feature_name = relevant_features[dt_structure.feature[node_index]]
                    # print(
                    #     f"tree: {tree_index} \nlevel: {depth} \nfeature: {feature_name}")

                    # traverse the tree
                    traversal_tree(
                        left_child_index, depth+1, i+1)
                    traversal_tree(
                        right_child_index, depth+1, i+1)

            # start with the root node with depth 1 (depth 0 is for the dummy root node)
            traversal_tree(0, 1, i+1)
        # write the forwarding table entries
        # the convert will take care of conversion from ipv4 address to integer as well. (in this case, a string should be given)
        self.write_table_entry(
            table_name_f="MyIngress.forward_table",
            match_fields_f={
                "hdr.ipv4.dstAddr": (self._ip2int("10.0.0.1"), 32)
            },
            action_name_f="MyIngress.ipv4_forward",
            action_params_f={
                "port": 0
            })

        self.write_table_entry(
            table_name_f="MyIngress.forward_table",
            match_fields_f={
                "hdr.ipv4.dstAddr": (self._ip2int("10.0.0.3"), 32)
            },
            action_name_f="MyIngress.ipv4_forward",
            action_params_f={
                "port": 1
            })
        print("Installed table entries.")

    def read_counter(self, counter_name, counter_index):
        ''' Read the counter at the specific index.
        '''
        for response in self.switch.ReadCounters(self.p4info_helper.get_counters_id(counter_name), counter_index):
            for entity in response.entities:
                counter = entity.counter_entry
                counter_value = counter.data.packet_count
                return counter_value

    def get_leaf_indexes(self):
        ''' Get all leaf indexes in the random forest
        '''
        leaf_index_list = []
        for i, dt in enumerate(self.data_plane_estimator.estimators_):
            dt_structure = dt.tree_
            leaf_index_list_temp = []

            def traversal_tree(node_index, tree_index):
                if dt_structure.feature[node_index] != _tree.TREE_UNDEFINED:
                    left_child_index = int(
                        dt_structure.children_left[node_index])
                    right_child_index = int(
                        dt_structure.children_right[node_index])
                    traversal_tree(left_child_index, i+1)
                    traversal_tree(right_child_index, i+1)
                else:
                    # all node index has been increased with 1
                    leaf_index_list_temp.append(node_index+1)
            # start traversing the tree
            traversal_tree(0, i+1)
            # add the leaf indexes of this tree to the entire list
            leaf_index_list.append(leaf_index_list_temp)

        return leaf_index_list

    def start_up(self):
        ''' Start up the switch
        '''
        try:
            # Send master arbitration update message to establish this controller as
            # master (required by P4Runtime before performing any other write operation)
            self.switch.MasterArbitrationUpdate()

            # Install the P4 program on the switches
            self.switch.SetForwardingPipelineConfig(p4info=self.p4info_helper.p4info,
                                                    bmv2_json_file_path=self.bmv2_json_path)
            print("Installed P4 Program using SetForwardingPipelineConfig on switch")
        except grpc.RpcError as e:
            printGrpcError(e)
