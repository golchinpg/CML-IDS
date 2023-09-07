#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sklearn.tree import _tree
import pandas as pd
import numpy as np
import pickle


class P4CodeGenerator():

    def __init__(self, rf_estimator, full_features, relevant_features, save_path, features_path) -> None:
        self.rf_estimator = rf_estimator
        self.full_features = full_features
        self.relevant_features = relevant_features
        self.save_path = save_path
        self.feature_to_id_dict = {}
        self.id_to_feature_dict = {}
        self._init_dicts(features_path)
        print("P4 code generator")

    def _feature_map(self, feature, id):
        self.feature_to_id_dict[feature] = id
        self.id_to_feature_dict[id] = feature

    def _init_dicts(self, features_path):
        df = pd.read_csv(features_path)
        df.apply(lambda x: self._feature_map(x[0], x[1]), axis=1)

    def save_feature_to_id_dict(self, dict_serialization_path):
        ''' Save the serialized feature to id dictionary.
        '''
        with open(dict_serialization_path, "wb") as f:
            pickle.dump(self.feature_to_id_dict, f)

    def generate_struct_to_bitstring_action(self):
        output_str = '''
        /**
        * convert struct to bitstring, in order to store the states in the register
        **/
        action struct_to_bitstring() {
            meta.bitstring = meta.flow.flow_id ++
                             meta.flow.src_ipv4_addr ++ 
                             meta.flow.dst_ipv4_addr ++ 
                             meta.flow.src_port ++ 
                             meta.flow.dst_port ++ 
                             meta.flow.protocol ++ 
                             meta.flow.packet_8th_seen_ms ++ 
                             meta.flow.stored ++
                             meta.flow.class ++
                             meta.flow.classified ++
                             meta.flow.class_tree_1 ++
                             meta.flow.classified_tree_1 ++
                             meta.flow.class_tree_2 ++
                             meta.flow.classified_tree_2 ++
                             meta.flow.class_tree_3 ++
                             meta.flow.classified_tree_3 ++ '''

        for feature in self.full_features:
            temp_str = f'''
                             meta.flow.features.{feature} ++'''
            output_str = output_str + temp_str

        output_str = output_str[:-3] + "; \n        }"
        file_name = "p4_struct_to_bitstring_action.txt"
        fh = open(self.save_path + file_name, 'w')
        fh.write(output_str)
        fh.close()
        print("Generated struct to bistring code.")

    def generate_bitstring_to_struct_action(self):
        flow_time_bits_str = "FLOW_TIME_BITS"
        flow_bytes_bits_str = "FLOW_BYTES_BITS"
        flow_count_bits_str = "FLOW_COUNT_BITS"
        flow_splt_direction_bits_str = "FLOW_SPLT_DIRECTION_BITS"
        # flow entry features with 1 bit length
        flow_entry_1_bit_features = ["stored",
                                     "class",
                                     "classified",
                                     "class_tree_1",
                                     "classified_tree_1",
                                     "class_tree_2",
                                     "classified_tree_2",
                                     "class_tree_3",
                                     "classified_tree_3"]
        # title of the action, the first 2 flow entry states (no 1 bit)
        output_str = '''
            /**
            * convert bit string to struct
            **/
            action bitstring_to_struct() {
                // only constant can be assigned to the slicing index

                /************************* states of flow entry ***********************/
                const int lowerBound_0 = FLOW_SIZE_BITS - FLOW_ID_BITS;
                meta.flow.flow_id =
                    meta.bitstring[(lowerBound_0+FLOW_ID_BITS-1):lowerBound_0];

                const int lowerBound_1 = lowerBound_0 - 32;
                meta.flow.src_ipv4_addr =
                    meta.bitstring[lowerBound_1+31:lowerBound_1];

                const int lowerBound_2 = lowerBound_1 - 32;
                meta.flow.dst_ipv4_addr =
                    meta.bitstring[lowerBound_2+31:lowerBound_2];

                const int lowerBound_3 = lowerBound_2 - 16;
                meta.flow.src_port =
                    meta.bitstring[lowerBound_3+15:lowerBound_3];

                const int lowerBound_4 = lowerBound_3 - 16;
                meta.flow.dst_port =
                    meta.bitstring[lowerBound_4+15:lowerBound_4];

                const int lowerBound_5 = lowerBound_4 - 8;
                meta.flow.protocol =
                    meta.bitstring[lowerBound_5+7:lowerBound_5];

                const int lowerBound_6 = lowerBound_5 - FLOW_TIME_BITS;
                meta.flow.packet_8th_seen_ms =
                    meta.bitstring[lowerBound_6+FLOW_TIME_BITS-1:lowerBound_6];'''

        # flow entry features with 1_bit feature (class, classified......)
        index = 7
        for feature in flow_entry_1_bit_features:
            temp_str = '''

                const int lowerBound_{0} = lowerBound_{1} - 1;
                meta.flow.{2} =
                    meta.bitstring[lowerBound_{0}:lowerBound_{0}];'''.format(index, index-1, feature)
            output_str = output_str + temp_str
            index = index + 1

        output_str = output_str + '''
        

                /************************* features ***********************/'''

        for feature in self.full_features:
            # map the type of bits length of features
            if ("ms" in feature):
                type_bits_str = flow_time_bits_str
            elif ("bytes" in feature):
                type_bits_str = flow_bytes_bits_str
            elif ("packets" in feature):
                type_bits_str = flow_count_bits_str
            elif ("ps" in feature and "psh" not in feature):
                type_bits_str = flow_bytes_bits_str
            elif ("protocol" in feature):
                type_bits_str = "1"
            elif ("splt_direction" in feature):
                type_bits_str = flow_splt_direction_bits_str

            temp_str = '''

                const int lowerBound_{0} = lowerBound_{1} - {2};
                meta.flow.features.{3} =
                    meta.bitstring[lowerBound_{0}+{2}-1:lowerBound_{0}];'''.format(index, index-1, type_bits_str, feature)
            output_str = output_str + temp_str
            index = index + 1

        output_str = output_str + "\n           }"
        file_name = "p4_bitstring_to_struct_action.txt"
        fh = open(self.save_path + file_name, 'w')
        fh.write(output_str)
        fh.close()
        print("Generated bistring to struct code.")

    def generate_compare_feature_action(self):
        output_str = f'''
            if (feature_id == FeatureId.{self.relevant_features[0]}_id)
                current_feature = (bit<MAX_FEATURE_SIZE_BITS>) meta.flow.features.{self.relevant_features[0]};'''

        for feature in self.relevant_features[1:]:
            temp_str = f'''
            else if (feature_id == FeatureId.{feature}_id)
                current_feature = (bit<MAX_FEATURE_SIZE_BITS>) meta.flow.features.{feature};'''
            output_str = output_str + temp_str

        # temp_str = '''

        #     // compare the value of the selected feature to the given threshold
        #     // feature_larger_than_thr = 0: feature value does not be compared
        #     // feature_larger_than_thr = 1: feature value is less than threshold
        #     // feature_larger_than_thr = 2: feature value is larger than threshold
        #     if ((current_feature * 10) <= threshold)
        #         meta.feature_larger_than_thr = 1;
        #     else
        #         meta.feature_larger_than_thr = 2;'''
        # output_str = output_str + temp_str + "\n        }"

        file_name = "p4_compare_feature_action.txt"
        fh = open(self.save_path + file_name, 'w')
        fh.write(output_str)
        fh.close()
        print("Generated compare feature action code")

    def generate_mathch_action_tables(self):
        ''' Generate match action tables in p4
        '''
        output_str = ""
        trees = self.rf_estimator.estimators_
        for i in range(len(trees)):
            for depth in range(trees[i].max_depth+1):
                output_str = output_str + """
                table table_cmp_feature_tree_{0}_level_{1} {{
                    key = {{
                        meta.current_node_id: exact;
                        meta.feature_larger_than_thr: exact;
                    }}
                    actions = {{
                        compare_feature;
                        classify_flow;
                    }}
                    size = 100;
                }}\n""".format(i+1, depth)
            output_str = output_str + "\n"

        file_name = "p4_match_action_tables_action.txt"
        fh = open(self.save_path + file_name, 'w')
        fh.write(output_str)
        fh.close()
        print("Generated match action table code")

    def generate_classfication_logic(self, with_trace=False):
        ''' Generate the random forest classification logic block
        '''
        output_str = ""
        trees = self.rf_estimator.estimators_

        if with_trace:
            for i in range(len(trees)):
                tree_index = i + 1
                output_str = output_str + f'''

                        // tree {i+1}
                        table_cmp_feature_tree_{tree_index}_level_0.apply();
                        larger_than_thr_l1_tree_{tree_index}_register.write(0, meta.feature_larger_than_thr);
                        current_node_id_l1_tree_{tree_index}_register.write(0, meta.current_node_id);'''

                for depth in range(trees[i].max_depth):
                    output_str = output_str + '''
                        if (meta.flow.classified_tree_{0} == 0) {{
                            table_cmp_feature_tree_{0}_level_{1}.apply();
                            larger_than_thr_l{1}_tree_{0}_register.write(0, meta.feature_larger_than_thr);
                            current_node_id_l{1}_tree_{0}_register.write(0, meta.current_node_id);
                        }}'''.format(tree_index, depth+1)
                file_name = "p4_random_forest_classification_logic_with_trace.txt"
        else:
            for i in range(len(trees)):
                tree_index = i + 1
                output_str = output_str + f'''

                        // tree {i+1}
                        table_cmp_feature_tree_{tree_index}_level_0.apply();'''

                for depth in range(trees[i].max_depth):
                    output_str = output_str + '''
                        if (meta.flow.classified_tree_{0} == 0) {{
                            table_cmp_feature_tree_{0}_level_{1}.apply();
                        }}'''.format(tree_index, depth+1)
            file_name = "p4_random_forest_classification_logic.txt"

        fh = open(self.save_path + file_name, 'w')
        fh.write(output_str)
        fh.close()
        print("Generated classification logic code")

    def generate_p4_rules(self):
        ''' Generate the rules to the p4 switch
        '''
        rules = ""
        for i, dt in enumerate(self.rf_estimator.estimators_):
            dt_structure = dt.tree_
            # add the rule for the dummy root node (dummy root node index = 0, real root node index = 1)
            root_feature_name = self.relevant_features[dt_structure.feature[0]]
            root_feature_id = self.feature_to_id_dict[root_feature_name]
            root_threshold = int(np.around(dt_structure.threshold[0], 1) * 10)
            dummy_node_rule = f"table_add table_cmp_feature_tree_{i+1}_level_{0} compare_feature 0 0 => {root_feature_id} {root_threshold} 1\n"
            rules = rules + dummy_node_rule

            def traversal_tree(node_index, depth, rules, tree_index):
                # if the node is not the leaf node, then generate the rules. Otherwise, do nothing.
                if dt_structure.feature[node_index] != _tree.TREE_UNDEFINED:
                    # get children node index
                    left_child_index = dt_structure.children_left[node_index]
                    right_child_index = dt_structure.children_right[node_index]

                    # if the left child is not a leaf node, compare the feature and update the node index
                    if (dt_structure.feature[left_child_index] != _tree.TREE_UNDEFINED):
                        # get the left child node feature name and id
                        left_child_feature_name = self.relevant_features[
                            dt_structure.feature[left_child_index]]
                        left_child_feature_id = self.feature_to_id_dict[left_child_feature_name]
                        # get the threshold of left child node
                        # feature value is ten times the original value (improve the precision)
                        # the time unit is different to the unit in P4
                        left_child_threshold = int(np.around(
                            dt_structure.threshold[left_child_index], 1) * 10)
                        # index 0 is the index of the dummy root node, thus, the node index has to be added with 1 for each node
                        rules = rules + \
                            f"table_add table_cmp_feature_tree_{i+1}_level_{depth} compare_feature {node_index+1} {1} => {left_child_feature_id} {left_child_threshold} {left_child_index+1}\n"

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
                        rules = rules + \
                            f"table_add table_cmp_feature_tree_{i+1}_level_{depth} classify_flow {node_index+1} {1} => {tree_index} {left_child_class_id} {leaf_gini} {left_child_index+1}\n"

                    # if the right child is not a leaf node, compare the feature and update the node index
                    if (dt_structure.feature[right_child_index] != _tree.TREE_UNDEFINED):
                        # get the right child node feature name and id
                        right_child_feature_name = self.relevant_features[
                            dt_structure.feature[right_child_index]]
                        right_child_feature_id = self.feature_to_id_dict[right_child_feature_name]
                        # get the threshold of right child node
                        # feature value is ten times the original value (improve the precision)
                        # the time unit is different to the unit in P4
                        right_child_threshold = int(np.around(
                            dt_structure.threshold[right_child_index], 1) * 10)
                        # index 0 is the index of the dummy root node, thus, the node index has to be added with 1 for each node
                        rules = rules + \
                            f"table_add table_cmp_feature_tree_{i+1}_level_{depth} compare_feature {node_index+1} {2} => {right_child_feature_id} {right_child_threshold} {right_child_index+1}\n"

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
                        rules = rules + \
                            f"table_add table_cmp_feature_tree_{i+1}_level_{depth} classify_flow {node_index+1} {2} => {tree_index} {right_child_class_id} {leaf_gini} {right_child_index+1}\n"

                    # traverse the tree
                    rules = traversal_tree(
                        left_child_index, depth + 1, rules, i+1)
                    rules = traversal_tree(
                        right_child_index, depth + 1, rules, i+1)

                return rules

            # start with the root node with depth 1 (depth 0 is for the dummy root node)
            rules = traversal_tree(0, 1, rules, i+1)

        # add the forwarding rules for two ports.
        forward_rules = "table_add forward_table ipv4_forward 10.0.0.1/32 => 0\ntable_add forward_table ipv4_forward 10.0.0.3/32 => 1"
        rules = rules + forward_rules
        file_name = "rf_rules.txt"
        fh = open(self.save_path + file_name, 'w')
        fh.write(rules)
        fh.close()
        print("Generated P4 rules.")
