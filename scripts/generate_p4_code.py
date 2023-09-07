#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from generators.p4_code_generator import P4CodeGenerator
from generators.random_forest_generator import RFGenerator

import pandas as pd
import pickle
from matplotlib import pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report


###########################################################################################################
####################################### Preparation #######################################################
###########################################################################################################

features_relevant_num = 20
pkt_num = 7
feature_id_path = "../dataset/features_with_id.csv"
feature_to_id_dict_serialization_path = "../outputs/serialization/feature_to_id_serialized.pkl"

####################################### le dataset #######################################
dataset_le_path = f"../dataset/relevant_le_{pkt_num}_merged.csv"
feature_importance_le_path = f"../outputs/feature_importance/feature_scores_le_{pkt_num}.csv"
tree_fig_le_path = f"../outputs/tree_structure/"
p4_code_le_path = f"../outputs/p4_code/le_{pkt_num}/"

# serialization paths
rf_serialization_le_path = f"../outputs/serialization/rf_le_{pkt_num}_seralized.pkl"
relevant_features_list_serialization_le_path = f"../outputs/serialization/relevant_features_list_le_{pkt_num}_seralized.pkl"

####################################### equal dataset #######################################
dataset_equal_path = f"../dataset/relevant_equal_{pkt_num}_merged.csv"
feature_importance_equal_path = f"../outputs/feature_importance/feature_scores_equal_{pkt_num}.csv"
tree_fig_equal_path = f"../outputs/tree_structure/equal_{pkt_num}_trees"
p4_code_equal_path = f"../outputs/p4_code/equal_{pkt_num}/"

# serialization paths
rf_serialization_equal_path = f"../outputs/serialization/rf_equal_{pkt_num}_seralized.pkl"
relevant_features_list_serialization_equal_path = f"../outputs/serialization/relevant_features_list_equal_{pkt_num}_seralized.pkl"

####################################### relevant features #######################################
# get the full features used in P4
stddev_features = ['bidirectional_stddev_ps',
                   'src2dst_stddev_ps',
                   'dst2src_stddev_ps',
                   'bidirectional_stddev_piat_ms',
                   'src2dst_stddev_piat_ms',
                   'dst2src_stddev_piat_ms']
# read the feature with id file and remove the unused faetures
full_features = pd.read_csv(feature_id_path)[
    "feature"][14:].tolist()
for f in stddev_features:
    full_features.remove(f)

# get the relevant features
features_relevant = pd.read_csv(feature_importance_equal_path, index_col=0).index.tolist()[
    :features_relevant_num]

with open(relevant_features_list_serialization_equal_path, "wb") as f:
    pickle.dump(features_relevant, f)

###########################################################################################################
##################################### Train estimator #####################################################
###########################################################################################################

rf_gen = RFGenerator()
# train the estimater (best parameters: 3 trees, 4 maximum depth)
rf = RandomForestClassifier(
    n_estimators=3, max_depth=4, n_jobs=-1)
X_train, X_test, y_train, y_test = rf_gen.split_dataset(
    dataset_path=dataset_equal_path)
rf = rf.fit(X_train, y_train)
rf_gen.plot_trees(save_path=tree_fig_equal_path, rf_estimator=rf,
                  features=X_train.columns)
rf_gen.save_rf(rf_serialization_equal_path, rf)
y_predict = rf.predict(X_test)
print(classification_report(y_test, y_predict))


###########################################################################################################
############################### Generate P4 codes und rules ###############################################
###########################################################################################################

p4_gen = P4CodeGenerator(
    rf_estimator=rf, full_features=full_features, relevant_features=features_relevant, save_path=p4_code_equal_path, features_path=feature_id_path)

# save the serialized feature to id dictionary
# p4_gen.save_feature_to_id_dict(feature_to_id_dict_serialization_path)

# DO NOT comment this code line, the rules have to be updated when training new estimator.
# REMEBER copy and paste the generated p4 rules to the according rules file under p4 folder.
p4_gen.generate_p4_rules(packets_count=7)

# p4_gen.generate_mathch_action_tables()

# p4_gen.generate_struct_to_bitstring_action()

# p4_gen.generate_bitstring_to_struct_action()

# p4_gen.generate_compare_feature_action()

# p4_gen.generate_classfication_logic(with_trace=True)
