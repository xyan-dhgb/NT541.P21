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
PROJECT_PATH = '/home/giabao/Documents/server-ping'

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
    controller_script = os.path.join(PROJECT_PATH, 'controller.py')
    controller_log = open(os.path.join(PROJECT_PATH, 'controller.log'), 'w')
    return subprocess.Popen(
        ['ryu-manager', controller_script],
        stdout=controller_log,
        stderr=controller_log
    )

# def startServer(net, open_xterm=False):
#     """Start Flask server on the server host"""
#     logger.info("Start Flask server...")
#     server = net.get('server')
    
#     # Try to install Flask on server host
#     logger.info("Installing Flask on server host...")
#     server.cmd('pip install flask --user')
    
#     # Create a simple server.py file directly on server host
#     logger.info("Creating server.py on server host...")
#     simple_server = """#!/usr/bin/env python
# from flask import Flask, request
# app = Flask(__name__)

# @app.route('/')
# def index():
#     client_ip = request.remote_addr
#     if client_ip.startswith('10.0.10.'):
#         return "Chào Student!"
#     elif client_ip.startswith('10.0.20.'):
#         return "Chào Teacher!"
#     elif client_ip.startswith('10.0.30.'):
#         return "Chào Staff!"
#     else:
#         return "Xin chào! IP của bạn là " + client_ip

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=8080)
# """
    
#     # Create server.py file directly on host
#     server.cmd('echo \'{}\' > /tmp/server.py'.format(simple_server))
#     server.cmd('chmod +x /tmp/server.py')
    
#     # Open xterm for server if requested
#     if open_xterm:
#         # Open xterm and run server in it
#         makeTerm(server, title="Server", cmd="bash -c 'python /tmp/server.py; bash'")
#         logger.info("Server running in xterm")
#     else:
#         # Run server
#         logger.info("Running server...")
#         server.cmd('python /tmp/server.py > /tmp/server.log 2>&1 &')
    
#     # Wait for server to start
#     time.sleep(2)
    
#     # Check if server is running
#     logger.info("Checking if server is running...")
#     result = server.cmd('ps aux | grep "[p]ython /tmp/server.py"')
#     if result:
#         logger.info("Server is running!")
#     else:
#         logger.error("Server failed to start!")
    
#     # Test server connection from server host
#     logger.info("Testing server connection from server host...")
#     response = server.cmd('wget -qO- http://localhost:8080')
#     logger.info("Server response: {}".format(response))

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
    studentA = net.addHost('student_A', ip='10.0.10.11/24', mac='00:00:00:00:10:01')
    studentB = net.addHost('student_B', ip='10.0.10.12/24', mac='00:00:00:00:10:02')
    studentC = net.addHost('student_C', ip='10.0.10.13/24', mac='00:00:00:00:10:03')
    
    # VLAN Teacher - 10.0.20.x
    teacherA = net.addHost('teacher_A', ip='10.0.20.11/24', mac='00:00:00:00:20:01')
    teacherB = net.addHost('teacher_B', ip='10.0.20.12/24', mac='00:00:00:00:20:02')
    teacherC = net.addHost('teacher_C', ip='10.0.20.13/24', mac='00:00:00:00:20:03')
    
    # VLAN Staff - 10.0.30.x
    staffA = net.addHost('staff_A', ip='10.0.30.11/24', mac='00:00:00:00:30:01')
    staffB = net.addHost('staff_B', ip='10.0.30.12/24', mac='00:00:00:00:30:02')
    staffC = net.addHost('staff_C', ip='10.0.30.13/24', mac='00:00:00:00:30:03')
    
    # Connect hosts to switches by building
    # Building A - s1
    net.addLink(studentA, s1, cls=TCLink, bw=100)
    net.addLink(teacherA, s1, cls=TCLink, bw=100)
    net.addLink(staffA, s1, cls=TCLink, bw=100)
    
    # Building B - s2
    net.addLink(studentB, s2, cls=TCLink, bw=100)
    net.addLink(teacherB, s2, cls=TCLink, bw=100)
    net.addLink(staffB, s2, cls=TCLink, bw=100)
    
    # Building C - s3

    # net.addLink(studentC, s3, cls=TCLink, bw=100)
    # # net.addLink(teacherC, s3, cls=TCLink, bw=100)
    # # net.addLink(staffC, s3, cls=TCLink, bw=100)
    
    return net

def configureNetwork(net):
    """Configure routes and ARP for hosts"""
    logger.info("Configuring routes for hosts...")
    
    # Make sure all hosts have a direct route to server
    for host in net.hosts:
        if host.name != 'server':
            # Delete default route if it exists
            host.cmd('ip route del default')
            # Create static route to connect directly to server network
            host.cmd('ip route add 10.0.0.0/24 dev {}-eth0'.format(host.name))
            # Add default route
            host.cmd('ip route add default via 10.0.0.100')
            # Add static ARP entry to ensure connection to server
            host.cmd('arp -s 10.0.0.100 00:00:00:00:00:64')
    
    # Configure server to accept packages from subnets
    server = net.get('server')
    server.cmd('sysctl -w net.ipv4.ip_forward=1')
    # Allow server to know how to reach subnets
    server.cmd('ip route add 10.0.10.0/24 dev server-eth0')
    server.cmd('ip route add 10.0.20.0/24 dev server-eth0')
    server.cmd('ip route add 10.0.30.0/24 dev server-eth0')
    
    # Test connectivity between hosts and server using ping
    logger.info("Testing connectivity with ping...")
    for host in net.hosts:
        if host.name != 'server':
            result = host.cmd('ping -c 1 10.0.0.100')
            if '1 received' in result:
                logger.info("{} can ping server".format(host.name))
            else:
                logger.error("{} cannot ping server".format(host.name))
                logger.error(result)

def openXterm(net, hosts):
    """Open xterm for specified hosts"""
    for host in hosts:
        if host in net.keys():
            info("*** Opening xterm for {}\n".format(host))
            net[host].cmd('xterm -title "{}" -e "bash" &'.format(host))
            time.sleep(0.5)  # Wait for each xterm

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
    info("*** Configuring network...\n")
    configureNetwork(net)
    
    # # Start server
    # info("*** Starting server...\n")
    # startServer(net, open_xterm=False)  # Set to True if you want to open xterm for server
    # info("*** Waiting for server to start (5 seconds)...\n")
    # time.sleep(5)  # Wait for server to start longer
    
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