#!/bin/sh

p4_name="temp"

# compile p4 file to json, p4i and p4info
path_p4="p4/${p4_name}.p4"
path_p4info="p4/build/${p4_name}.p4info.txt"
# path_p4_bin="p4/build/${p4_name}.bin"

# compile to p4info
p4c -b bmv2 --arch v1model --std p4-16 -o p4/build ${path_p4} --p4runtime-files ${path_p4info}
# compile to bin file
# p4c -b bmv2 --arch v1model --std p4-16 -o p4/build ${path_p4} --p4runtime-files ${path_p4_bin}

# connect to bmv2

path_json="p4/build/${p4_name}.json"
# sudo simple_switch --debugger --nanolog ipc:///tmp/bm-log.ipc --interface 0@veth2 --interface 1@veth4 ${path_json}

# connect to P4runtime
sudo simple_switch_grpc --debugger --no-p4 --interface 0@veth2 --interface 1@veth4 -- --grpc-server-addr 127.0.0.1:50052 --cpu-port 101