#!/bin/sh

p4_name="dp_ids_switch"
p4_base_path="./cml_ids/p4/"

# compile p4 file to json, p4i and p4info
path_p4="${p4_base_path}${p4_name}.p4"

path_build="${p4_base_path}build/"
path_json="${path_build}${p4_name}.json"
path_p4info="${path_build}${p4_name}.p4info.txt"

# compile to p4info
p4c -b bmv2 --arch v1model --std p4-16 -o ${path_build} ${path_p4} --p4runtime-files ${path_p4info}

# startup switch with p4 program (no controller control)
# sudo simple_switch --nanolog ipc:///tmp/bm-log.ipc --interface 0@veth2 --interface 1@veth4 ${path_json}

# startup switch via P4runtime without p4 program (with controller control)
sudo simple_switch_grpc --no-p4 --interface 0@veth2 --interface 1@veth4 -- --grpc-server-addr 127.0.0.1:50052 --cpu-port 101

