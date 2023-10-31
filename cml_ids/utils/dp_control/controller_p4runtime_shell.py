#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from enum import Enum
import pandas as pd
import pickle
import numpy as np
import threading
import time

from .p4_proto_parser import P4ProtoTxtParser
import p4runtime_sh.shell as sh
from keras.models import load_model
from xgboost import XGBClassifier


class Controller():
    """Controller connected to the P4 switch.

    Attributes
    ----------
    model_nn_dir: saved by calling save() method in keras.
        Dictionary of NN model.
    model_rf_path: .pkl (pickle)
        Path of RF model.
    model_xgb_path: .json 
        Path of XGB model.
    used_features: list
        Features used for prediction.
    number_to_switch: int
        Number of connected switch.
    nn_time_sum: float
        Sum of the prediction time of NN classifier. 
    rf_time_sum: float
        Sum of the prediction time of RF classifier. 
    xgb_time_sum: float
        Sum of the prediction time of XGB classifier. 
    id2name_dict: dict
        Mapping feature ID to name. (ID from proto file)
    """
    # Packet sent to this CPU_PORT will be sent to controller or switch
    CPU_PORT = 101

    # metadata value in the packet deliverd between switch and controller must be string

    # packet type
    PACKET_IN = '1'
    PACKET_OUT = '2'

    # operation code (opcode)
    NO_OP = '0'
    CLASSIFY_REQUEST = '1'
    CLASSIFY_RESPONSE = '2'

    def __init__(self, model_nn_dir, model_rf_path, model_xgb_path, features_path) -> None:
        # load ml models
        self.model_nn = load_model(model_nn_dir)
        print("Loaded NN model.")
        with open(model_rf_path, 'rb') as f:
            self.model_rf = pickle.load(f)
        print("Loaded RF model.")
        self.model_xgb = XGBClassifier()
        self.model_xgb.load_model(model_xgb_path)
        print("Loaded XGB model.")
        self.used_features = pd.read_csv(features_path)["feature_name"].tolist()
        self.number_to_switch = 0
        self.nn_time_sum = 0
        self.rf_time_sum = 0
        self.xgb_time_sum = 0

    def setUp(self, device_grpc_addr, device_id, p4_info_path, p4_bin_path):
        sh.setup(device_id=device_id,
                 grpc_addr=device_grpc_addr,
                 election_id=(0,  1),
                 config=sh.FwdPipeConfig(p4_info_path, p4_bin_path))
        print("Setup the connection to switch.")
        self.packetIn_handler = sh.PacketIn()
        self.pktOut_handler = sh.PacketOut()
        # get the mapping from feature ID to name (ID from proto file)
        proto_parser = P4ProtoTxtParser(p4_info_path)
        self.id2name_dict = proto_parser.get_packet_in_id2name_dict()


    def tearDown(self):
        sh.teardown()

    def send_packet(self, header_dict):
        """Send packet to the switch.

        Parameters
        ---------- 
        header_dict: dict 
            Packet header dictionary containing feature name and value
        """
        for key in header_dict:
            self.pktOut_handler.metadata[key] = header_dict[key]
        self.pktOut_handler.send()

    def get_flow_features(self, pkt):
        """Get flow feature values.

        Parameters
        ----------            
        pkt: 
            An incoming packet from switch.
        
        Returns
        -------
        dict
            Flow feature values.
        """
        packet_features_dict = {}
        for metadata in pkt.packet.metadata:
            feature_id = str(metadata.metadata_id)
            feature_name = self.id2name_dict[feature_id]
            packet_features_dict[feature_name] = int.from_bytes(
                metadata.value, byteorder="big")
        return packet_features_dict

    def show_header(self, pkt):
        """Show the header of packet from switch

        Parameters
        ----------
        pkt:
            An incoming packet from switch.
        """
        for metadata in pkt.packet.metadata:
            feature_id = str(metadata.metadata_id)
            feature_name = self.id2name_dict[feature_id]
            print(
                f"{feature_name}: {int.from_bytes(metadata.value, byteorder='big')}")

    def read_counter(self):
        pass

    def predict_flow(self, pkt, model_weights):
        """Predict the flow entry sent from switch

        Parameters
        ----------
        pkt: 
            An incoming packet from switch.
        """
        self.number_to_switch += 1
        # extract feature values in packet from switch
        feature_dict = {}
        for metadata in pkt.packet.metadata:
            feature_id = str(metadata.metadata_id)
            feature_name = self.id2name_dict[feature_id]
            feature_dict[feature_name] = int.from_bytes(
                metadata.value, byteorder="big")
        # extract flow id
        flow_id = feature_dict["flow_id"]

        # extract feature list fed to NN model
        relevant_feature_dict = {}
        for feature in self.used_features:
            relevant_feature_dict[feature] = feature_dict[feature]
        # print(relevant_feature_dict)

        relevant_feature_df = pd.DataFrame([relevant_feature_dict])

        # predict the label of flow (NN)
        start_timestamp = time.time()
        y_predict_nn = np.array(
            list(map(lambda x: [1 - x[0], x[0]], self.model_nn.predict(relevant_feature_df))))
        end_timestamp = time.time()
        self.nn_time_sum += end_timestamp - start_timestamp

        # predict the label of flow (RF)
        start_timestamp = time.time()
        y_predict_rf = self.model_rf.predict_proba(relevant_feature_df)
        end_timestamp = time.time()
        self.rf_time_sum += end_timestamp - start_timestamp

        # predict the label of flow (XGB)
        start_timestamp = time.time()
        y_predict_xgb = self.model_xgb.predict_proba(relevant_feature_df)
        end_timestamp = time.time()
        self.xgb_time_sum += end_timestamp - start_timestamp

        # compute the final predicted label from each model        
        flow_label = np.average(np.array(
            [y_predict_rf, y_predict_xgb, y_predict_nn]), axis=0, weights=model_weights).argmax(axis=1)[0]

        # send the predicted flow label to switch
        self.pktOut_handler.metadata["packet_type"] = Controller.PACKET_OUT
        self.pktOut_handler.metadata["opcode"] = Controller.CLASSIFY_RESPONSE
        self.pktOut_handler.metadata["flow_id"] = str(flow_id)
        self.pktOut_handler.metadata["class"] = str(flow_label)
        self.pktOut_handler.metadata["reserved"] = '0'
        self.pktOut_handler.send()

    def get_number_flow_to_switch(self):
        return self.number_to_switch

    def get_prediction_time_sum_nn(self):
        return self.nn_time_sum

    def get_prediction_time_sum_rf(self):
        return self.rf_time_sum

    def get_prediction_time_sum_xgb(self):
        return self.xgb_time_sum

    def get_prediction_time_avg_nn(self):
        return self.nn_time_sum / self.number_to_switch

    def get_prediction_time_avg_rf(self):
        return self.rf_time_sum / self.number_to_switch

    def get_prediction_time_avg_xgb(self):
        return self.xgb_time_sum / self.number_to_switch
