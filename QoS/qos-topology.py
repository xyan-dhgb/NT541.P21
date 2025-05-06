from mininet.net import Mininet
from mininet.node import RemoteController, OVSKernelSwitch
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel, info
import time

def clear_qos_settings(switch):
    """Remove all QoS settings from a switch"""
    info("Clearing QoS settings from {}\n".format(switch.name))
    switch.cmd('ovs-vsctl --all destroy QoS')
    switch.cmd('ovs-vsctl --all destroy Queue')
    
    # Use intfNames() instead of directly accessing switch.ports.values()
    for intf in switch.intfNames():
        if intf != 'lo':
            switch.cmd('ovs-vsctl clear Port {} qos'.format(intf))

def setup_tc_qos(host, intf_name, bandwidth):
    """Apply direct TC rate limiting on host interfaces"""
    info("Setting up TC rate limiting on {} ({}) to {}Mbps\n".format(host.name, intf_name, bandwidth))
    # Clear any existing qdisc
    host.cmd('tc qdisc del dev {} root'.format(intf_name))
    
    # Set up HTB qdisc with rate limiting
    host.cmd('tc qdisc add dev {} root handle 1: htb default 10'.format(intf_name))
    host.cmd('tc class add dev {} parent 1: classid 1:1 htb rate {}mbit ceil {}mbit'.format(intf_name, bandwidth, bandwidth))
    host.cmd('tc class add dev {} parent 1:1 classid 1:10 htb rate {}mbit ceil {}mbit'.format(intf_name, bandwidth, bandwidth))
    host.cmd('tc filter add dev {} protocol ip parent 1:0 prio 1 u32 match ip dst 0.0.0.0/0 flowid 1:10'.format(intf_name))
    
    # Verify the configuration
    result = host.cmd('tc -s qdisc show dev {}'.format(intf_name))
    info("TC config for {}: {}\n".format(host.name, result))

