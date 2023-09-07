/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>


/* CONSTANTS */

const bit<16>   TYPE_IPV4 = 0x800;
const bit<8>    TYPE_TCP = 6;
const bit<8>    TYPE_UDP = 17;

/************************ header field constants ************************/
/************************************************************************/
#define ETHERNET_HAEDER_LENGTH 14
#define IPV4_HEADER_LENGTH 20
#define UDP_HEADER_LENGTH 8

/************************ constants for flow feature bits ************************/
/*********************************************************************************/
// FLOW_SIZE_BITS has to adapt to the total bit length of flow struct.
// If the length is incorrect, the console will return error and give the correct value.
#define FLOW_SIZE_BITS  1131
#define FLOW_ID_BITS 32
#define FLOW_STORE_BITS 2
#define FLOW_TIME_BITS 48
#define FLOW_BYTES_BITS 40
#define FLOW_COUNT_BITS 4
#define FLOW_PACKET_SIZE_BITS 40

// MAX_FEATURE_SIZE_BITS has to be 4 bits larger than the maximal bit length of features.
// (increase one-decimal precision)
#define MAX_FEATURE_SIZE_BITS 52
#define FEATURE_ID_BITS 13
#define NODE_ID_BITS 8

/************************ other constants ************************/
/*****************************************************************/
// size of register to save flow features
#define FLOW_BUCKET 1000000
// number of bidirectional packet which is considered to classify flow
#define USED_PACKETS 7
// timeout to expire flow entries in the register (maximum bidirectional duration of dataset is 1799965000 microseconds)
// set the timeout to 40 mins == 2400000000 microseconds
#define TIMEOUT_EXPIRATION 2400000000

// the maxmum gini value is 0.5 (2 classes).
// This value has been amplified by a factor of 1000 to improve the precision from Python.
// needs 9 bits to store the maximum value 500
#define GINI_VALUE_BITS 9
// The maximum value of the sum of three gini value is 1500.   
#define GINI_VALUE_THRESHOLD 1500

// Packet with the same egress port of CPU_PORT is sent to controller.
// Packet from controller enters switch via CPU_PORT
#define CPU_PORT 101

#define CONTROLLER_MESSAGE_BITS 8


/*************************************************************************
*********************** H E A D E R S  ***********************************
*************************************************************************/

typedef bit<9>  egressSpec_t;
typedef bit<48> macAddr_t;
typedef bit<32> ip4Addr_t;

// packetIn is the packet sent from switch to controller. (from controller view)
// packetOut is the packet sent from controller to switch. (from controller view)
enum bit<CONTROLLER_MESSAGE_BITS> ControllerPacketType_t {
    PACKET_IN       = 1,
    PACKET_OUT      = 2
}

enum bit<CONTROLLER_MESSAGE_BITS> ControllerOpcode_t {
    NO_OP               = 0,
    CLASSIFY_REQUEST    = 1,
    CLASSIFY_RESPONSE   = 2
}



header ethernet_t {
    macAddr_t   dstAddr;
    macAddr_t   srcAddr;
    bit<16>     etherType;
}

header ipv4_t {
    bit<4>      version;
    bit<4>      ihl;
    bit<8>      diffserv;
    bit<16>     totalLen;
    bit<16>     identification;
    bit<3>      flags;
    bit<13>     fragOffset;
    bit<8>      ttl;
    bit<8>      protocol;
    bit<16>     hdrChecksum;
    ip4Addr_t   srcAddr;
    ip4Addr_t   dstAddr;
}

header udp_t {
    bit<16>     srcPort;
    bit<16>     dstPort;
    bit<16>     len;
    bit<16>     checksum;
}

header tcp_t{
    bit<16>     srcPort;
    bit<16>     dstPort;
    bit<32>     seqNo;
    bit<32>     ackNo;
    bit<4>      dataOffset;
    bit<4>      res;
    bit<1>      cwr;
    bit<1>      ece;
    bit<1>      urg;
    bit<1>      ack;
    bit<1>      psh;
    bit<1>      rst;
    bit<1>      syn;
    bit<1>      fin;
    bit<16>     window;
    bit<16>     checksum;
    bit<16>     urgentPtr;
}

// feature struct
struct features_t {
    bit<8>        bidirectional_packets;
    bit<32>       bidirectional_bytes;
}


@controller_header("packet_in")
header packet_in_header_t {
    bit<FLOW_ID_BITS>       flow_id;
    ControllerPacketType_t  packet_type;  
    ControllerOpcode_t      opcode;
    bit<8>                  reserved;
    bit<1>                  flag_1;
    bit<1>                  flag_2;
    bit<1>                  flag_3;
    bit<1>                  flag_4;
    bit<1>                  flag_5;
    bit<1>                  flag_6;
    bit<1>                  flag_7;
    bit<1>                  flag_8;
    bit<8>                  flag_9;
    bit<8>                  flag_10;
    features_t              features;
}

@controller_header("packet_out")
header packet_out_header_t {
    bit<FLOW_ID_BITS>       flow_id;
    ControllerPacketType_t  packet_type;  
    ControllerOpcode_t      opcode;
    bit<1>                  class;
    bit<7>                  reserved;
}
 
struct metadata {
    features_t              features;

}

struct headers {
    ethernet_t  ethernet;
    ipv4_t      ipv4;
    udp_t       udp;
    tcp_t       tcp;
    packet_out_header_t pkt_out;
    packet_in_header_t  pkt_in;
}

/*************************************************************************
*********************** P A R S E R  ***********************************
*************************************************************************/

