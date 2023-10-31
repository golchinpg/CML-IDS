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
// If the length is incorrect, the compiler will return error and give the correct value.
#define FLOW_SIZE_BITS  777
#define FLOW_ID_BITS 32
// The value of FLOW_TIME_BITS should be the same as standard_metadata.ingress_global_timestamp which has 48 bits
#define FLOW_TIME_BITS 48
// The value of FLOW_BYTES_BITS should be the same length of standard_metadata.packet_length which has 32 bits
#define FLOW_BYTES_BITS 32
#define FLOW_COUNT_BITS 8
#define FLOW_SPLT_DIRECTION_BITS 8

// MAX_FEATURE_SIZE_BITS has at least to be 4 bits larger than the maximal bit length of features.
// (increase one-decimal precision)
#define MAX_FEATURE_SIZE_BITS 56
#define FEATURE_ID_BITS 16
#define NODE_ID_BITS 8

#define CLASSIFICATION_TIME_BITS 128    
/************************ other constants ************************/
/*****************************************************************/
// size of register to save flow features
#define FLOW_BUCKET 10000000
// number of bidirectional packet which is considered to classify flow
#define USED_PACKETS 8
// timeout to expire flow entries in the register (maximum bidirectional duration of dataset is 1799965000 microseconds)
// set the timeout to 30 mins == 1800000000 microseconds
#define TIMEOUT_EXPIRATION 1800000000


// the maxmum gini value is 0.5 (2 classes).
// This value has been amplified by a factor of 1000 to improve the precision from Python.
// needs 9 bits to store the maximum value 500
#define GINI_VALUE_BITS 16
// The maximum value of the gini value is 500.   
#define GINI_VALUE_THRESHOLD 300

// bit length of message sent to the controller
#define CONTROLLER_MESSAGE_BITS 8 

// packet sent to this port will be delivered to the controller
#define CPU_PORT 101




/*************************************************************************
*********************** H E A D E R S  ***********************************
*************************************************************************/

typedef bit<9>  egressSpec_t;
typedef bit<48> macAddr_t;
typedef bit<32> ip4Addr_t;

// the size should be larger than the maximal vlaue of id.
enum bit<FEATURE_ID_BITS> FeatureId {
    bidirectional_packets_id            = 114,
    bidirectional_bytes_id              = 115,
    src2dst_packets_id                  = 214,
    src2dst_bytes_id                    = 215,
    dst2src_packets_id                  = 314,
    dst2src_bytes_id                    = 315,
    bidirectional_min_ps_id             = 121,
    bidirectional_mean_ps_id            = 122,
    bidirectional_max_ps_id             = 124,
    src2dst_min_ps_id                   = 221,
    src2dst_max_ps_id                   = 224,
    dst2src_min_ps_id                   = 321,
    dst2src_max_ps_id                   = 324,
    bidirectional_syn_packets_id        = 141,
    bidirectional_cwr_packets_id        = 142,
    bidirectional_ece_packets_id        = 143,
    bidirectional_urg_packets_id        = 144,
    bidirectional_ack_packets_id        = 145,
    bidirectional_psh_packets_id        = 146,
    bidirectional_rst_packets_id        = 147,
    bidirectional_fin_packets_id        = 148,
    src2dst_syn_packets_id              = 241,
    src2dst_cwr_packets_id              = 242,
    src2dst_ece_packets_id              = 243,
    src2dst_urg_packets_id              = 244,
    src2dst_ack_packets_id              = 245,
    src2dst_psh_packets_id              = 246,
    src2dst_rst_packets_id              = 247,
    src2dst_fin_packets_id              = 248,
    dst2src_syn_packets_id              = 341,
    dst2src_cwr_packets_id              = 342,
    dst2src_ece_packets_id              = 343,
    dst2src_urg_packets_id              = 344,
    dst2src_ack_packets_id              = 345,
    dst2src_psh_packets_id              = 346,
    dst2src_rst_packets_id              = 347,
    dst2src_fin_packets_id              = 348
}

// map ip address to integer, used to set the real label of flow
enum bit<32> IP2int {
    id_172_16_0_1       = 2886729729,
    id_192_168_10_8     = 3232238088,
    id_192_168_10_12    = 3232238092,
    id_205_174_165_73   = 3450774857,
    id_192_168_10_14    = 3232238094,
    id_52_6_13_28       = 872811804,
    id_192_168_10_15    = 3232238095,
    id_192_168_10_9     = 3232238089,
    id_192_168_10_17    = 3232238097,
    id_192_168_10_50    = 3232238130,
    id_192_168_10_5     = 3232238085,
    id_52_7_235_158     = 872934302
}


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
    bit<FLOW_COUNT_BITS>        bidirectional_packets;
    bit<FLOW_BYTES_BITS>        bidirectional_bytes;
    bit<FLOW_COUNT_BITS>        src2dst_packets;
    bit<FLOW_BYTES_BITS>        src2dst_bytes;
    bit<FLOW_COUNT_BITS>        dst2src_packets;
    bit<FLOW_BYTES_BITS>        dst2src_bytes;
    bit<FLOW_BYTES_BITS>        bidirectional_min_ps;
    bit<FLOW_BYTES_BITS>        bidirectional_mean_ps;
    bit<FLOW_BYTES_BITS>        bidirectional_max_ps;
    bit<FLOW_BYTES_BITS>        src2dst_min_ps;
    bit<FLOW_BYTES_BITS>        src2dst_max_ps;
    bit<FLOW_BYTES_BITS>        dst2src_min_ps;
    bit<FLOW_BYTES_BITS>        dst2src_max_ps;
    bit<FLOW_COUNT_BITS>        bidirectional_syn_packets;
    bit<FLOW_COUNT_BITS>        bidirectional_cwr_packets;
    bit<FLOW_COUNT_BITS>        bidirectional_ece_packets;
    bit<FLOW_COUNT_BITS>        bidirectional_urg_packets;
    bit<FLOW_COUNT_BITS>        bidirectional_ack_packets;
    bit<FLOW_COUNT_BITS>        bidirectional_psh_packets;
    bit<FLOW_COUNT_BITS>        bidirectional_rst_packets;
    bit<FLOW_COUNT_BITS>        bidirectional_fin_packets;
    bit<FLOW_COUNT_BITS>        src2dst_syn_packets;
    bit<FLOW_COUNT_BITS>        src2dst_cwr_packets;
    bit<FLOW_COUNT_BITS>        src2dst_ece_packets;
    bit<FLOW_COUNT_BITS>        src2dst_urg_packets;
    bit<FLOW_COUNT_BITS>        src2dst_ack_packets;
    bit<FLOW_COUNT_BITS>        src2dst_psh_packets;
    bit<FLOW_COUNT_BITS>        src2dst_rst_packets;
    bit<FLOW_COUNT_BITS>        src2dst_fin_packets;
    bit<FLOW_COUNT_BITS>        dst2src_syn_packets;
    bit<FLOW_COUNT_BITS>        dst2src_cwr_packets;
    bit<FLOW_COUNT_BITS>        dst2src_ece_packets;
    bit<FLOW_COUNT_BITS>        dst2src_urg_packets;
    bit<FLOW_COUNT_BITS>        dst2src_ack_packets;
    bit<FLOW_COUNT_BITS>        dst2src_psh_packets;
    bit<FLOW_COUNT_BITS>        dst2src_rst_packets;
    bit<FLOW_COUNT_BITS>        dst2src_fin_packets;
}

// packet in and out header should be placed after struct feature_t
// packet in header
@controller_header("packet_in")
header packet_in_header_t {
    ControllerPacketType_t  packet_type;  
    ControllerOpcode_t      opcode;
    bit<FLOW_ID_BITS>       flow_id;
    features_t              features;
}

// packet out header
@controller_header("packet_out")
header packet_out_header_t {
    ControllerPacketType_t  packet_type;  
    ControllerOpcode_t      opcode;
    bit<FLOW_ID_BITS>       flow_id;
    // set the bit length of class to 1 bit, which is consistent with the feature class in a flow entry.
    bit<1>                  class;
    // the total header length should be in byte
    bit<7>                  reserved;
}

// flow struct
struct flow_t {
    bit<FLOW_ID_BITS>       flow_id;
    ip4Addr_t               src_ipv4_addr;
    ip4Addr_t               dst_ipv4_addr;
    bit<16>                 src_port;
    bit<16>                 dst_port;
    bit<8>                  protocol;
    bit<FLOW_TIME_BITS>     bidirectional_first_seen_ms;
    bit<FLOW_TIME_BITS>     packet_8th_seen_ms;   
    bit<1>                  stored;
    bit<1>                  classified;
    bit<1>                  class;
    bit<1>                  classified_tree_1;
    bit<1>                  class_tree_1;
    bit<1>                  classified_tree_2;
    bit<1>                  class_tree_2;
    bit<1>                  classified_tree_3;
    bit<1>                  class_tree_3;
    features_t              features;
}

