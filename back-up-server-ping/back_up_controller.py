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
from ryu.lib.packet import ether_types

PROJECT_PATH = 'ENTER YOUR PATH HERE'  # Replace with your project path

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
        # # Server MAC and IP for reference
        self.server_ip = '10.0.0.100'
        self.server_mac = '00:00:00:00:00:64'

        # VLAN information
        # self.vlan_info = {
        #     '10.0.10.': 'STUDENT',  # Student VLAN
        #     '10.0.20.': 'TEACHER',  # Teacher VLAN
        #     '10.0.30.': 'STAFF'     # Staff VLAN
        # }
        self.mac_to_vlan = {
            # VLAN 10 - Students
            '00:00:00:00:10:01': 10,
            '00:00:00:00:10:02': 10,

            # VLAN 20 - Teachers
            '00:00:00:00:20:01': 20,
            '00:00:00:00:20:02': 20,

            # VLAN 30 - Staff
            '00:00:00:00:30:01': 30,
            '00:00:00:00:30:02': 30,

            # Server - special VLAN 40
            '00:00:00:00:00:64': 40,
        }

    def get_vlan_id(self, mac_addr):
        return self.mac_to_vlan.get(mac_addr, 0)

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

        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            return

        dst = eth.dst
        src = eth.src

        dpid = format(datapath.id, "d").zfill(16)
        self.mac_to_port.setdefault(dpid, {})

        src_vlan = self.get_vlan_id(src)
        dst_vlan = self.get_vlan_id(dst)

        self.logger.info("Packet in %s from %s (VLAN %s) to %s (VLAN %s) at port %s",
                         dpid, src, src_vlan, dst, dst_vlan, in_port)

        self.mac_to_port[dpid][src] = in_port

        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD

        actions = []

        if dst == 'ff:ff:ff:ff:ff:ff':
            actions = [parser.OFPActionOutput(out_port)]
        elif src_vlan == 0 or dst_vlan == 0:
            # Unknown VLANs – drop packet
            self.logger.info("Dropping packet: unknown VLAN - src %s (VLAN %s), dst %s (VLAN %s)",
                             src, src_vlan, dst, dst_vlan)
            return
        elif src_vlan == dst_vlan:
            # Same VLAN – allow
            actions = [parser.OFPActionOutput(out_port)]
        elif src_vlan == 40 or dst_vlan == 40:
            # Server involved – allow
            actions = [parser.OFPActionOutput(out_port)]
        else:
            # Different VLANs – block
            self.logger.info("Dropping packet between different VLANs: %s (VLAN %s) → %s (VLAN %s)",
                             src, src_vlan, dst, dst_vlan)
            return

        if out_port != ofproto.OFPP_FLOOD and actions:
            # For same VLAN or unknown VLAN, create a flow entry
            match = parser.OFPMatch(in_port=in_port, eth_dst=dst, eth_src=src)

            if msg.buffer_id != ofproto.OFP_NO_BUFFER:
                self.add_flow(datapath, 1, match, actions, msg.buffer_id)
                return
            else:
                self.add_flow(datapath, 1, match, actions)

        # # Install flows for packets between clients and server
        # if ip_pkt and out_port != ofproto.OFPP_FLOOD:
        #     # Handle traffic between hosts and server
        #     if dst_ip == self.server_ip or src_ip == self.server_ip:
        #         # Packets to or from server
        #         if dst_ip == self.server_ip:
        #             # From client to server
        #             match = parser.OFPMatch(
        #                 in_port=in_port,
        #                 eth_type=0x0800,  # IPv4
        #                 ipv4_src=src_ip,
        #                 ipv4_dst=dst_ip
        #             )
        #             self.add_flow(datapath, 2, match, actions)
        #             logger.debug("Added flow from client {} to server".format(src_ip))
        #         else:
        #             # From server to client
        #             match = parser.OFPMatch(
        #                 in_port=in_port,
        #                 eth_type=0x0800,  # IPv4
        #                 ipv4_src=src_ip,
        #                 ipv4_dst=dst_ip
        #             )
        #             self.add_flow(datapath, 2, match, actions)
        #             logger.debug("Added flow from server to client {}".format(dst_ip))
        #     else:
        #         # Packets between clients (no special handling needed)
        #         match = parser.OFPMatch(
        #             in_port=in_port,
        #             eth_dst=dst
        #         )
        #         self.add_flow(datapath, 1, match, actions)

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