# Notes

## NFStream

- If there is only one packet in a flow, the values of min_piat_ms and min_ps are 0. That should be consistent with p4 code.

## P4

- Duplicated declaration is not allowed.

- register_write is not allowed under conditional execution in actions.

- P4 standard_metadata.ingress_global_timestamp is in microsecond, time and ITA features of NFStream are in millisecond. The units should be unified.

- variable name can not start with number.

- Use **simple_switch_grpc** to bind the controller with the switch via grpc using protobuf format (Google Protocol Buffers).

- Communication between P4 switch and P4runtime controller only support string and int data format.

- Bit shifting may cause **zero** problem, if the bit length is not sufficient. e.g., (bit<4>) 1000 left shifting 1 bit leads to (bit<4>) 0000. The solution is cast the value to larger bit length before opering bit shifting. (bit<5>) 1000 << 1 => (bit<5>) 10000.

- The longest bit length supported by P4 is 2048.

- BMv2 target only supports headers with fields totaling a multiple of 8 bits.

## PacketIO via P4runtime

- PacketIn indicates packets sent from switch to controller (packet in from the controller view).

- PacketOut indicates pacekts sent from controller to switch (packet out from the controller view).

- PacketIn and PacketOut headers should be set in P4 program with annotations @controller_header("packet_in") or @controller_header("packet_out").

- The PacketIn header should be set to valid in P4, when switch sends pacekts to the controller. setValid() should be excuted before modifying header values. Otherwise, the header value will not be modified.

- Big-Endian is used to save values.

- The length of each field in packetIn header should be a multiple of 8 bits. The value of received pacekt are represented in bytes in controller.

## Tcpreplay

- Error: Unable to send packet: Error with PF_PACKET send() []: Message too long (errno = 90)  
  Fixed by: Increase the allowed MTU of the network interface

- replay pcap with the original speed

  ```
   sudo tcpreplay -i veth1 -v {pcap file}
  ```

## P4runtime

- > **Q: Exception**  
  > grpc._channel._InactiveRpcError: <_InactiveRpcError of RPC that terminated with:  
  > status = StatusCode.UNKNOWN  
  > details = ""
  > debug_error_string = "{"created":"@1669907521.300671577",  
  > "description":"Error received from peer ipv4:127.0.0.1:50052",  
  > "file":"src/core/lib/surface/call.cc",  
  > "file_line":1074,"grpc_message":"",  
  > "grpc_status":2}"  
  > **A:** Check the values of match fields, the values for a single table entry should be different.

## Implementation

- bidirectional_packets feature must been added into feature updates, because it's used to check the first n packets.

- incompatible features:
  - stddev features
  - time features ?
  - bidirectional_mean features ?

- Hash Collision Algorithm (one registers)
  - if an incoming packet has hash collision:
    - compute the src<->src flow id
    - if the src<->src flow id exists in the hash_collision_flow_buffer:
      - if the existing time exceeds the TIMEOUT:
        - expire this flow entry in hash_collision_flow_buffer
      - else:
        - do nothing (this packet is a src2dst pacekt which belongs to a flow in the hash_collision_flow_buffer)
    - else:
      - compute the src<->dst flow id
      - if the src<->dst flow id is in hash_collision_flow_buffer:
        - if the existing time exceeds the TIMEOUT:
          - expire this flow entry in hash_collision_flow_buffer
        - else:
          - do nothing (this packet is a dst2src pacekt which belongs to a flow in the hash_collision_flow_buffer)
      - else:
        - it's a new flow with hash collision; count the number of flows with hash collision; store this flow entry in hash_collision_flow_buffer.

- Hash Collision Algorithm (two registers)
  - if an incoming packet has hash collision:
    - compute the src<->src flow id by crc32
    - if the src<->src flow id is in hash_collision_flow_crc32_register:
      - if the existing time exceeds the TIMEOUT:
        - expire this flow entry in hash_collision_flow_crc32_register
      - else:
        - do nothing (this packet is a src2dst pacekt which belongs to a flow in the hash_collision_flow_crc32_register)
    - else:
      - compute the src<->dst flow id by crc32
      - if the src<->dst flow id is in hash_collision_flow_crc32_register:
        - if the existing time exceeds the TIMEOUT:
          - expire this flow entry in hash_collision_flow_crc32_register
        - else:
          - do nothing (this packet is a dst2src pacekt which belongs to a flow in the hash_collision_flow_crc32_register)

      - else:
        - compute the src<->src flow id by crc16
        - if the src<->src flow id is in hash_collision_flow_crc16_register:
          - if the existing time exceeds the TIMEOUT:
            - expire this flow entry in hash_collision_flow_crc16_register
          - else:
            - do nothing (this packet is a src2dst packet which belongs to a flow in the hash_collision_flow_crc16_register)
        - else:
          - compute the src<->dst flow id by crc16
          - if the src<->dst flow id is in hash_collision_flow_crc16_register:
            - if the existing time exceeds the TIMEOUT:
              - expire this flow entry in hash_collision_flow_crc16_register
            - else:
              - do nothing (this packet is a src2dst packet which belongs to a flow in the hash_collision_flow_crc16_register)

- else

            -

## Evaluation

- RF estimator (balanced, equal 7): Almost all attack flows fell on the decision (001) and flows are sent to the controller.

## Git

- Get the latest version of the remote repository ignoring the local changes

  ```
    git fetch --all
    git reset --hard origin/<branch name>
    git pull
  ```