def create_topology():
    net = Mininet(controller=RemoteController, switch=OVSKernelSwitch, link=TCLink)

    # Add controller
    info("*** Adding controller\n")
    c0 = net.addController('c0', controller=RemoteController, ip='127.0.0.1', port=6653)

    # Add switches
    info("*** Adding switches\n")
    s1 = net.addSwitch('s1')  # Building A
    s2 = net.addSwitch('s2')  # Building B
    s3 = net.addSwitch('s3')  # Building C

    # Add hosts - PUT ALL HOSTS IN SAME SUBNET
    info("*** Adding hosts for Building A\n")
    student_a = net.addHost('student_a', ip='10.0.0.11/24', mac='00:00:00:00:10:01')
    teacher_a = net.addHost('teacher_a', ip='10.0.0.21/24', mac='00:00:00:00:20:01')
    staff_a = net.addHost('staff_a', ip='10.0.0.31/24', mac='00:00:00:00:30:01')

    # Add hosts for Building B
    info("*** Adding hosts for Building B\n")
    student_b = net.addHost('student_b', ip='10.0.0.12/24', mac='00:00:00:00:10:02')
    teacher_b = net.addHost('teacher_b', ip='10.0.0.22/24', mac='00:00:00:00:20:02')
    staff_b = net.addHost('staff_b', ip='10.0.0.32/24', mac='00:00:00:00:30:02')

    # Add hosts for Building C
    info("*** Adding hosts for Building C\n")
    web_server = net.addHost('web_server', ip='10.0.0.100/24', mac='00:00:00:00:00:64')

    # Add links with QoS configuration
    info("*** Adding links\n")
    
    # Building A links
    net.addLink(student_a, s1, bw=20)
    net.addLink(teacher_a, s1, bw=20)
    net.addLink(staff_a, s1, bw=20)

    # Building B links
    net.addLink(student_b, s2, bw=20)
    net.addLink(teacher_b, s2, bw=20)
    net.addLink(staff_b, s2, bw=20)

    # Building C links
    net.addLink(web_server, s3, bw=20)

    # Connect switches
    net.addLink(s1, s2, bw=100)
    net.addLink(s2, s3, bw=100)

    # Start network
    info("*** Starting network\n")
    net.start()
    
    # Wait for controller to initialize
    info("*** Waiting for controller initialization\n")
    time.sleep(5)
    
    # First, clear any existing QoS configurations
    clear_qos_settings(s1)
    clear_qos_settings(s2)
    clear_qos_settings(s3)

    # Configure QoS queues on all switches - using OVS QoS settings
    info("*** Setting up OVS QoS queues\n")
    
    # Important: Make sure queue IDs match what's expected in the controller
    for s in [s1, s2, s3]:
        # Setup QoS properly with correct queue IDs
        info("Setting up QoS on {}\n".format(s.name))
        
        # First, create queues on all ports
        for port in s.intfNames():
            if port != 'lo':
                # Create QoS entries with specific queue IDs
                cmd = """
                ovs-vsctl -- set Port {} qos=@newqos -- \
                --id=@newqos create QoS type=linux-htb \
                other-config:max-rate=100000000 \
                queues=10=@q10,20=@q20,30=@q30,0=@q0 -- \
                --id=@q10 create Queue other-config:min-rate=5000000 other-config:max-rate=5000000 other-config:priority=10 -- \
                --id=@q20 create Queue other-config:min-rate=10000000 other-config:max-rate=10000000 other-config:priority=5 -- \
                --id=@q30 create Queue other-config:min-rate=15000000 other-config:max-rate=15000000 other-config:priority=1 -- \
                --id=@q0 create Queue other-config:min-rate=1000000 other-config:max-rate=20000000 other-config:priority=100
                """.format(port)
                s.cmd(cmd)
                info("QoS configured on port {}\n".format(port))
        
        # Verify queue configuration
        info("Verifying QoS on {}:\n".format(s.name))
        output = s.cmd('ovs-vsctl list queue')
        info(output + "\n")
        
        output = s.cmd('ovs-vsctl list qos')
        info(output + "\n")
    
    # Add TC-based rate limiting directly at the hosts
    info("*** Setting up TC-based rate limiting on hosts\n")
    # Set up TC rate limiting on hosts - this is crucial for enforcing hard limits
    setup_tc_qos(student_a, 'student_a-eth0', 5)  # Student: 5 Mbps
    setup_tc_qos(student_b, 'student_b-eth0', 5)  # Student: 5 Mbps
    setup_tc_qos(teacher_a, 'teacher_a-eth0', 10) # Teacher: 10 Mbps
    setup_tc_qos(teacher_b, 'teacher_b-eth0', 10) # Teacher: 10 Mbps
    setup_tc_qos(staff_a, 'staff_a-eth0', 15)     # Staff: 15 Mbps
    setup_tc_qos(staff_b, 'staff_b-eth0', 15)     # Staff: 15 Mbps
    
    # Also add return path limitations at server end
    # Create bidirectional limiting rules to enforce rate limits in both directions
    info("*** Setting up bidirectional rate limiting rules on server\n")
    # web_server.cmd('tc qdisc add dev web_server-eth0 root handle 1: htb default 1')
    # web_server.cmd('tc class add dev web_server-eth0 parent 1: classid 1:1 htb rate 20mbit ceil 20mbit')
    
    # 1. Create IP-specific classes for different user types
    # For students (MAC 00:00:00:00:10:XX) - limit to 5Mbps
    web_server.cmd('tc qdisc add dev web_server-eth0 root handle 1: htb default 1')
    web_server.cmd('tc class add dev web_server-eth0 parent 1: classid 1:1 htb rate 20mbit ceil 20mbit')
    web_server.cmd('tc class add dev web_server-eth0 parent 1:1 classid 1:10 htb rate 5mbit ceil 5mbit')
    web_server.cmd('tc class add dev web_server-eth0 parent 1:1 classid 1:20 htb rate 10mbit ceil 10mbit')
    web_server.cmd('tc class add dev web_server-eth0 parent 1:1 classid 1:30 htb rate 15mbit ceil 15mbit')
    
    # Add filters to match IP addresses
    # Student IPs
    web_server.cmd('tc filter add dev web_server-eth0 protocol ip parent 1:0 prio 1 u32 match ip dst 10.0.0.11/32 flowid 1:10')
    web_server.cmd('tc filter add dev web_server-eth0 protocol ip parent 1:0 prio 1 u32 match ip dst 10.0.0.12/32 flowid 1:10')
    
    # Teacher IPs
    web_server.cmd('tc filter add dev web_server-eth0 protocol ip parent 1:0 prio 1 u32 match ip dst 10.0.0.21/32 flowid 1:20')
    web_server.cmd('tc filter add dev web_server-eth0 protocol ip parent 1:0 prio 1 u32 match ip dst 10.0.0.22/32 flowid 1:20')
    
    # Staff IPs
    web_server.cmd('tc filter add dev web_server-eth0 protocol ip parent 1:0 prio 1 u32 match ip dst 10.0.0.31/32 flowid 1:30')
    web_server.cmd('tc filter add dev web_server-eth0 protocol ip parent 1:0 prio 1 u32 match ip dst 10.0.0.32/32 flowid 1:30')
    
    # Verify TC configuration on web_server
    result = web_server.cmd('tc -s qdisc show dev web_server-eth0')
    info("TC config for web_server: {}\n".format(result))
    
    result = web_server.cmd('tc -s class show dev web_server-eth0')
    info("TC classes for web_server: {}\n".format(result))
    
    # Open CLI
    CLI(net)

    # Clean up QoS configurations before stopping
    info("*** Removing QoS configurations\n")
    for s in [s1, s2, s3]:
        clear_qos_settings(s)

    # Stop network
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    create_topology()