struct metadata {
    flow_t                  flow;
    bit<FLOW_SIZE_BITS>     bitstring;    
    bit<FLOW_ID_BITS>       current_flow_id;
    bit<16>                 current_packet_src_port;
    bit<16>                 current_packet_dst_port;
    bit<1>                  is_dst2src;
    bit<NODE_ID_BITS>       current_node_id;
    bit<2>                  feature_larger_than_thr;
    bit<GINI_VALUE_BITS>    gini_value_tree_1;
    bit<GINI_VALUE_BITS>    gini_value_tree_2;
    bit<GINI_VALUE_BITS>    gini_value_tree_3;
    bit<NODE_ID_BITS>       leaf_node_id_tree_1;
    bit<NODE_ID_BITS>       leaf_node_id_tree_2;
    bit<NODE_ID_BITS>       leaf_node_id_tree_3;
    bit<1>                  accumulate_time_p4_flag;
}

struct headers {
    ethernet_t              ethernet;
    ipv4_t                  ipv4;
    udp_t                   udp;
    tcp_t                   tcp;
    packet_in_header_t      pkt_in;
    packet_out_header_t     pkt_out;
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

    /*********************** register to store the flows ***********************/
    // register to store the flow entries
    // use hash function crc32
    register<bit<FLOW_SIZE_BITS>>(FLOW_BUCKET) flow_buffer_32;
    
    /*********************** monitoring counters ***********************/
    counter(1, CounterType.packets) packet_ipv4_total_counter;

    // counters for total, begign and attack flows
    counter(1, CounterType.packets) flow_classified_counter;
    counter(1, CounterType.packets) flow_predicted_p4_sum_counter;
    counter(1, CounterType.packets) flow_predicted_controller_sum_counter;

    // counter for the number of flows with predicted class from the controller
    counter(1, CounterType.packets) flow_from_controller_counter;

    /*********************** classification time registers ***********************/
    // store the sum of classification time in controller
    register<bit<CLASSIFICATION_TIME_BITS>>(1) classification_time_controller_register;

    /**
    * get payload length 
    **/
    action get_payload_length(out bit<FLOW_BYTES_BITS> payload_length) {
        payload_length = standard_metadata.packet_length - ETHERNET_HAEDER_LENGTH - IPV4_HEADER_LENGTH;
        if (hdr.tcp.isValid()) {
            payload_length = payload_length - ((bit<FLOW_BYTES_BITS>) hdr.tcp.dataOffset * 4);
        } else if (hdr.udp.isValid()) {
            payload_length = payload_length - UDP_HEADER_LENGTH;
        }
    }


    /**
    * initialize flow
    **/
    action init_flow() {
        // Initially, the value of each feature is 0. Set all fields with the initialized value because of the refreshing register.
        /*********************** initiate the flow entry ***********************/
        meta.flow.flow_id = meta.current_flow_id;
        // assign the source IP address to this flow entry, used to label flows (benign or attack)
        meta.flow.src_ipv4_addr = hdr.ipv4.srcAddr;
        meta.flow.dst_ipv4_addr = hdr.ipv4.dstAddr;
        meta.flow.src_port = meta.current_packet_src_port;
        meta.flow.dst_port = meta.current_packet_dst_port;
        meta.flow.protocol = hdr.ipv4.protocol;
        // src and dst ports are initialized in the apply block

        meta.flow.stored = 1;
        meta.flow.classified = 0;
        meta.flow.class = 0;
        meta.flow.classified_tree_1 = 0;
        meta.flow.class_tree_1 = 0;
        meta.flow.classified_tree_2 = 0;
        meta.flow.class_tree_2 = 0;
        meta.flow.classified_tree_3 = 0;
        meta.flow.class_tree_3 = 0;
        meta.flow.bidirectional_first_seen_ms = standard_metadata.ingress_global_timestamp;

        /*********************** initiate the core features ***********************/
        // get payload length
        bit<FLOW_BYTES_BITS> payload_length = 0;
        get_payload_length(payload_length);

        meta.flow.features.bidirectional_packets = 1;
        meta.flow.features.bidirectional_bytes = payload_length;
        meta.flow.features.src2dst_packets = 1;
        meta.flow.features.src2dst_bytes = payload_length;
        meta.flow.features.dst2src_packets = 0;
        meta.flow.features.dst2src_bytes = 0;

        /*********************** initiate the post-mortem statistical features ***********************/
        meta.flow.features.bidirectional_min_ps = payload_length;
        meta.flow.features.bidirectional_mean_ps = payload_length;
        meta.flow.features.bidirectional_max_ps = payload_length;
        meta.flow.features.src2dst_min_ps = payload_length;
        meta.flow.features.src2dst_max_ps = payload_length;
        meta.flow.features.dst2src_min_ps = 0;
        meta.flow.features.dst2src_max_ps = 0;

        /*********************** initiate the flag features ***********************/
        if (hdr.tcp.syn == 1) {
            meta.flow.features.bidirectional_syn_packets = 1;
            meta.flow.features.src2dst_syn_packets = 1;
        } else {
            meta.flow.features.bidirectional_syn_packets = 0;
            meta.flow.features.src2dst_syn_packets = 0;
        }

        if (hdr.tcp.cwr == 1){
            meta.flow.features.bidirectional_cwr_packets = 1;
            meta.flow.features.src2dst_cwr_packets = 1;
        } else {
            meta.flow.features.bidirectional_cwr_packets = 0;
            meta.flow.features.src2dst_cwr_packets = 0;
        }
        
        if (hdr.tcp.ece == 1){
            meta.flow.features.bidirectional_ece_packets = 1;
            meta.flow.features.src2dst_ece_packets = 1;
        } else {
            meta.flow.features.bidirectional_ece_packets = 0;
            meta.flow.features.src2dst_ece_packets = 0;
        }
        
        if (hdr.tcp.urg == 1){
            meta.flow.features.bidirectional_urg_packets = 1;
            meta.flow.features.src2dst_urg_packets = 1;
        } else {
            meta.flow.features.bidirectional_urg_packets = 0;
            meta.flow.features.src2dst_urg_packets = 0;
        }
        
        if (hdr.tcp.ack == 1){
            meta.flow.features.bidirectional_ack_packets = 1;
            meta.flow.features.src2dst_ack_packets = 1;
        } else {
            meta.flow.features.bidirectional_ack_packets = 0;
            meta.flow.features.src2dst_ack_packets = 0;
        }
        
        if (hdr.tcp.psh == 1){
            meta.flow.features.bidirectional_psh_packets = 1;
            meta.flow.features.src2dst_psh_packets = 1;
        } else {
            meta.flow.features.bidirectional_psh_packets = 0;
            meta.flow.features.src2dst_psh_packets = 0;
        }
        
        if (hdr.tcp.rst == 1){
            meta.flow.features.bidirectional_rst_packets = 1;
            meta.flow.features.src2dst_rst_packets = 1;
        } else {
            meta.flow.features.bidirectional_rst_packets = 0;
            meta.flow.features.src2dst_rst_packets = 0;
        }
        
        if (hdr.tcp.fin == 1){
            meta.flow.features.bidirectional_fin_packets = 1;
            meta.flow.features.src2dst_fin_packets = 1;
        } else {
            meta.flow.features.bidirectional_fin_packets = 0;
            meta.flow.features.src2dst_fin_packets = 0;
        }

        meta.flow.features.dst2src_syn_packets = 0;
        meta.flow.features.dst2src_cwr_packets = 0;
        meta.flow.features.dst2src_ece_packets = 0;
        meta.flow.features.dst2src_urg_packets = 0;
        meta.flow.features.dst2src_ack_packets = 0;
        meta.flow.features.dst2src_psh_packets = 0;
        meta.flow.features.dst2src_rst_packets = 0;
        meta.flow.features.dst2src_fin_packets = 0;
    }


