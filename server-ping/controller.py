#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, ipv4, tcp
import logging
import os

# Initialize project path
PROJECT_PATH = '/home/giabao/Documents/server-ping'

# Initialize logging
logging.basicConfig(
    filename=os.path.join(PROJECT_PATH, 'controller.log'),
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('Campus_Controller')

class CampusController(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(CampusController, self).__init__(*args, **kwargs)
        self.mac_to_port = {}
        # Server MAC and IP for reference
        self.server_ip = '10.0.0.100'
        self.server_mac = '00:00:00:00:00:64'
        
        # VLAN information
        self.vlan_info = {
            '10.0.10.': 'STUDENT',  # Student VLAN
            '10.0.20.': 'TEACHER',  # Teacher VLAN
            '10.0.30.': 'STAFF'     # Staff VLAN
        }
        
        logger.info("Controller initialized successfully")

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        
        logger.info("Switch connected: {}".format(datapath.id))

        # Install the table-miss flow entry
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)

    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                    priority=priority, match=match,
                                    instructions=inst)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    match=match, instructions=inst)
        datapath.send_msg(mod)
        logger.debug("Flow added - Switch: {}, Priority: {}".format(datapath.id, priority))

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]

        dst = eth.dst
        src = eth.src

        dpid = datapath.id
        self.mac_to_port.setdefault(dpid, {})

        # Log packet info for debugging
        logger.debug("Packet in - Switch: {}, Src MAC: {}, Dst MAC: {}, In Port: {}".format(
                    dpid, src, dst, in_port))

        # Check for IP packet
        ip_pkt = pkt.get_protocol(ipv4.ipv4)
        src_ip = None
        dst_ip = None
        
        if ip_pkt:
            src_ip = ip_pkt.src
            dst_ip = ip_pkt.dst
            logger.debug("IP Packet - Src IP: {}, Dst IP: {}".format(src_ip, dst_ip))
            
            # Determine VLAN based on source IP
            src_vlan = None
            for prefix, vlan in self.vlan_info.items():
                if src_ip.startswith(prefix):
                    src_vlan = vlan
                    break
            
            if src_vlan:
                logger.debug("Packet from VLAN: {}".format(src_vlan))
        
        # Learn MAC address to avoid FLOOD
        self.mac_to_port[dpid][src] = in_port

        # Determine output port
        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD

        actions = [parser.OFPActionOutput(out_port)]

        # Install flows for packets between clients and server
        if ip_pkt and out_port != ofproto.OFPP_FLOOD:
            # Handle traffic between hosts and server
            if dst_ip == self.server_ip or src_ip == self.server_ip:
                # Packets to or from server
                if dst_ip == self.server_ip:
                    # From client to server
                    match = parser.OFPMatch(
                        in_port=in_port,
                        eth_type=0x0800,  # IPv4
                        ipv4_src=src_ip,
                        ipv4_dst=dst_ip
                    )
                    self.add_flow(datapath, 2, match, actions)
                    logger.debug("Added flow from client {} to server".format(src_ip))
                else:
                    # From server to client
                    match = parser.OFPMatch(
                        in_port=in_port,
                        eth_type=0x0800,  # IPv4
                        ipv4_src=src_ip,
                        ipv4_dst=dst_ip
                    )
                    self.add_flow(datapath, 2, match, actions)
                    logger.debug("Added flow from server to client {}".format(dst_ip))
            else:
                # Packets between clients (no special handling needed)
                match = parser.OFPMatch(
                    in_port=in_port,
                    eth_dst=dst
                )
                self.add_flow(datapath, 1, match, actions)

        # Send packet out
        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = parser.OFPPacketOut(datapath=datapath,
                                  buffer_id=msg.buffer_id,
                                  in_port=in_port,
                                  actions=actions,
                                  data=data)
        datapath.send_msg(out) 