#!/bin/sh

sudo ip link add name veth1 type veth peer name veth2
sudo ip link set dev veth1 up
sudo ip link set dev veth2 up
sudo ip link set veth1 mtu 65535
sudo ip link set veth2 mtu 65535
sudo sysctl net.ipv6.conf.veth1.disable_ipv6=1
sudo sysctl net.ipv6.conf.veth2.disable_ipv6=1

sudo ip link add name veth3 type veth peer name veth4
sudo ip link set dev veth3 up
sudo ip link set dev veth4 up
sudo ip link set veth3 mtu 65535
sudo ip link set veth4 mtu 65535
sudo sysctl net.ipv6.conf.veth3.disable_ipv6=1
sudo sysctl net.ipv6.conf.veth4.disable_ipv6=1

sudo ip link add name veth5 type veth peer name veth6
sudo ip link set dev veth5 up
sudo ip link set dev veth6 up
sudo ip link set veth5 mtu 65535
sudo ip link set veth6 mtu 65535
sudo sysctl net.ipv6.conf.veth5.disable_ipv6=1
sudo sysctl net.ipv6.conf.veth6.disable_ipv6=1

sudo ip link add name veth7 type veth peer name veth8
sudo ip link set dev veth7 up
sudo ip link set dev veth8 up
sudo ip link set veth7 mtu 65535
sudo ip link set veth8 mtu 65535
sudo sysctl net.ipv6.conf.veth7.disable_ipv6=1
sudo sysctl net.ipv6.conf.veth8.disable_ipv6=1

sudo ip addr add 10.0.0.1/32 dev veth1
sudo ip addr add 10.0.0.3/32 dev veth3
sudo ip addr add 10.0.0.5/32 dev veth5
sudo ip addr add 10.0.0.7/32 dev veth7

# delete the links
# sudo ip link delete veth1
# sudo ip link delete veth3