    /**
    * update the flow features
    **/
    action update_flow() {
        // get payload length
        bit<FLOW_BYTES_BITS> payload_length = 0;
        get_payload_length(payload_length);

        /*********************************************************************************/
        /*********************** update the bidirectional features ***********************/
        /*********************************************************************************/

        /*********************** init of core features ***********************/
        meta.flow.features.bidirectional_packets = meta.flow.features.bidirectional_packets + 1;
        meta.flow.features.bidirectional_bytes = meta.flow.features.bidirectional_bytes + payload_length;
        
        /*********************** init of post-mortem statistical features ***********************/
        if (payload_length < meta.flow.features.bidirectional_min_ps) {
            meta.flow.features.bidirectional_min_ps = payload_length;
        }
        if (payload_length > meta.flow.features.bidirectional_max_ps) {
            meta.flow.features.bidirectional_max_ps = payload_length;
        }
        // if the number of bidirectional pacekts reachs the desired number, compute the mean value of bidirectional bytes 
        // store the packet_8th_seen_ms
        if (meta.flow.features.bidirectional_packets == USED_PACKETS) {
            meta.flow.features.bidirectional_mean_ps = meta.flow.features.bidirectional_bytes >> 3;
            meta.flow.packet_8th_seen_ms = standard_metadata.ingress_global_timestamp;

        }

        if (meta.is_dst2src == 1) {
            /***************************************************************************/
            /*********************** update the dst2src features ***********************/
            /***************************************************************************/
            
            /*********************** update the dst2src core features ***********************/
            meta.flow.features.dst2src_packets = meta.flow.features.dst2src_packets + 1;
            meta.flow.features.dst2src_bytes = meta.flow.features.dst2src_bytes + payload_length;

            /*********************** update the dst2src post-mortem statistical features ***********************/
            // initialize the dst2src_min_ps with the first dst2src pacekt
            if (meta.flow.features.dst2src_packets == 1) {
                meta.flow.features.dst2src_min_ps = payload_length;
            } else if (payload_length < meta.flow.features.dst2src_min_ps) {
                meta.flow.features.dst2src_min_ps = payload_length;
            }

            if (payload_length > meta.flow.features.dst2src_max_ps) {
                meta.flow.features.dst2src_max_ps = payload_length;
            }
                
            /*********************** update the dst2src and bidirectional flag features ***********************/
            if (hdr.tcp.syn == 1) {
                meta.flow.features.dst2src_syn_packets = meta.flow.features.dst2src_syn_packets + 1;
                meta.flow.features.bidirectional_syn_packets = meta.flow.features.bidirectional_syn_packets + 1;
            } 

            if (hdr.tcp.cwr == 1){
                meta.flow.features.dst2src_cwr_packets = meta.flow.features.dst2src_cwr_packets + 1;
                meta.flow.features.bidirectional_cwr_packets = meta.flow.features.bidirectional_cwr_packets + 1;
            } 
            
            if (hdr.tcp.ece == 1){
                meta.flow.features.dst2src_ece_packets = meta.flow.features.dst2src_ece_packets + 1;
                meta.flow.features.bidirectional_ece_packets = meta.flow.features.bidirectional_ece_packets + 1;
            } 
            
            if (hdr.tcp.urg == 1){
                meta.flow.features.dst2src_urg_packets = meta.flow.features.dst2src_urg_packets + 1;
                meta.flow.features.bidirectional_urg_packets = meta.flow.features.bidirectional_urg_packets + 1;
            } 
            
            if (hdr.tcp.ack == 1){
                meta.flow.features.dst2src_ack_packets = meta.flow.features.dst2src_ack_packets + 1;
                meta.flow.features.bidirectional_ack_packets = meta.flow.features.bidirectional_ack_packets + 1;
            } 
            
            if (hdr.tcp.psh == 1){
                meta.flow.features.dst2src_psh_packets = meta.flow.features.dst2src_psh_packets + 1;
                meta.flow.features.bidirectional_psh_packets = meta.flow.features.bidirectional_psh_packets + 1;
            } 
            
            if (hdr.tcp.rst == 1){
                meta.flow.features.dst2src_rst_packets = meta.flow.features.dst2src_rst_packets + 1;
                meta.flow.features.bidirectional_rst_packets = meta.flow.features.bidirectional_rst_packets + 1;
            } 
            
            if (hdr.tcp.fin == 1){
                meta.flow.features.dst2src_fin_packets = meta.flow.features.dst2src_fin_packets + 1;
                meta.flow.features.bidirectional_fin_packets = meta.flow.features.bidirectional_fin_packets + 1;
            } 
        } else {
            /***************************************************************************/
            /*********************** update the src2dst features ***********************/
            /***************************************************************************/

            /*********************** update the src2dst core features ***********************/
            meta.flow.features.src2dst_packets = meta.flow.features.src2dst_packets + 1;
            meta.flow.features.src2dst_bytes = meta.flow.features.src2dst_bytes + (bit<FLOW_BYTES_BITS>)payload_length;   
                
            /*********************** update the src2dst post-mortem statistical features ***********************/
            if (payload_length < meta.flow.features.src2dst_min_ps){
                meta.flow.features.src2dst_min_ps = payload_length;
            }
            if (payload_length > meta.flow.features.src2dst_max_ps) {
                meta.flow.features.src2dst_max_ps = payload_length;
            }

            /*********************** update the src2dst and bidirectional flag features ***********************/
            if (hdr.tcp.syn == 1) {
                meta.flow.features.src2dst_syn_packets = meta.flow.features.src2dst_syn_packets + 1;
                meta.flow.features.bidirectional_syn_packets = meta.flow.features.bidirectional_syn_packets + 1;
            } 

            if (hdr.tcp.cwr == 1){
                meta.flow.features.src2dst_cwr_packets = meta.flow.features.src2dst_cwr_packets + 1;
                meta.flow.features.bidirectional_cwr_packets = meta.flow.features.bidirectional_cwr_packets + 1;
            } 
            
            if (hdr.tcp.ece == 1){
                meta.flow.features.src2dst_ece_packets = meta.flow.features.src2dst_ece_packets + 1;
                meta.flow.features.bidirectional_ece_packets = meta.flow.features.bidirectional_ece_packets + 1;
            } 
            
            if (hdr.tcp.urg == 1){
                meta.flow.features.src2dst_urg_packets = meta.flow.features.src2dst_urg_packets + 1;
                meta.flow.features.bidirectional_urg_packets = meta.flow.features.bidirectional_urg_packets + 1;
            } 
            
            if (hdr.tcp.ack == 1){
                meta.flow.features.src2dst_ack_packets = meta.flow.features.src2dst_ack_packets + 1;
                meta.flow.features.bidirectional_ack_packets = meta.flow.features.bidirectional_ack_packets + 1;
            } 
            
            if (hdr.tcp.psh == 1){
                meta.flow.features.src2dst_psh_packets = meta.flow.features.src2dst_psh_packets + 1;
                meta.flow.features.bidirectional_psh_packets = meta.flow.features.bidirectional_psh_packets + 1;
            } 
            
            if (hdr.tcp.rst == 1){
                meta.flow.features.src2dst_rst_packets = meta.flow.features.src2dst_rst_packets + 1;
                meta.flow.features.bidirectional_rst_packets = meta.flow.features.bidirectional_rst_packets + 1;
            } 
            
            if (hdr.tcp.fin == 1){
                meta.flow.features.src2dst_fin_packets = meta.flow.features.src2dst_fin_packets + 1;
                meta.flow.features.bidirectional_fin_packets = meta.flow.features.bidirectional_fin_packets + 1;
            }
        }
    }


    /**
    * convert struct to bitstring, in order to store the states in the register
    **/
    action struct_to_bitstring() {
        meta.bitstring = meta.flow.flow_id ++
                            meta.flow.src_ipv4_addr ++ 
                            meta.flow.dst_ipv4_addr ++ 
                            meta.flow.src_port ++ 
                            meta.flow.dst_port ++ 
                            meta.flow.protocol ++ 
                            meta.flow.bidirectional_first_seen_ms ++ 
                            meta.flow.packet_8th_seen_ms ++ 
                            meta.flow.stored ++
                            meta.flow.class ++
                            meta.flow.classified ++
                            meta.flow.class_tree_1 ++
                            meta.flow.classified_tree_1 ++
                            meta.flow.class_tree_2 ++
                            meta.flow.classified_tree_2 ++
                            meta.flow.class_tree_3 ++
                            meta.flow.classified_tree_3 ++ 
                            meta.flow.features.bidirectional_packets ++
                            meta.flow.features.bidirectional_bytes ++
                            meta.flow.features.src2dst_packets ++
                            meta.flow.features.src2dst_bytes ++
                            meta.flow.features.dst2src_packets ++
                            meta.flow.features.dst2src_bytes ++
                            meta.flow.features.bidirectional_min_ps ++
                            meta.flow.features.bidirectional_mean_ps ++
                            meta.flow.features.bidirectional_max_ps ++
                            meta.flow.features.src2dst_min_ps ++
                            meta.flow.features.src2dst_max_ps ++
                            meta.flow.features.dst2src_min_ps ++
                            meta.flow.features.dst2src_max_ps ++
                            meta.flow.features.bidirectional_syn_packets ++
                            meta.flow.features.bidirectional_cwr_packets ++
                            meta.flow.features.bidirectional_ece_packets ++
                            meta.flow.features.bidirectional_urg_packets ++
                            meta.flow.features.bidirectional_ack_packets ++
                            meta.flow.features.bidirectional_psh_packets ++
                            meta.flow.features.bidirectional_rst_packets ++
                            meta.flow.features.bidirectional_fin_packets ++
                            meta.flow.features.src2dst_syn_packets ++
                            meta.flow.features.src2dst_cwr_packets ++
                            meta.flow.features.src2dst_ece_packets ++
                            meta.flow.features.src2dst_urg_packets ++
                            meta.flow.features.src2dst_ack_packets ++
                            meta.flow.features.src2dst_psh_packets ++
                            meta.flow.features.src2dst_rst_packets ++
                            meta.flow.features.src2dst_fin_packets ++
                            meta.flow.features.dst2src_syn_packets ++
                            meta.flow.features.dst2src_cwr_packets ++
                            meta.flow.features.dst2src_ece_packets ++
                            meta.flow.features.dst2src_urg_packets ++
                            meta.flow.features.dst2src_ack_packets ++
                            meta.flow.features.dst2src_psh_packets ++
                            meta.flow.features.dst2src_rst_packets ++
                            meta.flow.features.dst2src_fin_packets; 
    }

