from scapy.all import *


def filter_pcap_tuesday(pcap_dataset_path, attack_output_path):
    ''' Filter the attack in Tuesday dataset
    '''
    pcap_dataset = rdpcap(pcap_dataset_path)
    pkt_num = len(pcap_dataset)
    print("Finished reading Tuesday pcap dataset.")
    print(f"Tuesday total packet number: {pkt_num}")
    attack_num = 0
    attack_list = []
    for pkt in pcap_dataset:
        if pkt.haslayer(IP):
            src_ip = pkt.getlayer(IP).src
            dst_ip = pkt.getlayer(IP).dst
            if (src_ip == "172.16.0.1") or (dst_ip == "172.16.0.1"):
                attack_num = attack_num + 1
                attack_list.append(pkt)
    wrpcap(attack_output_path, attack_list)
    print(f"Tuesday benign packet number: {pkt_num - attack_num}")
    print(f"Tuesday attack packet number: {attack_num}")


def filter_pcap_wednesday(pcap_dataset_path, attack_output_path):
    ''' Filter the attack in Wednesday dataset
    '''
    pcap_dataset = rdpcap(pcap_dataset_path)
    pkt_num = len(pcap_dataset)
    print("Finished reading Wednesday pcap dataset.")
    print(f"Wednesday packet total number: {pkt_num}")
    attack_num = 0
    attack_list = []
    for pkt in pcap_dataset:
        if pkt.haslayer(IP):
            dst_ip = pkt.getlayer(IP).dst
            if (src_ip == "172.16.0.1") or (dst_ip == "172.16.0.1"):
                attack_num = attack_num + 1
                attack_list.append(pkt)
    wrpcap(attack_output_path, attack_list)
    print(f"Wednesday benign packet number: {pkt_num - attack_num}")
    print(f"Wednesday attack packet number: {attack_num}")


def filter_pcap_thursday(pcap_dataset_path, attack_output_path):
    ''' Filter the attack in Thursday dataset
    '''
    pcap_dataset = rdpcap(pcap_dataset_path)
    pkt_num = len(pcap_dataset)
    print("Finished reading Thurday pcap dataset.")
    print(f"Thurday packet number: {pkt_num}")
    attack_num = 0
    attack_list = []
    for pkt in pcap_dataset:
        if pkt.haslayer(IP):
            src_ip = pkt.getlayer(IP).src
            dst_ip = pkt.getlayer(IP).dst
            if (src_ip == "172.16.0.1") or (dst_ip == "172.16.0.1") or (src_ip == "192.168.10.8") or (dst_ip == "192.168.10.8"):
                attack_num = attack_num + 1
                attack_list.append(pkt)
    wrpcap(attack_output_path, attack_list)
    print(f"Thurday benign packet number: {pkt_num - attack_num}")
    print(f"Thurday attack packet number: {attack_num}")


def filter_pcap_friday(pcap_dataset_path, attack_output_path):
    ''' Filter the attack in Friday dataset
    '''
    pcap_dataset = rdpcap(pcap_dataset_path)
    pkt_num = len(pcap_dataset)
    print("Finished reading Friday pcap dataset.")
    print(f"Friday packet number: {pkt_num}")
    attack_num = 0
    attack_list = []
    for pkt in pcap_dataset:
        if pkt.haslayer(IP):
            src_ip = pkt.getlayer(IP).src
            dst_ip = pkt.getlayer(IP).dst
            if ((src_ip == '192.168.10.12' and dst_ip == '52.6.13.28')
                    or (src_ip == '192.168.10.50' and dst_ip == '172.16.0.1')
                    or (src_ip == '172.16.0.1' and dst_ip == '192.168.10.50')
                    or (src_ip == '192.168.10.17' and dst_ip == '52.7.235.158')
                    or (src_ip == '192.168.10.8' and dst_ip == '205.174.165.73')
                    or (src_ip == '192.168.10.5' and dst_ip == '205.174.165.73')
                    or (src_ip == '192.168.10.14' and dst_ip == '205.174.165.73')
                    or (src_ip == '192.168.10.9' and dst_ip == '205.174.165.73')
                    or (src_ip == '205.174.165.73' and dst_ip == '192.168.10.8')
                    or (src_ip == '192.168.10.15' and dst_ip == '205.174.165.73')):
                attack_num = attack_num + 1
                attack_list.append(pkt)
    wrpcap(attack_output_path, attack_list)
    print(f"Friday benign packet number: {pkt_num - attack_num}")
    print(f"Friday attack packet number: {attack_num}")


# pcap_path = "../../datasets/pcaps/Monday-WorkingHours.pcap"
pcap_path = "../../datasets/pcaps/Tuesday-WorkingHours.pcap"
# pcap_path = "../../datasets/pcaps/Wednesday-WorkingHours.pcap"
# pcap_path = "../../datasets/pcaps/Thursday-WorkingHours.pcap"
# pcap_path = "../../datasets/pcaps/Friday-WorkingHours.pcap"

attack_path = pcap_path[:-5] + "_attack.pcap"

filter_pcap_tuesday(pcap_path, attack_path)
