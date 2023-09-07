#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from generators.traffic_generator import TrafficGenerator
from scapy.all import *
import time


src_if = sys.argv[1]
dst_if = sys.argv[2]
src_port = int(sys.argv[3])
dst_port = int(sys.argv[4])
src2dst_packet_num = int(sys.argv[5])
packet_num = 10

traffic_gen_src2dst = TrafficGenerator(
    src_if, dst_if, src_port, dst_port)

traffic_gen_dst2src = TrafficGenerator(
    dst_if, src_if, dst_port, src_port)


def test_21_r():
    traffic_gen_src2dst.send_tcp(10, src2dst_packet_num)
    traffic_gen_dst2src.send_tcp(5000, packet_num - src2dst_packet_num)


def send_packets():
    traffic_gen_src2dst.send_tcp(10, src2dst_packet_num)
    time.sleep(10)
    traffic_gen_dst2src.send_tcp(5000, packet_num - src2dst_packet_num)


if __name__ == "__main__":
    send_packets()
