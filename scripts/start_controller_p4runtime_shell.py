from generators.controller_runtime_shell import Controller, P4ProtoTxtParser
from generators.evaluation_parser import EvaluationPaser

import pandas as pd
import numpy as np
import pickle
import threading

from keras.models import load_model
from xgboost import XGBClassifier


############################################### setup ###############################################
p4_prog_name = "rf_new"
# p4_prog_name = "temp"

p4_info_path = f"../p4/build/{p4_prog_name}.p4info.txt"
p4_bin_path = f"../p4/build/{p4_prog_name}.json"
switch_grpc_addr = "127.0.0.1:50052"

# ml models paths
controller_models_dir = '../outputs/controller_ml/'

nn_model_dir = controller_models_dir + 'nn_model/'
rf_model_path = controller_models_dir + 'rf_model.pkl'
xgb_model_path = controller_models_dir + "xgb_model.json"

# setup the connection
my_controller = Controller(model_nn_dir=nn_model_dir,
                           model_rf_path=rf_model_path, model_xgb_path=xgb_model_path)
my_controller.setUp(device_grpc_addr=switch_grpc_addr,
                    device_id=0,
                    p4_info_path=p4_info_path,
                    p4_bin_path=p4_bin_path)

# parse the P4 proto text file
proto_parser = P4ProtoTxtParser(p4_info_path)

############################################### process packetIn (part 1) ###############################################
# pathes
flow_length = 8
relevant_features_num = 20
feature_relevant_serialiazation_path = f"../outputs/serialization/balanced_wo_time/feature_relevant_balanced_wo_time_equal_{flow_length}_f_{relevant_features_num}_serialized.pkl"

# get header collection
pkt_in_header_id2name_dict = proto_parser.get_packet_in_id2name_dict()
pkt_in_header_name2id_dict = proto_parser.get_packet_in_name2id_dict()
pkt_out_header_list = proto_parser.get_packet_out_header()

# # load relevant features
# with open(feature_relevant_serialiazation_path, "rb") as f:
#     relevant_feature_list = pickle.load(f)

features_list = ['bidirectional_bytes', 'src2dst_packets', 'src2dst_bytes',
                 'dst2src_packets', 'dst2src_bytes', 'bidirectional_min_ps',
                 'bidirectional_mean_ps', 'bidirectional_max_ps', 'src2dst_min_ps',
                 'src2dst_max_ps', 'dst2src_min_ps', 'dst2src_max_ps',
                 'bidirectional_syn_packets', 'bidirectional_cwr_packets',
                 'bidirectional_ece_packets', 'bidirectional_urg_packets',
                 'bidirectional_ack_packets', 'bidirectional_psh_packets',
                 'bidirectional_rst_packets', 'bidirectional_fin_packets',
                 'src2dst_syn_packets', 'src2dst_cwr_packets', 'src2dst_ece_packets',
                 'src2dst_urg_packets', 'src2dst_ack_packets', 'src2dst_psh_packets',
                 'src2dst_rst_packets', 'src2dst_fin_packets', 'dst2src_syn_packets',
                 'dst2src_cwr_packets', 'dst2src_ece_packets', 'dst2src_urg_packets',
                 'dst2src_ack_packets', 'dst2src_psh_packets', 'dst2src_rst_packets',
                 'dst2src_fin_packets', 'splt_ps_1', 'splt_ps_2', 'splt_ps_3',
                 'splt_ps_4', 'splt_ps_5', 'splt_ps_6', 'splt_ps_7', 'splt_ps_8',
                 'splt_direction_1_1', 'splt_direction_2_1', 'splt_direction_2_2',
                 'splt_direction_3_1', 'splt_direction_3_2', 'splt_direction_4_1',
                 'splt_direction_4_2', 'splt_direction_5_1', 'splt_direction_5_2',
                 'splt_direction_6_1', 'splt_direction_6_2', 'splt_direction_7_1',
                 'splt_direction_7_2', 'splt_direction_8_1', 'splt_direction_8_2']

############################################### process packetIn (part 2) ###############################################
# sniff the packets from switch
pktIn_handler = my_controller.packetIn_handler
pktIn_handler.my_sniff(lambda pkt: my_controller.predict_flow(
    pkt, pkt_in_header_id2name_dict, features_list))
