#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
from scapy.all import *


################################## dataset functions ##################################
def cut(path, length):
    if (path is None):
        print('Please give the path of PCAP file. Use -p to input the path')
        exit(1)
    if (length is None):
        print('Please give the length to cut the PCAP file. Use -l to input the length')
        exit(1)
    if length <= 0:
        print("Invalid length. Please give a positive number")
        exit(1)

    pcap = rdpcap(path)
    pcap_size = len(pcap)
    if length > pcap_size:
        print(
            f"The given length exceeds the size of pcap file. Please give the length < {pcap_size}.")
        exit(1)
    else:
        cutted = pcap[: length]
        if ".pcap" in path:
            save_to_path = path[:-5] + f"_top_{length}" + ".pcap"
        else:
            save_to_path = path + f"_top_{length}" + ".pcap"
        wrpcap(save_to_path, cutted)
        print(f'PCAP file has been cutted to the top {length}')


def rewrite(path, addr):
    if (path is None):
        print('Please give the path of PCAP file. Use -p to input the path')
        exit(1)
    if (addr is None):
        print('Please give the destination IP address to rewrite the PCAP file. Use -di to input the destination IP address')
        exit(1)

    pcap = rdpcap(path)
    for p in pcap:
        if p.haslayer(IP):
            p.getlayer(IP).dst = addr
        del (p.chksum)
    wrpcap(path + "_rewritten", pcap)
    print('PCAP file has been rewritten.')


def replay(path, interface):
    if (path is None):
        print('Please give the path of PCAP file. Use -p to input the path')
        exit(1)
    if (interface is None):
        print('Please give the interface to replay the PCAP file. Use -i to input the interface')
        exit(1)

    pcap = rdpcap(path)
    for p in pcap:
        sendp(p, iface=interface)
    print(f'{len(pcap)} packets have been sent')


def dataset_control(args):
    if (args.cut):
        cut(args.path, args.length)
    elif (args.rewrite):
        rewrite(args.path, args.dst_ip)
    elif (args.replay):
        replay(args.path, args.interface)


################################## traffic functions ##################################
def send_tcp(src_if, dst_if, length, src_port=None, dst_port=None):
    if (src_if is None):
        print('Please give the source interface. Use -si to input the source interface')
        exit(1)
    if (dst_if is None):
        print('Please give the destination interface. Use -si to input the destination interface')
        exit(1)
    if (length is None):
        print('Please give the packet length. Use -l to input the length')
        exit(1)

    src_mac = get_if_hwaddr(src_if)
    dst_mac = get_if_hwaddr(dst_if)
    src_ip = get_if_addr(src_if)
    dst_ip = get_if_addr(dst_if)
    pkt = Ether(src=src_mac, dst=dst_mac) / IP(src=src_ip, dst=dst_ip)
    if ((src_port is not None) and (dst_port is not None)):
        pkt = pkt / TCP(sport=src_port, dport=dst_port, flags=0) / \
            Raw(RandString(size=length))
    else:
        pkt = pkt / TCP(flags=0) / Raw(RandString(size=length))
    print(pkt.show())
    sendp(pkt, iface=src_if)


def send_tcp_with_syn(src_if, dst_if, length, src_port=None, dst_port=None):
    if (src_if is None):
        print('Please give the source interface. Use -si to input the source interface')
        exit(1)
    if (dst_if is None):
        print('Please give the destination interface. Use -si to input the destination interface')
        exit(1)
    if (length is None):
        print('Please give the packet length. Use -l to input the length')
        exit(1)

    src_mac = get_if_hwaddr(src_if)
    dst_mac = get_if_hwaddr(dst_if)
    src_ip = get_if_addr(src_if)
    dst_ip = get_if_addr(dst_if)
    pkt = Ether(src=src_mac, dst=dst_mac) / IP(src=src_ip, dst=dst_ip)
    if ((src_port is not None) and (dst_port is not None)):
        pkt = pkt / TCP(sport=src_port, dport=dst_port, flags='S') / \
            Raw(RandString(size=length))
    else:
        pkt = pkt / TCP(flags='S') / Raw(RandString(size=length))
    print(pkt.show())
    sendp(pkt, iface=src_if)


def sniff_my(interface):
    if (interface is None):
        print('Please give the interface to sniff. Use -si to input the interface')
        exit(1)
    print("sniffing on %s" % interface)
    sniff(iface=interface, prn=lambda x: x.show())


def traffic_control(args):
    if (args.tcp):
        send_tcp(args.src_interface, args.dst_interface,
                 args.length, args.src_port, args.dst_port)
    elif (args.tcp_with_syn):
        send_tcp_with_syn(args.src_interface, args.dst_interface,
                          args.length, args.src_port, args.dst_port)
    elif (args.sniff):
        sniff_my(args.src_interface)


################################## parser ##################################
def parsers():
    parser = argparse.ArgumentParser(description='A script')
    subparsers = parser.add_subparsers(help="subparsers")

    ################################## dataset parser ##################################
    subpaerser_dataset = subparsers.add_parser(
        'dataset', help='contains functinos to manipulate pcap dataset')
    subpaerser_dataset.set_defaults(func=dataset_control)

    subpaerser_dataset.add_argument(
        '--path', '-p', type=str, required=True, metavar='', help='path of PCAP file')
    subpaerser_dataset.add_argument(
        '--length', '-l', type=int, metavar='', help='length to cut the PCAP file')
    subpaerser_dataset.add_argument(
        '--dst_ip', '-di', type=str, metavar='', help='destination IP address to rewrite')
    subpaerser_dataset.add_argument(
        '--interface', '-i', type=str, metavar='', help='interface to send the PCAP file')

    group_dataset = subpaerser_dataset.add_mutually_exclusive_group()
    group_dataset.add_argument(
        '--cut', action='store_true', help='cut the PCAP file to a given length')
    group_dataset.add_argument(
        '--rewrite', action='store_true', help='rewrite the PCAP file')
    group_dataset.add_argument(
        '--replay', action='store_true', help='replay the PCAP file')

    ################################## traffic parser ##################################
    subpaerser_traffic = subparsers.add_parser(
        'traffic', help='contains functinos to generate traffic')
    subpaerser_traffic.set_defaults(func=traffic_control)

    subpaerser_traffic.add_argument(
        '--src_interface', '-si', type=str, metavar='', help='source interface to send traffic')
    subpaerser_traffic.add_argument(
        '--dst_interface', '-di', type=str, metavar='', help='destination interface to send traffic')
    subpaerser_traffic.add_argument(
        '--length', '-l', type=int, metavar='', help='length of the packet')
    subpaerser_traffic.add_argument(
        '--src_port', '-sp', type=int, metavar='', help='source port')
    subpaerser_traffic.add_argument(
        '--dst_port', '-dp', type=int, metavar='', help='destination port')

    group_traffic = subpaerser_traffic.add_mutually_exclusive_group()
    group_traffic.add_argument(
        '--tcp', action='store_true', help='send tcp packets')
    group_traffic.add_argument(
        '--tcp_with_syn', action='store_true', help='send tcp pacekts with FIN flag')
    group_traffic.add_argument(
        '--sniff', action='store_true', help='sniff at an interface')

    args = parser.parse_args()
    args.func(args)


################################## control block ##################################
def main():
    None


if __name__ == '__main__':
    parsers()
    main()