    /**
    * convert bit string to struct
    **/
    action bitstring_to_struct() {
        // only constant can be assigned to the slicing index

        /************************* states of flow entry ***********************/
        const int lowerBound_0 = FLOW_SIZE_BITS - FLOW_ID_BITS;
        meta.flow.flow_id =
            meta.bitstring[(lowerBound_0+FLOW_ID_BITS-1):lowerBound_0];

        const int lowerBound_1 = lowerBound_0 - 32;
        meta.flow.src_ipv4_addr =
            meta.bitstring[lowerBound_1+31:lowerBound_1];

        const int lowerBound_2 = lowerBound_1 - 32;
        meta.flow.dst_ipv4_addr =
            meta.bitstring[lowerBound_2+31:lowerBound_2];

        const int lowerBound_3 = lowerBound_2 - 16;
        meta.flow.src_port =
            meta.bitstring[lowerBound_3+15:lowerBound_3];

        const int lowerBound_4 = lowerBound_3 - 16;
        meta.flow.dst_port =
            meta.bitstring[lowerBound_4+15:lowerBound_4];

        const int lowerBound_5 = lowerBound_4 - 8;
        meta.flow.protocol =
            meta.bitstring[lowerBound_5+7:lowerBound_5];

        const int lowerBound_6 = lowerBound_5 - FLOW_TIME_BITS;
        meta.flow.bidirectional_first_seen_ms =
            meta.bitstring[lowerBound_6+FLOW_TIME_BITS-1:lowerBound_6];

        const int lowerBound_7 = lowerBound_6 - FLOW_TIME_BITS;
        meta.flow.packet_8th_seen_ms =
            meta.bitstring[lowerBound_7+FLOW_TIME_BITS-1:lowerBound_7];

        const int lowerBound_8 = lowerBound_7 - 1;
        meta.flow.stored =
            meta.bitstring[lowerBound_8:lowerBound_8];

        const int lowerBound_9 = lowerBound_8 - 1;
        meta.flow.class =
            meta.bitstring[lowerBound_9:lowerBound_9];

        const int lowerBound_10 = lowerBound_9 - 1;
        meta.flow.classified =
            meta.bitstring[lowerBound_10:lowerBound_10];

        const int lowerBound_11 = lowerBound_10 - 1;
        meta.flow.class_tree_1 =
            meta.bitstring[lowerBound_11:lowerBound_11];

        const int lowerBound_12 = lowerBound_11 - 1;
        meta.flow.classified_tree_1 =
            meta.bitstring[lowerBound_12:lowerBound_12];

        const int lowerBound_13 = lowerBound_12 - 1;
        meta.flow.class_tree_2 =
            meta.bitstring[lowerBound_13:lowerBound_13];

        const int lowerBound_14 = lowerBound_13 - 1;
        meta.flow.classified_tree_2 =
            meta.bitstring[lowerBound_14:lowerBound_14];

        const int lowerBound_15 = lowerBound_14 - 1;
        meta.flow.class_tree_3 =
            meta.bitstring[lowerBound_15:lowerBound_15];

        const int lowerBound_16 = lowerBound_15 - 1;
        meta.flow.classified_tree_3 =
            meta.bitstring[lowerBound_16:lowerBound_16];


        /************************* features ***********************/

        const int lowerBound_17 = lowerBound_16 - FLOW_COUNT_BITS;
        meta.flow.features.bidirectional_packets =
            meta.bitstring[lowerBound_17+FLOW_COUNT_BITS-1:lowerBound_17];

        const int lowerBound_18 = lowerBound_17 - FLOW_BYTES_BITS;
        meta.flow.features.bidirectional_bytes =
            meta.bitstring[lowerBound_18+FLOW_BYTES_BITS-1:lowerBound_18];

        const int lowerBound_19 = lowerBound_18 - FLOW_COUNT_BITS;
        meta.flow.features.src2dst_packets =
            meta.bitstring[lowerBound_19+FLOW_COUNT_BITS-1:lowerBound_19];

        const int lowerBound_20 = lowerBound_19 - FLOW_BYTES_BITS;
        meta.flow.features.src2dst_bytes =
            meta.bitstring[lowerBound_20+FLOW_BYTES_BITS-1:lowerBound_20];

        const int lowerBound_21 = lowerBound_20 - FLOW_COUNT_BITS;
        meta.flow.features.dst2src_packets =
            meta.bitstring[lowerBound_21+FLOW_COUNT_BITS-1:lowerBound_21];

        const int lowerBound_22 = lowerBound_21 - FLOW_BYTES_BITS;
        meta.flow.features.dst2src_bytes =
            meta.bitstring[lowerBound_22+FLOW_BYTES_BITS-1:lowerBound_22];

        const int lowerBound_23 = lowerBound_22 - FLOW_BYTES_BITS;
        meta.flow.features.bidirectional_min_ps =
            meta.bitstring[lowerBound_23+FLOW_BYTES_BITS-1:lowerBound_23];

        const int lowerBound_24 = lowerBound_23 - FLOW_BYTES_BITS;
        meta.flow.features.bidirectional_mean_ps =
            meta.bitstring[lowerBound_24+FLOW_BYTES_BITS-1:lowerBound_24];

        const int lowerBound_25 = lowerBound_24 - FLOW_BYTES_BITS;
        meta.flow.features.bidirectional_max_ps =
            meta.bitstring[lowerBound_25+FLOW_BYTES_BITS-1:lowerBound_25];

        const int lowerBound_26 = lowerBound_25 - FLOW_BYTES_BITS;
        meta.flow.features.src2dst_min_ps =
            meta.bitstring[lowerBound_26+FLOW_BYTES_BITS-1:lowerBound_26];

        const int lowerBound_27 = lowerBound_26 - FLOW_BYTES_BITS;
        meta.flow.features.src2dst_max_ps =
            meta.bitstring[lowerBound_27+FLOW_BYTES_BITS-1:lowerBound_27];

        const int lowerBound_28 = lowerBound_27 - FLOW_BYTES_BITS;
        meta.flow.features.dst2src_min_ps =
            meta.bitstring[lowerBound_28+FLOW_BYTES_BITS-1:lowerBound_28];

        const int lowerBound_29 = lowerBound_28 - FLOW_BYTES_BITS;
        meta.flow.features.dst2src_max_ps =
            meta.bitstring[lowerBound_29+FLOW_BYTES_BITS-1:lowerBound_29];

        const int lowerBound_30 = lowerBound_29 - FLOW_COUNT_BITS;
        meta.flow.features.bidirectional_syn_packets =
            meta.bitstring[lowerBound_30+FLOW_COUNT_BITS-1:lowerBound_30];

        const int lowerBound_31 = lowerBound_30 - FLOW_COUNT_BITS;
        meta.flow.features.bidirectional_cwr_packets =
            meta.bitstring[lowerBound_31+FLOW_COUNT_BITS-1:lowerBound_31];

        const int lowerBound_32 = lowerBound_31 - FLOW_COUNT_BITS;
        meta.flow.features.bidirectional_ece_packets =
            meta.bitstring[lowerBound_32+FLOW_COUNT_BITS-1:lowerBound_32];

        const int lowerBound_33 = lowerBound_32 - FLOW_COUNT_BITS;
        meta.flow.features.bidirectional_urg_packets =
            meta.bitstring[lowerBound_33+FLOW_COUNT_BITS-1:lowerBound_33];

        const int lowerBound_34 = lowerBound_33 - FLOW_COUNT_BITS;
        meta.flow.features.bidirectional_ack_packets =
            meta.bitstring[lowerBound_34+FLOW_COUNT_BITS-1:lowerBound_34];

        const int lowerBound_35 = lowerBound_34 - FLOW_COUNT_BITS;
        meta.flow.features.bidirectional_psh_packets =
            meta.bitstring[lowerBound_35+FLOW_COUNT_BITS-1:lowerBound_35];

        const int lowerBound_36 = lowerBound_35 - FLOW_COUNT_BITS;
        meta.flow.features.bidirectional_rst_packets =
            meta.bitstring[lowerBound_36+FLOW_COUNT_BITS-1:lowerBound_36];

        const int lowerBound_37 = lowerBound_36 - FLOW_COUNT_BITS;
        meta.flow.features.bidirectional_fin_packets =
            meta.bitstring[lowerBound_37+FLOW_COUNT_BITS-1:lowerBound_37];

        const int lowerBound_38 = lowerBound_37 - FLOW_COUNT_BITS;
        meta.flow.features.src2dst_syn_packets =
            meta.bitstring[lowerBound_38+FLOW_COUNT_BITS-1:lowerBound_38];

        const int lowerBound_39 = lowerBound_38 - FLOW_COUNT_BITS;
        meta.flow.features.src2dst_cwr_packets =
            meta.bitstring[lowerBound_39+FLOW_COUNT_BITS-1:lowerBound_39];

        const int lowerBound_40 = lowerBound_39 - FLOW_COUNT_BITS;
        meta.flow.features.src2dst_ece_packets =
            meta.bitstring[lowerBound_40+FLOW_COUNT_BITS-1:lowerBound_40];

        const int lowerBound_41 = lowerBound_40 - FLOW_COUNT_BITS;
        meta.flow.features.src2dst_urg_packets =
            meta.bitstring[lowerBound_41+FLOW_COUNT_BITS-1:lowerBound_41];

        const int lowerBound_42 = lowerBound_41 - FLOW_COUNT_BITS;
        meta.flow.features.src2dst_ack_packets =
            meta.bitstring[lowerBound_42+FLOW_COUNT_BITS-1:lowerBound_42];

        const int lowerBound_43 = lowerBound_42 - FLOW_COUNT_BITS;
        meta.flow.features.src2dst_psh_packets =
            meta.bitstring[lowerBound_43+FLOW_COUNT_BITS-1:lowerBound_43];

        const int lowerBound_44 = lowerBound_43 - FLOW_COUNT_BITS;
        meta.flow.features.src2dst_rst_packets =
            meta.bitstring[lowerBound_44+FLOW_COUNT_BITS-1:lowerBound_44];

        const int lowerBound_45 = lowerBound_44 - FLOW_COUNT_BITS;
        meta.flow.features.src2dst_fin_packets =
            meta.bitstring[lowerBound_45+FLOW_COUNT_BITS-1:lowerBound_45];

        const int lowerBound_46 = lowerBound_45 - FLOW_COUNT_BITS;
        meta.flow.features.dst2src_syn_packets =
            meta.bitstring[lowerBound_46+FLOW_COUNT_BITS-1:lowerBound_46];

        const int lowerBound_47 = lowerBound_46 - FLOW_COUNT_BITS;
        meta.flow.features.dst2src_cwr_packets =
            meta.bitstring[lowerBound_47+FLOW_COUNT_BITS-1:lowerBound_47];

        const int lowerBound_48 = lowerBound_47 - FLOW_COUNT_BITS;
        meta.flow.features.dst2src_ece_packets =
            meta.bitstring[lowerBound_48+FLOW_COUNT_BITS-1:lowerBound_48];

        const int lowerBound_49 = lowerBound_48 - FLOW_COUNT_BITS;
        meta.flow.features.dst2src_urg_packets =
            meta.bitstring[lowerBound_49+FLOW_COUNT_BITS-1:lowerBound_49];

        const int lowerBound_50 = lowerBound_49 - FLOW_COUNT_BITS;
        meta.flow.features.dst2src_ack_packets =
            meta.bitstring[lowerBound_50+FLOW_COUNT_BITS-1:lowerBound_50];

        const int lowerBound_51 = lowerBound_50 - FLOW_COUNT_BITS;
        meta.flow.features.dst2src_psh_packets =
            meta.bitstring[lowerBound_51+FLOW_COUNT_BITS-1:lowerBound_51];

        const int lowerBound_52 = lowerBound_51 - FLOW_COUNT_BITS;
        meta.flow.features.dst2src_rst_packets =
            meta.bitstring[lowerBound_52+FLOW_COUNT_BITS-1:lowerBound_52];

        const int lowerBound_53 = lowerBound_52 - FLOW_COUNT_BITS;
        meta.flow.features.dst2src_fin_packets =
            meta.bitstring[lowerBound_53+FLOW_COUNT_BITS-1:lowerBound_53];
    }