parser MyParser(packet_in packet,
                out headers hdr,
                inout metadata meta,
                inout standard_metadata_t standard_metadata) {

    state start {
        transition parse_ingress_port;
    }

    state parse_ingress_port {
        transition select(standard_metadata.ingress_port) {
            CPU_PORT: parse_packet_from_controller;
            default:parse_ethernet;
        }
    }

    state parse_packet_from_controller {
        packet.extract(hdr.pkt_out);
        transition accept;
    }

    state parse_ethernet {
        packet.extract(hdr.ethernet);
        transition select(hdr.ethernet.etherType) {
            TYPE_IPV4: parse_ipv4;
            default: accept;
        }
    }

    state parse_ipv4 {
        packet.extract(hdr.ipv4);
        transition select(hdr.ipv4.protocol) {
            TYPE_UDP: parse_udp;
            TYPE_TCP: parse_tcp;
            default: accept;
        }
    }

    state parse_udp {
        packet.extract(hdr.udp);
        transition accept;
    }

    state parse_tcp {
        packet.extract(hdr.tcp);
        transition accept;
    }
}

/*************************************************************************
************   C H E C K S U M    V E R I F I C A T I O N   *************
*************************************************************************/

control MyVerifyChecksum(inout headers hdr, inout metadata meta) {
    apply {  }
}


/*************************************************************************
**************  I N G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyIngress(inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata) {

    counter(1, CounterType.packets) tmp_counter;

    register<bit<32>>(1) tmp_register;
    register<bit<32>>(1) test_register;
    



    action ipv4_forward(egressSpec_t port) {
        standard_metadata.egress_spec = port;
        hdr.ipv4.ttl = hdr.ipv4.ttl - 1;
    }
    
    table forward {
    	key = {
    	    hdr.ipv4.dstAddr: lpm;
    	}
        actions = {
            ipv4_forward;
            NoAction;
        }
        size = 1024;
        default_action = NoAction();
    }
    
    action test(out bit<32> re) {
        tmp_register.write(0, 15);
        tmp_register.read(re, 0);
        tmp_counter.count(0);
    }

    apply {

        forward.apply();

        bit<32> tmp_ip_addr = 0;
        test(tmp_ip_addr);
        test_register.write(0, tmp_ip_addr);


        /******************************************* TEST: packetIO *******************************************/
        // if (hdr.ipv4.isValid()) {            
        //     // Only when the packetIn header is set to valid, packet can be sent to controller.
        //     // Should be placed before modify the packetIn header values
        //     hdr.pkt_in.setValid();
        //     standard_metadata.egress_spec = CPU_PORT;

        //     // set the packetIn headers
        //     hdr.pkt_in.flow_id = 13898;
        //     hdr.pkt_in.packet_type = ControllerPacketType_t.PACKET_IN;
        //     hdr.pkt_in.opcode = ControllerOpcode_t.CLASSIFY_REQUEST;
        //     hdr.pkt_in.reserved = 8;
        //     hdr.pkt_in.flag_1 = 1;
        //     hdr.pkt_in.flag_2 = 0;
        //     hdr.pkt_in.flag_3 = 1;
        //     hdr.pkt_in.flag_4 = 0;
        //     hdr.pkt_in.flag_5 = 1;
        //     hdr.pkt_in.flag_6 = 0;
        //     hdr.pkt_in.flag_7 = 1;
        //     hdr.pkt_in.flag_8 = 1;
        //     hdr.pkt_in.flag_9 = 7;
        //     hdr.pkt_in.flag_10 = 8;
        //     hdr.pkt_in.features.bidirectional_packets = 12;
        //     hdr.pkt_in.features.bidirectional_bytes = 5564;

        //     to_controller_counter.count(0);
        // } else if (hdr.pkt_out.isValid()) {
        //     flow_id_register.write(0, hdr.pkt_out.flow_id);
        //     packet_type_register.write(0, hdr.pkt_out.packet_type);
        //     opcode_register.write(0, hdr.pkt_out.opcode);
        //     class_register.write(0, hdr.pkt_out.class);
        //     reserved_register.write(0, hdr.pkt_out.reserved);

        //     from_controller_counter.count(0);
        // }
        /******************************************************************************************************/
    }
}

/*************************************************************************
****************  E G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {
    apply {  }
}

/*************************************************************************
*************   C H E C K S U M    C O M P U T A T I O N   **************
*************************************************************************/

control MyComputeChecksum(inout headers  hdr, inout metadata meta) {
     apply {
        update_checksum(
        hdr.ipv4.isValid(),
            { hdr.ipv4.version,
              hdr.ipv4.ihl,
              hdr.ipv4.diffserv,
              hdr.ipv4.totalLen,
              hdr.ipv4.identification,
              hdr.ipv4.flags,
              hdr.ipv4.fragOffset,
              hdr.ipv4.ttl,
              hdr.ipv4.protocol,
              hdr.ipv4.srcAddr,
              hdr.ipv4.dstAddr },
            hdr.ipv4.hdrChecksum,
            HashAlgorithm.csum16);
    }
}

/*************************************************************************
***********************  D E P A R S E R  *******************************
*************************************************************************/

control MyDeparser(packet_out packet, in headers hdr) {
    apply {
        packet.emit(hdr.pkt_in);
        packet.emit(hdr.ethernet);
        packet.emit(hdr.ipv4);
        packet.emit(hdr.udp);
        packet.emit(hdr.tcp);
    }
}

/*************************************************************************
***********************  S W I T C H  *******************************
*************************************************************************/

V1Switch(
MyParser(),
MyVerifyChecksum(),
MyIngress(),
MyEgress(),
MyComputeChecksum(),
MyDeparser()
) main;

/****************************** TODO *****************************************/
// TODO: 
// P4 standard_metadata.ingress_global_timestamp is in microsecond, time 
// or interval features are in millisecond (according to NFStream). The units should be unified. 
