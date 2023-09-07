#!/bin/sh

p4_name="temp"

# compile p4 file to json and p4info
path_p4="p4/${p4_name}.p4"
path_p4info="p4/build/${p4_name}.p4info.txt"
# p4c -b bmv2 --arch v1model --std p4-16 -o p4/build ${path_p4} --p4runtime-files ${path_p4info}

path_json="p4/build/${p4_name}.json"

# startup switch with p4 program
# sudo simple_switch --debugger --nanolog ipc:///tmp/bm-log.ipc --interface 0@veth2 --interface 1@veth4 ${path_json}

# startup switch via P4runtime without p4 program 
sudo ip netns exec ${ns} simple_switch_grpc --debugger --no-p4 --interface 0@${ns}_veth2 --interface 1@${ns}_veth4 -- --grpc-server-addr 127.0.0.2:50051 --cpu-port 101


# namespaces_list=(tuesday wednesday thursday friday)
# for ns in ${namespaces_list[@]}
# do
#     sudo ip netns exec ${ns} simple_switch_grpc --debugger --no-p4 --interface 0@${ns}_veth2 --interface 1@${ns}_veth4 -- --grpc-server-addr 127.0.0.1:50052 --cpu-port 101
# done

ns="tuesday"

# sudo ip netns exec ${ns} simple_switch_grpc --debugger --no-p4 --interface 0@${ns}_veth2 --interface 1@${ns}_veth4 -- --grpc-server-addr 127.0.0.2:50051 --cpu-port 101
