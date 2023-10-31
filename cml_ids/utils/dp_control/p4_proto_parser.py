#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