    /**
    * called by the control plane to install rules.
    **/
    action compare_feature(bit<FEATURE_ID_BITS> feature_id, bit<MAX_FEATURE_SIZE_BITS> threshold, bit<NODE_ID_BITS> next_node_id) {
        // update the node id
        meta.current_node_id = next_node_id;
        // the current feature with the maximal feature size bits
        bit<MAX_FEATURE_SIZE_BITS> current_feature = 0;

        if (feature_id == FeatureId.dst2src_bytes_id)
            current_feature = (bit<MAX_FEATURE_SIZE_BITS>) meta.flow.features.dst2src_bytes;
        else if (feature_id == FeatureId.bidirectional_bytes_id)
            current_feature = (bit<MAX_FEATURE_SIZE_BITS>) meta.flow.features.bidirectional_bytes;
        else if (feature_id == FeatureId.bidirectional_mean_ps_id)
            current_feature = (bit<MAX_FEATURE_SIZE_BITS>) meta.flow.features.bidirectional_mean_ps;
        else if (feature_id == FeatureId.bidirectional_max_ps_id)
            current_feature = (bit<MAX_FEATURE_SIZE_BITS>) meta.flow.features.bidirectional_max_ps;
        else if (feature_id == FeatureId.dst2src_max_ps_id)
            current_feature = (bit<MAX_FEATURE_SIZE_BITS>) meta.flow.features.dst2src_max_ps;
        else if (feature_id == FeatureId.src2dst_bytes_id)
            current_feature = (bit<MAX_FEATURE_SIZE_BITS>) meta.flow.features.src2dst_bytes;
        else if (feature_id == FeatureId.src2dst_max_ps_id)
            current_feature = (bit<MAX_FEATURE_SIZE_BITS>) meta.flow.features.src2dst_max_ps;
        else if (feature_id == FeatureId.dst2src_ack_packets_id)
            current_feature = (bit<MAX_FEATURE_SIZE_BITS>) meta.flow.features.dst2src_ack_packets;
        else if (feature_id == FeatureId.src2dst_packets_id)
            current_feature = (bit<MAX_FEATURE_SIZE_BITS>) meta.flow.features.src2dst_packets;
        else if (feature_id == FeatureId.src2dst_psh_packets_id)
            current_feature = (bit<MAX_FEATURE_SIZE_BITS>) meta.flow.features.src2dst_psh_packets;
        else if (feature_id == FeatureId.dst2src_packets_id)
            current_feature = (bit<MAX_FEATURE_SIZE_BITS>) meta.flow.features.dst2src_packets;
        else if (feature_id == FeatureId.src2dst_ack_packets_id)
            current_feature = (bit<MAX_FEATURE_SIZE_BITS>) meta.flow.features.src2dst_ack_packets;
        else if (feature_id == FeatureId.dst2src_fin_packets_id)
            current_feature = (bit<MAX_FEATURE_SIZE_BITS>) meta.flow.features.dst2src_fin_packets;
        else if (feature_id == FeatureId.bidirectional_psh_packets_id)
            current_feature = (bit<MAX_FEATURE_SIZE_BITS>) meta.flow.features.bidirectional_psh_packets;
        else if (feature_id == FeatureId.bidirectional_fin_packets_id)
            current_feature = (bit<MAX_FEATURE_SIZE_BITS>) meta.flow.features.bidirectional_fin_packets;
        else if (feature_id == FeatureId.src2dst_syn_packets_id)
            current_feature = (bit<MAX_FEATURE_SIZE_BITS>) meta.flow.features.src2dst_syn_packets;
        else if (feature_id == FeatureId.dst2src_psh_packets_id)
            current_feature = (bit<MAX_FEATURE_SIZE_BITS>) meta.flow.features.dst2src_psh_packets;
        else if (feature_id == FeatureId.dst2src_syn_packets_id)
            current_feature = (bit<MAX_FEATURE_SIZE_BITS>) meta.flow.features.dst2src_syn_packets;
        else if (feature_id == FeatureId.bidirectional_syn_packets_id)
            current_feature = (bit<MAX_FEATURE_SIZE_BITS>) meta.flow.features.bidirectional_syn_packets;
        else if (feature_id == FeatureId.bidirectional_ack_packets_id)
            current_feature = (bit<MAX_FEATURE_SIZE_BITS>) meta.flow.features.bidirectional_ack_packets;
        
        // compare the value of the selected feature to the given threshold
        // feature_larger_than_thr = 0: feature value does not be compared
        // feature_larger_than_thr = 1: feature value is less than threshold
        // feature_larger_than_thr = 2: feature value is larger than threshold
        if ((current_feature * 10) <= threshold)
            meta.feature_larger_than_thr = 1;
        else
            meta.feature_larger_than_thr = 2;
    }


    /**
    * Classify the flow
    **/
    action classify_flow(bit<3> tree_index, bit<1> class, bit<GINI_VALUE_BITS> gini_value, bit<NODE_ID_BITS> leaf_index) {
        // set the classified and class feature of the tree accordingly
        if (tree_index == 1) {
            meta.flow.class_tree_1 = class;
            meta.flow.classified_tree_1 = 1;
            meta.gini_value_tree_1 = gini_value;
            meta.leaf_node_id_tree_1 = leaf_index;
        } else if (tree_index == 2) {
            meta.flow.class_tree_2 = class;
            meta.flow.classified_tree_2 = 1;
            meta.gini_value_tree_2 = gini_value;
            meta.leaf_node_id_tree_2 = leaf_index;
        } else if (tree_index == 3) {
            meta.flow.class_tree_3 = class;
            meta.flow.classified_tree_3 = 1;
            meta.gini_value_tree_3 = gini_value;
            meta.leaf_node_id_tree_3 = leaf_index;
        }
        // all trees classify flow after the same number of packets have been seen.
        meta.flow.classified = 1;
        // reset the node id and feature_larger_than_thr to 0
        meta.current_node_id = 0;
        meta.feature_larger_than_thr = 0;
    }


