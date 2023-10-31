#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append("./cml_ids/")

import pandas as pd
import numpy as np
import pickle
import threading
from keras.models import load_model
from xgboost import XGBClassifier
from utils.dp_control.controller_p4runtime_shell import Controller
from utils.dp_control.p4_proto_parser import P4ProtoTxtParser


############################################### setup ###############################################
# P4 pathes
p4_prog_name = "dp_ids_switch"

p4_info_path = f"./cml_ids//p4/build/{p4_prog_name}.p4info.txt"
p4_bin_path = f"./cml_ids//p4/build/{p4_prog_name}.json"
switch_grpc_addr = "127.0.0.1:50052"

# used features
features_path = "./cml_ids//base_files/used_features.csv"

# ml models paths
controller_ml_models_dir = "./cml_ids//ml_models/cp_ids_models/"

nn_model_dir = controller_ml_models_dir + 'nn_model/'
rf_model_path = controller_ml_models_dir + 'rf_cp_ids_model.pkl'
xgb_model_path = controller_ml_models_dir + "xgb_model.json"

# setup the connection
my_controller = Controller(model_nn_dir=nn_model_dir,
                           model_rf_path=rf_model_path, model_xgb_path=xgb_model_path, features_path=features_path)
my_controller.setUp(device_grpc_addr=switch_grpc_addr,
                    device_id=0,
                    p4_info_path=p4_info_path,
                    p4_bin_path=p4_bin_path)

# parse the P4 proto text file
proto_parser = P4ProtoTxtParser(p4_info_path)

############################################### process packetIn ###############################################

model_weights = [1.9, 2.5, 1]
# sniff the packets from switch
pktIn_handler = my_controller.packetIn_handler
pktIn_handler.my_sniff(
    lambda pkt: my_controller.predict_flow(pkt, model_weights))
