#!/bin/sh

# add namespaces

namespaces_list=(tuesday wednesday thursday friday)

# delete network namespaces
for ns in ${namespaces_list[@]}
do
    sudo ip netns del ${ns}
done

# setup the network namespaces and interfaces
for ns in ${namespaces_list[@]}
do
    sudo ip netns add ${ns}

    sudo ip netns exec ${ns} ip link set dev lo up

    sudo ip netns exec ${ns} ip link add name ${ns}_veth1 type veth peer name ${ns}_veth2
    sudo ip netns exec ${ns} ip link set dev ${ns}_veth1 up
    sudo ip netns exec ${ns} ip link set dev ${ns}_veth2 up
    sudo ip netns exec ${ns} ip link set ${ns}_veth1 mtu 65535
    sudo ip netns exec ${ns} ip link set ${ns}_veth2 mtu 65535
    sudo ip netns exec ${ns} sysctl net.ipv6.conf.${ns}_veth1.disable_ipv6=1
    sudo ip netns exec ${ns} sysctl net.ipv6.conf.${ns}_veth2.disable_ipv6=1

    sudo ip netns exec ${ns} ip link add name ${ns}_veth3 type veth peer name ${ns}_veth4
    sudo ip netns exec ${ns} ip link set dev ${ns}_veth3 up
    sudo ip netns exec ${ns} ip link set dev ${ns}_veth4 up
    sudo ip netns exec ${ns} ip link set ${ns}_veth3 mtu 65535
    sudo ip netns exec ${ns} ip link set ${ns}_veth4 mtu 65535
    sudo ip netns exec ${ns} sysctl net.ipv6.conf.${ns}_veth3.disable_ipv6=1
    sudo ip netns exec ${ns} sysctl net.ipv6.conf.${ns}_veth4.disable_ipv6=1

    sudo ip netns exec ${ns} ip addr add 10.0.0.1/32 dev ${ns}_veth1
    sudo ip netns exec ${ns} ip addr add 10.0.0.3/32 dev ${ns}_veth3
done

