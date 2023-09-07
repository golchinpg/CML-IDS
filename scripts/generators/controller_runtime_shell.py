import p4runtime_sh.shell as sh

from enum import Enum
import pandas as pd
import pickle
import numpy as np
import threading
import time


from keras.models import load_model
from xgboost import XGBClassifier


class Controller():
    """Controller connect to switch

    Attributes:
    model_nn_dir: saved calling save() method in keras.
        Dictionary of NN model.
    model_rf_path: file format: pkl (pickle)
        Path of RF model.
    model_xgb_path: file format: json 
        Path of XGB model.
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

    def __init__(self, model_nn_dir, model_rf_path, model_xgb_path) -> None:
        # load ml models
        self.model_nn = load_model(model_nn_dir)
        print("Loaded NN model.")
        with open(model_rf_path, 'rb') as f:
            self.model_rf = pickle.load(f)
        print("Loaded RF model.")
        self.model_xgb = XGBClassifier()
        self.model_xgb.load_model(model_xgb_path)
        print("Loaded XGB model.")
        self.packet_features_dict = {}
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

    def tearDown(self):
        sh.teardown()

    def send_packet(self, header_dict):
        """Send packet to the switch.

        Args:
            header_dict: Packet header dictionary containing feature name and value
        """
        for key in header_dict:
            self.pktOut_handler.metadata[key] = header_dict[key]
        self.pktOut_handler.send()

    def get_flow_features(self, pkt, id2name_dict):
        """Get flow feature values.

        Args:
            pkt: An incoming packet from switch.
            id2name_dict: Feature id to name dictionary.
        """
        for metadata in pkt.packet.metadata:
            feature_id = str(metadata.metadata_id)
            feature_name = id2name_dict[feature_id]
            self.packet_features_dict[feature_name] = int.from_bytes(
                metadata.value, byteorder="big")

    def show_header(self, pkt, id2name_dict):
        """Show the header of packet from switch

        Args:
            pkt: An incoming packet from switch.
            id2name_dict: Feature id to name dictionary.
        """
        for metadata in pkt.packet.metadata:
            feature_id = str(metadata.metadata_id)
            feature_name = id2name_dict[feature_id]
            print(
                f"{feature_name}: {int.from_bytes(metadata.value, byteorder='big')}")

    def read_counter(self):
        pass

    def predict_flow(self, pkt, id2name_dict, relevant_features):
        """Predict the flow entry sent from switch

        Args:
            pkt: An incoming packet from switch.
            id2name_dict: Feature id to name dictionary.    
            relevant_features: Relevant features used to train NN model.
        """
        self.number_to_switch += 1
        # extract feature values in packet from switch
        feature_dict = {}
        for metadata in pkt.packet.metadata:
            feature_id = str(metadata.metadata_id)
            feature_name = id2name_dict[feature_id]
            feature_dict[feature_name] = int.from_bytes(
                metadata.value, byteorder="big")
        # extract flow id
        flow_id = feature_dict["flow_id"]

        # extract feature list fed to NN model
        relevant_feature_dict = {}
        for feature in relevant_features:
            relevant_feature_dict[feature] = feature_dict[feature]
        # print(relevant_feature_dict)

        relevant_feature_df = pd.DataFrame([relevant_feature_dict])

        # predict the label of flow (NN)
        start_timestamp = time.time()
        label_predict_nn = np.array(
            list(map(lambda x: [1 - x[0], x[0]], self.model_nn.predict(relevant_feature_df))))
        end_timestamp = time.time()
        self.nn_time_sum += end_timestamp - start_timestamp

        # predict the label of flow (RF)
        start_timestamp = time.time()
        label_predict_rf = self.model_rf.predict_proba(relevant_feature_df)
        end_timestamp = time.time()
        self.rf_time_sum += end_timestamp - start_timestamp

        # predict the label of flow (XGB)
        start_timestamp = time.time()
        label_predict_xgb = self.model_xgb.predict_proba(relevant_feature_df)
        end_timestamp = time.time()
        self.xgb_time_sum += end_timestamp - start_timestamp

        # compute the final predicted label from each model
        flow_label = np.array([label_predict_nn, label_predict_rf, label_predict_xgb]).mean(
            axis=0).argmax(axis=1)[0]

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


class P4ProtoTxtParser():

    def __init__(self, proto_txt_path) -> None:
        self.dict_proto = self.parse_proto_file(proto_txt_path)

    def parse_proto_file(self, proto_txt_path) -> dict:
        ''' Parse the P4 proto file to dictionary.
        '''
        with open(proto_txt_path, 'r') as file:
            line = file.readline()
            # top dictionary: save the entire proto file
            dict_top = {}
            # level 1 dictionary: save the entry of counter, register, table, action, controller_packet_metadata
            dict_level_1 = {}
            # level 2 dictionary: save the entry under the counter, register, table, action, controller_packet_metadata
            dict_level_2 = {}
            # level 3 dictionary: save the entry of bitstring under type_spec under register
            dict_level_3 = {}
            # level 4 dictionary: save the entry of bit under bitstring under type_spec under the register
            dict_level_4 = {}

            # index indicates in which level
            level_index = 0

            while line:
                if '{' in line:
                    # level 1 entry appears
                    if level_index == 0:
                        # save to assign the key of top dictionary
                        key_top_dict = line.strip(" {\n")
                    elif level_index == 1:
                        # save to assign the key of level 1 dictionary
                        key_level_1 = line.strip(" {\n")
                    elif level_index == 2:
                        # save to assign the key of level 2 dictionary
                        key_level_2 = line.strip(" {\n")
                    elif level_index == 3:
                        # save to assign the key of level 2 dictionary
                        key_level_3 = line.strip(" {\n")
                    # increase the level index
                    level_index += 1
                elif '}' in line:
                    # decrease the leval index
                    level_index -= 1
                    if level_index == 0:
                        # add suffix to key_top_dict of counter, register, table, controller_packet_metadata
                        if key_top_dict in ["counters",
                                            "registers",
                                            "tables",
                                            "actions",
                                            "controller_packet_metadata"]:
                            key_top_dict = key_top_dict + '_' + \
                                dict_level_1["preamble"]["name"]

                        # save the copy of level 1 dictionary.
                        dict_top[key_top_dict] = dict_level_1.copy()
                        # clear the level 1 dictionary to save new content
                        dict_level_1.clear()
                    elif level_index == 1:
                        # add suffix to key_level_1 of the following fields:
                        # - table: match_fields, action_refs
                        # - action: params
                        # - controller_packet_metadata: metadata
                        # ATTENTION: action_refs entry does not have name field. Use ID as suffix for these entries
                        if key_level_1 in ["match_fields",
                                           "action_refs",
                                           "params",
                                           "metadata"]:
                            key_level_1 = key_level_1 + \
                                '_' + dict_level_2["id"]

                        # save the copy of level 2 dictionary.
                        dict_level_1[key_level_1] = dict_level_2.copy()
                        # clear the level 2 dictionary to save new content
                        dict_level_2.clear()
                    elif level_index == 2:
                        # save the copy of level 3 dictionary.
                        dict_level_2[key_level_2] = dict_level_3.copy()
                        # clear the level 3 dictionary to save new content
                        dict_level_3.clear()
                    elif level_index == 3:
                        # save the copy of level 4 dictionary.
                        dict_level_3[key_level_3] = dict_level_4.copy()
                        # clear the level 4 dictionary to save new content
                        dict_level_4.clear()
                else:
                    # split the line to key and value
                    line = line.strip(" \n")
                    key, value = line.split(": ")
                    value = value.strip('"')

                    if level_index == 0:
                        pass
                    elif level_index == 1:
                        dict_level_1[key] = value
                    elif level_index == 2:
                        dict_level_2[key] = value
                    elif level_index == 3:
                        dict_level_3[key] = value
                    elif level_index == 4:
                        dict_level_4[key] = value
                # read new line
                line = file.readline()

        return dict_top

    def get_entry(self, entry_name):
        ''' Extract the given entry in the parsed dictionary.
        '''
        return self.dict_proto[entry_name]

    def get_packet_in_id2name_dict(self) -> dict:
        ''' Map the feature ids of packetIn header fields to names.
        '''
        packet_in_entry_name = "controller_packet_metadata_packet_in"
        packet_in_dict = self.dict_proto[packet_in_entry_name]
        packet_in_id2name_dict = {}
        for key in packet_in_dict.keys():
            if "metadata" in key:
                packet_in_id2name_dict[packet_in_dict[key]
                                       ["id"]] = packet_in_dict[key]["name"].replace("features.", '')
        return packet_in_id2name_dict

    def get_packet_in_name2id_dict(self) -> dict:
        ''' Map the feature names of packetIn header fields to ids.
        '''
        packet_in_entry_name = "controller_packet_metadata_packet_in"
        packet_in_dict = self.dict_proto[packet_in_entry_name]
        packet_in_name2id_dict = {}
        for key in packet_in_dict.keys():
            if "metadata" in key:
                packet_in_name2id_dict[packet_in_dict[key]
                                       ["name"].replace("features.", '')] = packet_in_dict[key]["id"]
        return packet_in_name2id_dict

    def get_packet_in_header(self) -> list:
        ''' Extract the pacektIn header fields name in list.
        '''
        packet_in_entry_name = "controller_packet_metadata_packet_in"
        packet_in_dict = self.dict_proto[packet_in_entry_name]
        packet_in_header_name_list = []
        for key in packet_in_dict.keys():
            if "metadata" in key:
                packet_in_header_name_list.append(
                    packet_in_dict[key]["name"].replace("features.", ''))
        return packet_in_header_name_list

    def get_packet_out_header(self) -> list:
        ''' Extract the pacektOut header fields name in list.
        '''
        packet_out_entry_name = "controller_packet_metadata_packet_out"
        packet_out_dict = self.dict_proto[packet_out_entry_name]
        packet_out_header_name_list = []
        for key in packet_out_dict.keys():
            if "metadata" in key:
                packet_out_header_name_list.append(
                    packet_out_dict[key]["name"].replace("features.", ''))
        return packet_out_header_name_list

    def get_counter_name(self) -> list:
        ''' Extract the counter names in list 
        '''
        counter_name_list = []
        for key in self.dict_proto.keys():
            if "counters" in key:
                counter_name = key.replace("counters_MyIngress.", '')
                counter_name_list.append(counter_name)
        return counter_name_list