    /** 
    * Encapsulate the packet in header which is sent to the controller
    **/
    action send_to_controller() {
        // set packet in header to valid
        hdr.pkt_in.setValid();
        // modify the egress port to CPU_PORT
        standard_metadata.egress_spec = CPU_PORT;

        hdr.pkt_in.packet_type = ControllerPacketType_t.PACKET_IN;
        hdr.pkt_in.opcode = ControllerOpcode_t.CLASSIFY_REQUEST;
        hdr.pkt_in.flow_id = meta.flow.flow_id;
        hdr.pkt_in.features = meta.flow.features;
    }


    action drop() {
        mark_to_drop(standard_metadata);
    }


    action ipv4_forward(egressSpec_t port) {
        standard_metadata.egress_spec = port;
        hdr.ipv4.ttl = hdr.ipv4.ttl - 1;
    }

    /**
    * label the real class of flows in Tuesday dataset.
    **/
    action label_real_class_tues(out bit<1> label) {
        if ((meta.flow.src_ipv4_addr == IP2int.id_172_16_0_1))
            label = 1;
        else 
            label = 0;
    }

    /**
    * label the real class of flows in Wednesday dataset.
    **/
    action label_real_class_wed(out bit<1> label) {
        if (meta.flow.src_ipv4_addr == IP2int.id_172_16_0_1)
            label = 1;
        else 
            label = 0;
    }

    /**
    * label the real class of flows in Thursday dataset.
    **/
    action label_real_class_thur(out bit<1> label) {
        if ((meta.flow.src_ipv4_addr == IP2int.id_192_168_10_8) || (meta.flow.src_ipv4_addr == IP2int.id_172_16_0_1))
            label = 1;
        else 
            label = 0;
    }

    /**
    * label the real class of flows in Friday dataset.
    **/
    action label_real_class_fri(out bit<1> label) {
        if ((meta.flow.src_ipv4_addr == IP2int.id_192_168_10_12) && (meta.flow.dst_ipv4_addr == IP2int.id_52_6_13_28) ||
            (meta.flow.src_ipv4_addr == IP2int.id_192_168_10_50) && (meta.flow.dst_ipv4_addr == IP2int.id_172_16_0_1) ||
            (meta.flow.src_ipv4_addr == IP2int.id_172_16_0_1) && (meta.flow.dst_ipv4_addr == IP2int.id_192_168_10_50) ||
            (meta.flow.src_ipv4_addr == IP2int.id_192_168_10_17) && (meta.flow.dst_ipv4_addr == IP2int.id_52_7_235_158) ||
            (meta.flow.src_ipv4_addr == IP2int.id_192_168_10_8) && (meta.flow.dst_ipv4_addr == IP2int.id_205_174_165_73) ||
            (meta.flow.src_ipv4_addr == IP2int.id_192_168_10_5) && (meta.flow.dst_ipv4_addr == IP2int.id_205_174_165_73) ||
            (meta.flow.src_ipv4_addr == IP2int.id_192_168_10_14) && (meta.flow.dst_ipv4_addr == IP2int.id_205_174_165_73) ||
            (meta.flow.src_ipv4_addr == IP2int.id_192_168_10_9) && (meta.flow.dst_ipv4_addr == IP2int.id_205_174_165_73) ||
            (meta.flow.src_ipv4_addr == IP2int.id_205_174_165_73) && (meta.flow.dst_ipv4_addr == IP2int.id_192_168_10_8) ||
            (meta.flow.src_ipv4_addr == IP2int.id_192_168_10_15) && (meta.flow.dst_ipv4_addr == IP2int.id_205_174_165_73)) 

            label = 1;
        else 
            label = 0;
    }


    table forward_table {
    	key = {
    	    hdr.ipv4.dstAddr: lpm;
            // meta.flow.class: exact;
    	}
        actions = {
            ipv4_forward;
            drop;
            NoAction;
        }
        size = 1024;
        default_action = NoAction();
    }



    /************************* feature match-action table ********************/

    table table_cmp_feature_tree_1_level_0 {
        key = {
            meta.current_node_id: exact;
            meta.feature_larger_than_thr: exact;
        }
        actions = {
            compare_feature;
            classify_flow;
        }
        size = 100;
    }

    table table_cmp_feature_tree_1_level_1 {
        key = {
            meta.current_node_id: exact;
            meta.feature_larger_than_thr: exact;
        }
        actions = {
            compare_feature;
            classify_flow;
        }
        size = 100;
    }

    table table_cmp_feature_tree_1_level_2 {
        key = {
            meta.current_node_id: exact;
            meta.feature_larger_than_thr: exact;
        }
        actions = {
            compare_feature;
            classify_flow;
        }
        size = 100;
    }

    table table_cmp_feature_tree_1_level_3 {
        key = {
            meta.current_node_id: exact;
            meta.feature_larger_than_thr: exact;
        }
        actions = {
            compare_feature;
            classify_flow;
        }
        size = 100;
    }

    table table_cmp_feature_tree_1_level_4 {
        key = {
            meta.current_node_id: exact;
            meta.feature_larger_than_thr: exact;
        }
        actions = {
            compare_feature;
            classify_flow;
        }
        size = 100;
    }

    table table_cmp_feature_tree_1_level_5 {
        key = {
            meta.current_node_id: exact;
            meta.feature_larger_than_thr: exact;
        }
        actions = {
            compare_feature;
            classify_flow;
        }
        size = 100;
    }


    table table_cmp_feature_tree_2_level_0 {
        key = {
            meta.current_node_id: exact;
            meta.feature_larger_than_thr: exact;
        }
        actions = {
            compare_feature;
            classify_flow;
        }
        size = 100;
    }

    table table_cmp_feature_tree_2_level_1 {
        key = {
            meta.current_node_id: exact;
            meta.feature_larger_than_thr: exact;
        }
        actions = {
            compare_feature;
            classify_flow;
        }
        size = 100;
    }

    table table_cmp_feature_tree_2_level_2 {
        key = {
            meta.current_node_id: exact;
            meta.feature_larger_than_thr: exact;
        }
        actions = {
            compare_feature;
            classify_flow;
        }
        size = 100;
    }

    table table_cmp_feature_tree_2_level_3 {
        key = {
            meta.current_node_id: exact;
            meta.feature_larger_than_thr: exact;
        }
        actions = {
            compare_feature;
            classify_flow;
        }
        size = 100;
    }

    table table_cmp_feature_tree_2_level_4 {
        key = {
            meta.current_node_id: exact;
            meta.feature_larger_than_thr: exact;
        }
        actions = {
            compare_feature;
            classify_flow;
        }
        size = 100;
    }

    table table_cmp_feature_tree_2_level_5 {
        key = {
            meta.current_node_id: exact;
            meta.feature_larger_than_thr: exact;
        }
        actions = {
            compare_feature;
            classify_flow;
        }
        size = 100;
    }


    table table_cmp_feature_tree_3_level_0 {
        key = {
            meta.current_node_id: exact;
            meta.feature_larger_than_thr: exact;
        }
        actions = {
            compare_feature;
            classify_flow;
        }
        size = 100;
    }

    table table_cmp_feature_tree_3_level_1 {
        key = {
            meta.current_node_id: exact;
            meta.feature_larger_than_thr: exact;
        }
        actions = {
            compare_feature;
            classify_flow;
        }
        size = 100;
    }

    table table_cmp_feature_tree_3_level_2 {
        key = {
            meta.current_node_id: exact;
            meta.feature_larger_than_thr: exact;
        }
        actions = {
            compare_feature;
            classify_flow;
        }
        size = 100;
    }

    table table_cmp_feature_tree_3_level_3 {
        key = {
            meta.current_node_id: exact;
            meta.feature_larger_than_thr: exact;
        }
        actions = {
            compare_feature;
            classify_flow;
        }
        size = 100;
    }

    table table_cmp_feature_tree_3_level_4 {
        key = {
            meta.current_node_id: exact;
            meta.feature_larger_than_thr: exact;
        }
        actions = {
            compare_feature;
            classify_flow;
        }
        size = 100;
    }

    table table_cmp_feature_tree_3_level_5 {
        key = {
            meta.current_node_id: exact;
            meta.feature_larger_than_thr: exact;
        }
        actions = {
            compare_feature;
            classify_flow;
        }
        size = 100;
    }


