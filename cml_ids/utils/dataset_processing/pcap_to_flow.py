#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from nfstream import NFStreamer, NFPlugin
import pandas as pd
import numpy as np


class FlowSlicer(NFPlugin):
    """Aggregate packets into flows including the first few packets.

    Implements NFPlugin. Aggregate the features values of the first few packets within a flow. All flow-based features are stored
    within the .udps attributes of flow. 

    Attributes
    -----------
    bidirectional_pkt_count: int 
        Number of packets to aggregate.

    """

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


class Pcap2Flow:
    """Aggregate pcap (packet-based) dataset into flow-based dataset.

    """
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
        print("Start building flow-based dataset.")

    def __map_udps_features(self):
        """Map the udps features names to the normal names in __slots__.

        Returns
        -------
        dict
            The mapping dictionary of the udps feature names to normal feature names.
        """
        feature_dict = {}
        for feature in self.__slots__:
            udps_feature = "udps." + feature
            feature_dict[udps_feature] = feature
        return feature_dict

    def to_flow(self, pcap_path, save_path, flow_extract_type, limit):
        """Aggregate pcap datasets into flow-based datasets.

        Aggregate packets into flows based on the given aggregation type.
            - 'sub-flow': Aggregate the first n packets determined by the 
                given parameter limit.
            - 'complete-flow': Aggregate all packets within a flow.
            - 'packet': Only extract the first packet.

        Parameters
        ----------
        pcap_path: str 
            Path of pcap dataset.
        save_path: str
            Path of the aggregated dataset.
        flow_extract_type: str, {'sub-flow', 'complete-flow', 'packet'}
            Flow aggregation type
        limit: int, optional
            Number of bidirectional packets within a flow to aggregate.
        """
        if flow_extract_type == 'sub-flow':
            print('Extrcating sub-flow information......')
            my_streamer = NFStreamer(source=pcap_path,
                                     n_dissections=0,
                                     accounting_mode=3,
                                     udps=FlowSlicer(
                                         bidirectional_pkt_count=limit),
                                     statistical_analysis=True)
            df = my_streamer.to_pandas(columns_to_anonymize=[])
            # eliminate the non-udps features whose values are computed from the entire flow
            # (the last three features are splt features from plt_analysis)
            df = df.iloc[:, len(self.__slots__):]
            # change the names of columns (delete "udps.")
            df.rename(columns=self.__map_udps_features(), inplace=True)
            # set index=False to avoid reading the first column as Unnamed: 0
            df.to_csv(save_path, index=False)
        elif flow_extract_type == 'complete-flow':
            print('Extracting complete flow information......')
            my_streamer = NFStreamer(source=pcap_path,
                                     n_dissections=0,
                                     accounting_mode=3,
                                     statistical_analysis=True) 
            my_streamer.to_csv(path=save_path, columns_to_anonymize=(),
                               flows_per_file=0,
                               rotate_files=0)
        elif flow_extract_type == 'packet':
            print('Extracting packet-based information......')
            my_streamer = NFStreamer(source=pcap_path,
                                     n_dissections=0,
                                     accounting_mode=3,
                                     udps=FlowSlicer(
                                         bidirectional_pkt_count=1),
                                     statistical_analysis=True) 
            df = my_streamer.to_pandas(columns_to_anonymize=[])
            # eliminate the non-udps features whose values are computed from the entire flow
            # (the last three features are splt features from plt_analysis)
            df = df.iloc[:, len(self.__slots__):]
            # change the names of columns (delete "udps.")
            df.rename(columns=self.__map_udps_features(), inplace=True)
            # set index=False to avoid reading the first column as Unnamed: 0
            df.to_csv(save_path, index=False)
        print(f'Flow extraction is accomplished. Saving path: {save_path}')

        # split features of early statstical analysis.
        """
        split_columns = feature_to_split = [
            'splt_direction', 'splt_ps', 'splt_piat_ms']
        for feature in split_columns:
            split_data = df[feature].str.split(",", n=limit, expand=True)
            for i in range(limit):
                # delete '[', ']' and ' ' in each splitted feature
                df[feature + '_' +
                    str(i+1)] = split_data[i].str.strip("[ ]")
        
        df = df.drop(split_columns, axis=1)
        """
