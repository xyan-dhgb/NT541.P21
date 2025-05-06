from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, ipv4, tcp, ether_types

class QoSController(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(QoSController, self).__init__(*args, **kwargs)
        self.mac_to_port = {}
        # Map MAC prefix to QoS settings
        self.mac_to_qos = {
            '00:00:00:00:10': {'queue': 10, 'rate': 5},  # Student: 5 Mbps
            '00:00:00:00:20': {'queue': 20, 'rate': 10}, # Teacher: 10 Mbps
            '00:00:00:00:30': {'queue': 30, 'rate': 15}  # Staff: 15 Mbps
        }
        self.ip_to_mac = {}
        self.server_mac = '00:00:00:00:00:64'  # Server MAC address
        self.server_ip = '10.0.0.100'          # Server IP address
        self.dpid_to_dp = {}  # Keep track of datapath objects

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        dpid = datapath.id
        
        # Save datapath object
        self.dpid_to_dp[dpid] = datapath
        
        # Clear any existing flows
        self.clear_flows(datapath)
        
        # Install table-miss flow entry
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)
        
        # Log the switch connection
        self.logger.info(f"Switch {dpid} connected")

    def clear_flows(self, datapath):
        """Clear all flow entries in the switch"""
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        
        # Clear flow table
        match = parser.OFPMatch()
        instructions = []
        flow_mod = parser.OFPFlowMod(
            datapath=datapath,
            command=ofproto.OFPFC_DELETE,
            out_port=ofproto.OFPP_ANY,
            out_group=ofproto.OFPG_ANY,
            match=match,
            instructions=instructions
        )
        datapath.send_msg(flow_mod)
        self.logger.info(f"Cleared all flows from datapath {datapath.id}")

    def add_flow(self, datapath, priority, match, actions, buffer_id=None, hard_timeout=0, idle_timeout=0):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                    priority=priority, match=match,
                                    instructions=inst,
                                    hard_timeout=hard_timeout,
                                    idle_timeout=idle_timeout)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    match=match, instructions=inst,
                                    hard_timeout=hard_timeout,
                                    idle_timeout=idle_timeout)
        datapath.send_msg(mod)
        self.logger.info(f"Added flow: {match} with actions {actions}")

    def get_qos_settings(self, mac_addr):
        """Get QoS settings based on MAC prefix"""
        prefix = mac_addr[:14]  # Get the first 14 characters (MAC prefix)
        if prefix in self.mac_to_qos:
            return self.mac_to_qos[prefix]
        return None

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']
        dpid = datapath.id

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]

        # Ignore LLDP packets
        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            return

        dst = eth.dst
        src = eth.src

        # Learn MAC addresses
        self.mac_to_port.setdefault(dpid, {})
        self.mac_to_port[dpid][src] = in_port

        # Learn IP to MAC mapping
        ip_pkt = pkt.get_protocol(ipv4.ipv4)
        if ip_pkt:
            self.ip_to_mac[ip_pkt.src] = src
            self.logger.info(f"Learned IP {ip_pkt.src} -> MAC {src}")

        # Determine output port
        out_port = ofproto.OFPP_FLOOD
        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]

        # Get QoS settings for source MAC
        qos_settings = self.get_qos_settings(src)
        
        # Create actions based on QoS settings
        actions = []
        if qos_settings and out_port != ofproto.OFPP_FLOOD:
            queue_id = qos_settings['queue']
            self.logger.info(f"Applying QoS for MAC {src}, Queue: {queue_id}, Rate: {qos_settings['rate']} Mbps")
            actions = [
                parser.OFPActionSetQueue(queue_id),
                parser.OFPActionOutput(out_port)
            ]
        else:
            actions = [parser.OFPActionOutput(out_port)]

        # Install flow rule if we have a specific destination
        if dst != 'ff:ff:ff:ff:ff:ff' and out_port != ofproto.OFPP_FLOOD:
            if ip_pkt:
                # Check if this is traffic to or from the server
                if ip_pkt.dst == self.server_ip or dst == self.server_mac:
                    # Traffic TO server - apply QoS based on source
                    if qos_settings:
                        queue_id = qos_settings['queue']
                        self.logger.info(f"Installing flow for {src} -> server with QoS queue {queue_id}")
                        
                        # Install specific rule for this flow
                        match = parser.OFPMatch(
                            eth_type=ether_types.ETH_TYPE_IP,
                            ipv4_src=ip_pkt.src,
                            ipv4_dst=ip_pkt.dst
                        )
                        self.add_flow(datapath, 100, match, actions, hard_timeout=300)
                        
                        # Also install a rule for return traffic from server
                        # This ensures symmetrical QoS
                        out_port_return = self.mac_to_port[dpid].get(src)
                        if out_port_return:
                            return_actions = [
                                parser.OFPActionSetQueue(queue_id),
                                parser.OFPActionOutput(out_port_return)
                            ]
                            return_match = parser.OFPMatch(
                                eth_type=ether_types.ETH_TYPE_IP,
                                ipv4_src=ip_pkt.dst,
                                ipv4_dst=ip_pkt.src
                            )
                            self.add_flow(datapath, 100, return_match, return_actions, hard_timeout=300)
                
                # For other traffic, install normal flows
                else:
                    match = parser.OFPMatch(
                        eth_type=ether_types.ETH_TYPE_IP,
                        ipv4_src=ip_pkt.src,
                        ipv4_dst=ip_pkt.dst
                    )
                    self.add_flow(datapath, 90, match, actions, hard_timeout=300)
            
            # Low priority rule for traffic from this source
            if qos_settings:
                match = parser.OFPMatch(eth_src=src)
                self.add_flow(datapath, 10, match, actions, hard_timeout=300)

        # Send packet out
        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                 in_port=in_port, actions=actions, data=data)
        datapath.send_msg(out)