    apply {
        // deal with packets with predicted flow class from controller
        if (hdr.pkt_out.isValid()) {            
            flow_from_controller_counter.count(0);
            // read flow entry from register and convert bitstring to struct
            flow_buffer_32.read(meta.bitstring, hdr.pkt_out.flow_id);
            bitstring_to_struct();

            // assign the flow with real class label (only used to computed confusion matrix)
            // bit<1> real_label = 0;
            // Tuesday
            // label_real_class_tues(real_label);
            // Wednesday
            // label_real_class_wed(real_label);
            // Thursday
            // label_real_class_thur(real_label);
            // Friday
            // label_real_class_fri(real_label);


            // measure the classification time caused by CP-IDS
            bit<CLASSIFICATION_TIME_BITS> tmp_time_diff_1 = (bit<CLASSIFICATION_TIME_BITS>) (standard_metadata.ingress_global_timestamp - 
                                                                                            meta.flow.packet_8th_seen_ms);
            bit<CLASSIFICATION_TIME_BITS> tmp_time_sum_1 = 0; 
            classification_time_controller_register.read(tmp_time_sum_1, 0);
            tmp_time_sum_1 = tmp_time_sum_1 + tmp_time_diff_1;
            classification_time_controller_register.write(0, tmp_time_sum_1);

            // label the flow entry according the predicted class from controller
            meta.flow.class = hdr.pkt_out.class;
            // store the updated flow entry in buffer
            struct_to_bitstring();
            flow_buffer_32.write(hdr.pkt_out.flow_id, meta.bitstring);
        }
        // deal with packets from network interface
        // only process the tcp and udp packets
        if (hdr.ipv4.isValid() && (hdr.tcp.isValid() || hdr.udp.isValid())) {
            // count the total ipv4 pacekts
            packet_ipv4_total_counter.count(0);

            // determine the ports of current packet (distinguished between TCP and UDP)
            if (hdr.tcp.isValid()) {
                meta.current_packet_src_port = hdr.tcp.srcPort;
                meta.current_packet_dst_port = hdr.tcp.dstPort;
            } else if (hdr.udp.isValid()) {
                meta.current_packet_src_port = hdr.udp.srcPort;
                meta.current_packet_dst_port = hdr.udp.dstPort;
            }

            /************************************** Extract Flow Entry **************************************/
            /************************************************************************************************/

            /**************************** control flag setting  ****************************/
            // flag that indicates if the packet belongs to a flow in buffer. used to enter the update and classification block
            bool is_stored_in_buffer = false;
            // flag that indicates the existed flow id does not match the current packet, need to check if the reversed flow id exists in buffer 
            bool check_reversed_id = false;
            // flag that indicates hash collision occurs
            bool is_hash_collision = false;
            // flag that indicates it's a new flow
            bool is_new_flow = false;


            /**************************** check the src <-> src flow ****************************/
            // calculate flow id using crc32
            hash(meta.current_flow_id, 
                 HashAlgorithm.crc32,
                 (bit<32>)1, 
                 {hdr.ipv4.srcAddr, hdr.ipv4.dstAddr, meta.current_packet_src_port, meta.current_packet_dst_port, hdr.ipv4.protocol}, 
                 (bit<32>)FLOW_BUCKET
                 ); 

            // read flow entry from register and convert bitstring to struct
            flow_buffer_32.read(meta.bitstring, meta.current_flow_id);
            bitstring_to_struct(); 

            // If flow exists in buffer, check if this flow is usable.
            if (meta.flow.stored == 1) {
                if ((standard_metadata.ingress_global_timestamp - meta.flow.bidirectional_first_seen_ms) > TIMEOUT_EXPIRATION) {
                    // expire this flow entry
                    meta.flow.stored = 0;
                } else {
                    // compare each 5-tuple value (src <-> src)
                    if ((hdr.ipv4.protocol == meta.flow.protocol) &&
                        (hdr.ipv4.srcAddr == meta.flow.src_ipv4_addr) && 
                        (hdr.ipv4.dstAddr == meta.flow.dst_ipv4_addr) &&
                        (meta.current_packet_src_port == meta.flow.src_port) &&
                        (meta.current_packet_dst_port == meta.flow.dst_port)) {

                        // the current packet belongs to this flow (src <-> src) (BINGO!!!!!!!)
                        is_stored_in_buffer = true;
                    } else {
                        // the existed flow id does not match the current packet, need to check the reversed flow id
                        check_reversed_id = true;
                    }
                }
            } 

            /**************************** check the src <-> dst flow ****************************/
            // Three cases entering this block 
            //   1. the src <-> src flow id does not exist in flow buffer.
            //   2. the src <-> src flow id is expired.
            //   3. the src <-> src flow id exists in flow buffer, but the 5-tuple of current packet does not match the extracted flow entry.

            bit<FLOW_ID_BITS> current_reversed_flow_id;
            if (meta.flow.stored == 0 || check_reversed_id) {                
                hash(current_reversed_flow_id, 
                     HashAlgorithm.crc32,
                     (bit<32>)1, 
                     {hdr.ipv4.dstAddr, hdr.ipv4.srcAddr, meta.current_packet_dst_port, meta.current_packet_src_port, hdr.ipv4.protocol}, 
                     (bit<32>)FLOW_BUCKET
                     ); 

                // read the flow entry with reversed flow id and convert the bitstring to struct
                flow_buffer_32.read(meta.bitstring, current_reversed_flow_id);
                bitstring_to_struct(); 
                
                // check if src <-> dst flow id exists in buffer
                if (meta.flow.stored == 1) {
                    if ((standard_metadata.ingress_global_timestamp - meta.flow.bidirectional_first_seen_ms) > TIMEOUT_EXPIRATION) {
                        // expire this flow entry
                        meta.flow.stored = 0;
                    } else {
                        // compare each 5-tuple value (src <-> dst)
                        if ((hdr.ipv4.protocol == meta.flow.protocol) &&
                            (hdr.ipv4.dstAddr == meta.flow.src_ipv4_addr) && 
                            (hdr.ipv4.srcAddr == meta.flow.dst_ipv4_addr) &&
                            (meta.current_packet_dst_port == meta.flow.src_port) &&
                            (meta.current_packet_src_port == meta.flow.dst_port)) {

                            // the current packet belongs to this flow (src <-> dst) (BINGO!!!!!!!)
                            is_stored_in_buffer = true;
                            // set the flag bit to indicate it's a dst2src packet
                            meta.is_dst2src = 1;
                        } else {
                            // the 5-tuple of src <-> dst flow does not match the current packet
                            if (check_reversed_id) {
                                // Both the src <-> src flow id and src <-> dst (revsersed) flow id exist in buffer, 
                                // but none of 5-tuple of two flows match the current packet. 
                                // It means hash collision occurs. 
                                is_hash_collision = true;
                            } else {
                                // src <-> src flow id does not exist in the flow buffer or is already expired.
                                // The 5-tuple of src <-> dst flow does not match the current packet (it's not a dst2src pacekt). 
                                // It means the current packet belongs to a new flow.
                                is_new_flow = true;
                            }
                        }
                    }
                } else {
                    if (check_reversed_id) {
                        // the src <-> src flow id exists in buffer, but 5-tuple of src <-> src flow does not match the current packet. 
                        // src <-> dst (reversed) flow id is not in the flow buffer.
                        // It means hash collision occurs. 
                        // Why? A flow is always initilized by the first src2dst packet. src<->src 5-tuple does not match indicates this packet
                        // could be a dst2src pacekt or a hash collision happens. src<->dst flow id does not exist in the flow buffer, that 
                        // indicates this packet is not a dst2src packet. Therefore, a hash collision occurs.
                        is_hash_collision = true;
                    } else {
                        // src <-> src flow id is not in the flow buffer or is expired. 
                        // src <-> dst (reversed) flow id is not in the flow buffer.
                        // It means the current packet belongs to a new flow.
                        is_new_flow = true;
                    }
                }
            }

            /************************************** Initialize, Updata and Classify Flow **************************************/
            /******************************************************************************************************************/

            // initialize the node id to the dummy node
            meta.current_node_id = 0;
            
            // the current packet belongs to a flow in buffer
            if (is_stored_in_buffer) {
                // The flow is classified, forward or drop packet according to the class.
                if (meta.flow.classified == 1) {
                    // This packet is Benign, forward it
                    if (meta.flow.class == 0) {
                        forward_table.apply();
                    }
                    // This packet is Attack, drop it
                    else {
                        drop();
                    }
                } else {
                    // Flow is still not classified. Update the flow entry.
                    update_flow();

                    // if the 8th packet enters switch, trigger classification
                    if (meta.flow.features.bidirectional_packets == USED_PACKETS) {

                        /************************* random forest **************************/
                        // tree 1
                        table_cmp_feature_tree_1_level_0.apply();
                        if (meta.flow.classified_tree_1 == 0) {
                            table_cmp_feature_tree_1_level_1.apply();
                        }
                        if (meta.flow.classified_tree_1 == 0) {
                            table_cmp_feature_tree_1_level_2.apply();
                        }
                        if (meta.flow.classified_tree_1 == 0) {
                            table_cmp_feature_tree_1_level_3.apply();
                        }
                        if (meta.flow.classified_tree_1 == 0) {
                            table_cmp_feature_tree_1_level_4.apply();
                        }
                        if (meta.flow.classified_tree_1 == 0) {
                            table_cmp_feature_tree_1_level_5.apply();
                        }

                        // tree 2
                        table_cmp_feature_tree_2_level_0.apply();
                        if (meta.flow.classified_tree_2 == 0) {
                            table_cmp_feature_tree_2_level_1.apply();
                        }
                        if (meta.flow.classified_tree_2 == 0) {
                            table_cmp_feature_tree_2_level_2.apply();
                        }
                        if (meta.flow.classified_tree_2 == 0) {
                            table_cmp_feature_tree_2_level_3.apply();
                        }
                        if (meta.flow.classified_tree_2 == 0) {
                            table_cmp_feature_tree_2_level_4.apply();
                        }
                        if (meta.flow.classified_tree_2 == 0) {
                            table_cmp_feature_tree_2_level_5.apply();
                        }

                        // tree 3
                        table_cmp_feature_tree_3_level_0.apply();
                        if (meta.flow.classified_tree_3 == 0) {
                            table_cmp_feature_tree_3_level_1.apply();
                        }
                        if (meta.flow.classified_tree_3 == 0) {
                            table_cmp_feature_tree_3_level_2.apply();
                        }
                        if (meta.flow.classified_tree_3 == 0) {
                            table_cmp_feature_tree_3_level_3.apply();
                        }
                        if (meta.flow.classified_tree_3 == 0) {
                            table_cmp_feature_tree_3_level_4.apply();
                        }
                        if (meta.flow.classified_tree_3 == 0) {
                            table_cmp_feature_tree_3_level_5.apply();
                        }
                    }

                    
                    /************************* voting and final classification **************************/
                    if (meta.flow.classified == 1) {
                        flow_classified_counter.count(0);
                        // concatenate the predicted class of each tree in a 3 bits string
                        bit<3> class_string = meta.flow.class_tree_1 ++ meta.flow.class_tree_2 ++ meta.flow.class_tree_3;
                        bit<16> sum_gini_3_trees_value = 0;
                        bit<16> avg_gini_2_trees_value = 0;

                        // assign the flow with real class label (only used to computed confusion matrix)
                        // bit<1> real_label = 0;
                        // Tuesday
                        // label_real_class_tues(real_label);
                        // Wednesday
                        // label_real_class_wed(real_label);
                        // Thursday
                        // label_real_class_thur(real_label);
                        // Friday
                        // label_real_class_fri(real_label);

                        // tree 1: 0 
                        // tree 2: 0
                        // tree 3: 0
                        if (class_string == 0) {
                            sum_gini_3_trees_value = meta.gini_value_tree_1 + meta.gini_value_tree_2 + meta.gini_value_tree_3;
                            if (sum_gini_3_trees_value <= GINI_VALUE_THRESHOLD * 3) {
                                meta.flow.class = 0;
                                flow_predicted_p4_sum_counter.count(0);
                                // set flag to True, used to accumulate the classification time in egress pipeline 
                                meta.accumulate_time_p4_flag = 1;
                            } else {
                                // send flow to controller
                                send_to_controller();
                                flow_predicted_controller_sum_counter.count(0);
                            } 
                        } 
                        // tree 1: 0 
                        // tree 2: 0
                        // tree 3: 1
                        else if (class_string == 1) {
                            avg_gini_2_trees_value = (meta.gini_value_tree_1 + meta.gini_value_tree_2) >> 1;
                            if ((avg_gini_2_trees_value <= GINI_VALUE_THRESHOLD) && (avg_gini_2_trees_value <= meta.gini_value_tree_3)){
                                meta.flow.class = 0;
                                flow_predicted_p4_sum_counter.count(0);
                                // set flag to True, used to accumulate the classification time in egress pipeline 
                                meta.accumulate_time_p4_flag = 1;
                            } else {
                                // send flow to controller
                                send_to_controller();
                                flow_predicted_controller_sum_counter.count(0);
                            }
                        } 
                        // tree 1: 0 
                        // tree 2: 1
                        // tree 3: 0
                        else if (class_string == 2) {
                            avg_gini_2_trees_value = (meta.gini_value_tree_1 + meta.gini_value_tree_3) >> 1;
                            if ((avg_gini_2_trees_value <= GINI_VALUE_THRESHOLD) && (avg_gini_2_trees_value <= meta.gini_value_tree_2)){
                                meta.flow.class = 0;
                                flow_predicted_p4_sum_counter.count(0);
                                // set flag to True, used to accumulate the classification time in egress pipeline 
                                meta.accumulate_time_p4_flag = 1;
                            } else {
                                // send flow to controller
                                send_to_controller();
                                flow_predicted_controller_sum_counter.count(0);
                            }                        
                        } 
                        // tree 1: 0 
                        // tree 2: 1
                        // tree 3: 1
                        else if (class_string == 3) {
                            avg_gini_2_trees_value = (meta.gini_value_tree_2 + meta.gini_value_tree_3) >> 1;
                            if ((avg_gini_2_trees_value <= GINI_VALUE_THRESHOLD) && (avg_gini_2_trees_value <= meta.gini_value_tree_1)){
                                meta.flow.class = 1;
                                flow_predicted_p4_sum_counter.count(0);
                                // set flag to True, used to accumulate the classification time in egress pipeline 
                                meta.accumulate_time_p4_flag = 1;
                            } else {
                                // send flow to controller
                                send_to_controller();
                                flow_predicted_controller_sum_counter.count(0);                 
                            }                        
                        } 
                        // tree 1: 1
                        // tree 2: 0
                        // tree 3: 0
                        else if (class_string == 4) {      
                            avg_gini_2_trees_value = (meta.gini_value_tree_2 + meta.gini_value_tree_3) >> 1;
                            if ((avg_gini_2_trees_value <= GINI_VALUE_THRESHOLD) && (avg_gini_2_trees_value <= meta.gini_value_tree_1)){
                                meta.flow.class = 0;
                                flow_predicted_p4_sum_counter.count(0);
                                // set flag to True, used to accumulate the classification time in egress pipeline 
                                meta.accumulate_time_p4_flag = 1;
                            } else {
                                // send flow to controller
                                send_to_controller();
                                flow_predicted_controller_sum_counter.count(0);
                            }                                                    
                        } 
                        // tree 1: 1
                        // tree 2: 0
                        // tree 3: 1
                        else if (class_string == 5) {
                            avg_gini_2_trees_value = (meta.gini_value_tree_1 + meta.gini_value_tree_3) >> 1;
                            if ((avg_gini_2_trees_value <= GINI_VALUE_THRESHOLD) && (avg_gini_2_trees_value <= meta.gini_value_tree_2)){
                                meta.flow.class = 1;
                                flow_predicted_p4_sum_counter.count(0);
                                // set flag to True, used to accumulate the classification time in egress pipeline 
                                meta.accumulate_time_p4_flag = 1;
                            } else {
                                // send flow to controller
                                send_to_controller();
                                flow_predicted_controller_sum_counter.count(0);
                            }                                                    
                        } 
                        // tree 1: 1
                        // tree 2: 1
                        // tree 3: 0
                        else if (class_string == 6) {         
                            avg_gini_2_trees_value = (meta.gini_value_tree_1 + meta.gini_value_tree_2) >> 1;
                            if ((avg_gini_2_trees_value <= GINI_VALUE_THRESHOLD) && (avg_gini_2_trees_value <= meta.gini_value_tree_3)){
                                meta.flow.class = 1;
                                flow_predicted_p4_sum_counter.count(0);
                                // set flag to True, used to accumulate the classification time in egress pipeline 
                                meta.accumulate_time_p4_flag = 1;
                            } else {
                                // send flow to controller
                                send_to_controller();
                                flow_predicted_controller_sum_counter.count(0);  
                            }                                                  
                        } 
                        // tree 1: 1
                        // tree 2: 1
                        // tree 3: 1
                        else if (class_string == 7) {      
                            sum_gini_3_trees_value = meta.gini_value_tree_1 + meta.gini_value_tree_2 + meta.gini_value_tree_3;
                            if (sum_gini_3_trees_value <= GINI_VALUE_THRESHOLD * 3){
                                meta.flow.class = 1;
                                flow_predicted_p4_sum_counter.count(0);
                                // set flag to True, used to accumulate the classification time in egress pipeline 
                                meta.accumulate_time_p4_flag = 1;
                            } else {
                                // send flow to controller
                                send_to_controller();
                                flow_predicted_controller_sum_counter.count(0);
                            }                                                 
                        }                        
                    }

                    // store the updated features into the flow buffer.
                    // the feature "class" would be updated (when MC is high), if the 8th packet enters switch.
                    // Therefore, struct_to_bitstring and register write operations should be placed after classification logic block.
                    struct_to_bitstring();
                    flow_buffer_32.write(meta.flow.flow_id, meta.bitstring);
                    forward_table.apply();
                }

            } 
            // the current packet does not belong to a flow in buffer
            else {
                // It's a new flow. Initialize the new flow
                if (is_new_flow) {
                    // initialize the other features
                    init_flow();

                    struct_to_bitstring();
                    flow_buffer_32.write(meta.flow.flow_id, meta.bitstring);
                    forward_table.apply();
                }
            }
        }
    }
}

/*************************************************************************
****************  E G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {

    // store the sum of classification time in P4
    register<bit<CLASSIFICATION_TIME_BITS>>(1) classification_time_p4_egress_register;
    
    apply {
        if (meta.accumulate_time_p4_flag == 1) {
            bit<CLASSIFICATION_TIME_BITS> tmp_time_diff = (bit<CLASSIFICATION_TIME_BITS>) (standard_metadata.egress_global_timestamp - 
                                                                                            standard_metadata.ingress_global_timestamp );

            bit<CLASSIFICATION_TIME_BITS> tmp_time_sum = 0; 
            classification_time_p4_egress_register.read(tmp_time_sum, 0);
            tmp_time_sum = tmp_time_sum + tmp_time_diff;

            classification_time_p4_egress_register.write(0, tmp_time_sum);
        }
      }
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