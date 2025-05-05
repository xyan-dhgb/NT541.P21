#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSKernelSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink
from mininet.term import makeTerm
import os
import sys
import time
import logging
import subprocess

# Initialize project path
PROJECT_PATH = '/home/bacan/NT541.P21/server-ping'

# Initialize logging
logging.basicConfig(
    filename=os.path.join(PROJECT_PATH, 'mininet_debug.log'),
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('Campus_Topology')

def startController():
    """Start Ryu controller in a separate process"""
    logger.info("Start Ryu controller...")
    controller_script = os.path.join(PROJECT_PATH, 'back_up_controller.py')
    controller_log = open(os.path.join(PROJECT_PATH, 'controller.log'), 'w')
    return subprocess.Popen(
        ['ryu-manager', controller_script],
        stdout=controller_log,
        stderr=controller_log
    )

def createNetworkTopo():
    """Create campus network topology with 3 buildings and 3 VLANs"""
    net = Mininet(controller=None, switch=OVSKernelSwitch, link=TCLink)
    
    # Add remote controller
    c0 = net.addController('c0', controller=RemoteController, ip='127.0.0.1', port=6653)
    
    # Create 3 switches for buildings A, B, C
    s1 = net.addSwitch('s1')  # Building A
    s2 = net.addSwitch('s2')  # Building B
    s3 = net.addSwitch('s3')  # Building C
    
    # Connect switches to each other
    net.addLink(s1, s2, cls=TCLink, bw=100)
    net.addLink(s2, s3, cls=TCLink, bw=100)

    
    # Create server
    server = net.addHost('server', ip='10.0.0.100/24', mac='00:00:00:00:00:64')
    net.addLink(server, s3, cls=TCLink, bw=100)
    
    # Create hosts for VLANs in each building
    # VLAN Student - 10.0.10.x
    studentA = net.addHost('student_A', ip='10.0.0.1/24', mac='00:00:00:00:10:01')
    studentB = net.addHost('student_B', ip='10.0.0.2/24', mac='00:00:00:00:10:02')

    # VLAN Teacher - 10.0.20.x
    teacherA = net.addHost('teacher_A', ip='10.0.0.3/24', mac='00:00:00:00:20:01')
    teacherB = net.addHost('teacher_B', ip='10.0.0.4/24', mac='00:00:00:00:20:02')

    # VLAN Staff - 10.0.30.x
    staffA = net.addHost('staff_A', ip='10.0.0.5/24', mac='00:00:00:00:30:01')
    staffB = net.addHost('staff_B', ip='10.0.0.6/24', mac='00:00:00:00:30:02')

    # Connect hosts to switches by building
    # Building A - s1
    net.addLink(studentA, s1, cls=TCLink, bw=100)
    net.addLink(teacherA, s1, cls=TCLink, bw=100)
    net.addLink(staffA, s1, cls=TCLink, bw=100)
    
    # Building B - s2
    net.addLink(studentB, s2, cls=TCLink, bw=100)
    net.addLink(teacherB, s2, cls=TCLink, bw=100)
    net.addLink(staffB, s2, cls=TCLink, bw=100)
    return net

# def configureNetwork(net):
#     """Configure routes and ARP for hosts"""
#     logger.info("Configuring routes for hosts...")
#
#     # Make sure all hosts have a direct route to server
#     for host in net.hosts:
#         if host.name != 'server':
#             # Delete default route if it exists
#             host.cmd('ip route del default')
#             # Create static route to connect directly to server network
#             host.cmd('ip route add 10.0.0.0/24 dev {}-eth0'.format(host.name))
#             # Add default route
#             host.cmd('ip route add default via 10.0.0.100')
#             # Add static ARP entry to ensure connection to server
#             host.cmd('arp -s 10.0.0.100 00:00:00:00:00:64')
#
#     # Configure server to accept packages from subnets
#     server = net.get('server')
#     server.cmd('sysctl -w net.ipv4.ip_forward=1')
#     # Allow server to know how to reach subnets
#     server.cmd('ip route add 10.0.10.0/24 dev server-eth0')
#     server.cmd('ip route add 10.0.20.0/24 dev server-eth0')
#     server.cmd('ip route add 10.0.30.0/24 dev server-eth0')
#
#     # Test connectivity between hosts and server using ping
#     logger.info("Testing connectivity with ping...")
#     for host in net.hosts:
#         if host.name != 'server':
#             result = host.cmd('ping -c 1 10.0.0.100')
#             if '1 received' in result:
#                 logger.info("{} can ping server".format(host.name))
#             else:
#                 logger.error("{} cannot ping server".format(host.name))
#                 logger.error(result)

# def openXterm(net, hosts):
#     """Open xterm for specified hosts"""
#     for host in hosts:
#         if host in net.keys():
#             info("*** Opening xterm for {}\n".format(host))
#             net[host].cmd('xterm -title "{}" -e "bash" &'.format(host))
#             time.sleep(0.5)  # Wait for each xterm

# Extend Mininet CLI to add custom xterm command
class CustomCLI(CLI):
    def do_xterm(self, line):
        """Open xterm for a host: xterm <host>"""
        args = line.split()
        if len(args) != 1:
            print("Usage: xterm <hostname>")
            return
        host_name = args[0]
        if host_name not in self.mn:
            print("Error: Host '{}' not found".format(host_name))
            return
        host = self.mn[host_name]
        # Use makeTerm from mininet.term
        makeTerm(host, title=host_name)

def main():
    """Main function to set up and run the network"""
    setLogLevel('info')
    
    # Start controller
    controller_proc = startController()
    info("*** Waiting for controller to start (5 seconds)...\n")
    time.sleep(5)  # Wait for controller to start longer
    
    # Create and configure network
    info("*** Creating network topology...\n")
    net = createNetworkTopo()
    info("*** Starting network\n")
    net.start()
    
    # Configure hosts
    # info("*** Configuring network...\n")
    # configureNetwork(net)

    # Optional: open xterm for server and some hosts for easier monitoring
    # Uncomment the line below if you want to open xterm
    # openXterm(net, ['server', 'student_A', 'teacher_A', 'staff_A'])
    
    info("\n*** Network is ready. You can check connectivity as follows:\n")
    info("  student_A wget -qO- http://10.0.0.100:8080\n")
    info("  teacher_A wget -qO- http://10.0.0.100:8080\n")
    info("  staff_A wget -qO- http://10.0.0.100:8080\n")
    
    # If you want to open xterm from CLI, you can use the command 'xterm <hostname>'
    info("\n*** To open xterm for a host, use the command:\n")
    info("  xterm <hostname>\n")
    info("  Example: xterm server\n")
    
    # Start Mininet CLI with custom CLI
    info("\n*** If server does not respond, you can check the log by:\n")
    info("  server cat /tmp/server.log\n")
    CustomCLI(net)
    
    # Cleanup when finished
    info("*** Stopping network\n")
    net.stop()
    controller_proc.kill()
    os.system('sudo mn -c')  # Clean up any remaining resources

if __name__ == '__main__':
    main()