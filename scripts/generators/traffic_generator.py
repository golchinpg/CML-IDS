from scapy.all import *
import time


class TrafficGenerator:

    sleep_timeout_s = 0.01

    def __init__(self, src_interface, dst_interface, src_port=None, dst_port=None):
        self.src_if = src_interface
        self.src_mac = get_if_hwaddr(src_interface)
        self.dst_mac = get_if_hwaddr(dst_interface)
        self.src_ip = get_if_addr(src_interface)
        self.dst_ip = get_if_addr(dst_interface)
        self.src_port = src_port
        self.dst_port = dst_port

    def send_tcp(self, length, times):
        pkt = Ether(src=self.src_mac, dst=self.dst_mac) / \
            IP(src=self.src_ip, dst=self.dst_ip)
        if ((self.src_port is not None) and (self.dst_port is not None)):
            pkt = pkt / TCP(sport=self.src_port, dport=self.dst_port, flags=0) / \
                Raw(RandString(size=length))
        else:
            pkt = pkt / TCP(flags=0) / Raw(RandString(size=length))
        print(pkt.show())
        for i in range(times):
            time.sleep(TrafficGenerator.sleep_timeout_s)
            sendp(pkt, iface=self.src_if)

    def send_tcp_with_syn(self, length, times):
        pkt = Ether(src=self.src_mac, dst=self.dst_mac) / \
            IP(src=self.src_ip, dst=self.dst_ip)
        if ((self.src_port is not None) and (self.dst_port is not None)):
            pkt = pkt / TCP(sport=self.src_port, dport=self.dst_port, flags='S') / \
                Raw(RandString(size=length))
        else:
            pkt = pkt / TCP(flags='S') / Raw(RandString(size=length))
        print(pkt.show())
        for i in range(times):
            time.sleep(TrafficGenerator.sleep_timeout_s)
            sendp(pkt, iface=self.src_if)
