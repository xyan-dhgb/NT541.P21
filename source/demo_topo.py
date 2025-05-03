from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types


class VLANSwitch13(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(VLANSwitch13, self).__init__(*args, **kwargs)
        self.mac_to_port = {}

        self.mac_to_vlan = {
            # VLAN 10
            '00:00:00:00:00:01': 10,
            '00:00:00:00:00:05': 10,
            '00:00:00:00:00:09': 10,
            '00:00:00:00:00:0d': 10,

            # VLAN 20
            '00:00:00:00:00:02': 20,
            '00:00:00:00:00:06': 20,
            '00:00:00:00:00:0a': 20,
            '00:00:00:00:00:0e': 20,

            # VLAN 30
            '00:00:00:00:00:03': 30,
            '00:00:00:00:00:07': 30,
            '00:00:00:00:00:0b': 30,
            '00:00:00:00:00:0f': 30,

            # VLAN 40
            '00:00:00:00:00:04': 40,
            '00:00:00:00:00:08': 40,
            '00:00:00:00:00:0c': 40,
            '00:00:00:00:00:10': 40
        }

    def get_vlan_id(self, mac_addr):
        return self.mac_to_vlan.get(mac_addr, 0)

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

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

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        if ev.msg.msg_len < ev.msg.total_len:
            self.logger.debug("packet truncated: only %s of %s bytes",
                              ev.msg.msg_len, ev.msg.total_len)
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]

        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            # Ignore LLDP packets
            return

        dst = eth.dst
        src = eth.src

        dpid = format(datapath.id, "d").zfill(16)
        self.mac_to_port.setdefault(dpid, {})

        # Get VLAN IDs for source and destination
        src_vlan = self.get_vlan_id(src)
        dst_vlan = self.get_vlan_id(dst)

        self.logger.info("Packet in %s from %s (VLAN %s) to %s (VLAN %s) at port %s",
                         dpid, src, src_vlan, dst, dst_vlan, in_port)

        # Learn the port for this MAC to avoid FLOOD next time
        self.mac_to_port[dpid][src] = in_port

        # Determine output port
        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD

        actions = []

        # VLAN enforcement: Only allow communication within the same VLAN
        # If source or destination is not in any VLAN, default to traditional switching
        if src_vlan == 0 or dst_vlan == 0 or dst == 'ff:ff:ff:ff:ff:ff':
            # Special handling for broadcast and unknown VLANs
            actions = [parser.OFPActionOutput(out_port)]
        elif src_vlan == dst_vlan:
            # Same VLAN - forward packet
            actions = [parser.OFPActionOutput(out_port)]
        else:
            # Different VLANs - drop packet (no actions)
            self.logger.info("Dropping packet: source and destination are in different VLANs")
            return

        # If we have a valid output port and it's not flooding, install a flow
        if out_port != ofproto.OFPP_FLOOD and actions:
            # For same VLAN or unknown VLAN, create a flow entry
            match = parser.OFPMatch(in_port=in_port, eth_dst=dst, eth_src=src)

            if msg.buffer_id != ofproto.OFP_NO_BUFFER:
                self.add_flow(datapath, 1, match, actions, msg.buffer_id)
                return
            else:
                self.add_flow(datapath, 1, match, actions)

        # If we're flooding or if we need to send a packet out
        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        if actions:  # Only send if we have actions
            out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                      in_port=in_port, actions=actions, data=data)
            datapath.send_msg(out)

