#!/usr/bin/python3

from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.term import makeTerm


def customTopo():
    net = Mininet(controller=RemoteController, link=TCLink, switch=OVSSwitch)

    print("*** Adding controller")
    c0 = net.addController('c0', port=6633)

    print("*** Adding switches")
    s1 = net.addSwitch('s1')  # Local switch
    s2 = net.addSwitch('s2')  # Remote switch

    print("*** Adding hosts")
    h1 = net.addHost('h1', ip='10.0.0.1/24')
    h2 = net.addHost('h2', ip='10.0.0.2/24')
    h3 = net.addHost('h3', ip='10.0.0.3/24')
    h4 = net.addHost('h4', ip='10.0.0.4/24')

    print("*** Creating links")
    net.addLink(h1, s1)
    net.addLink(h2, s1)
    net.addLink(h3, s2)
    net.addLink(h4, s2)

    net.build()
    c0.start()
    s1.start([c0])
    s2.start([c0])

    # Tạo VXLAN giữa s1 và s2
    print("*** Setting up VXLAN tunnels")
    s1.cmd('ovs-vsctl add-port s1 vxlan10 -- set interface vxlan10 type=vxlan options:remote_ip=10.0.0.3 options:key=10')
    s1.cmd('ovs-vsctl add-port s1 vxlan20 -- set interface vxlan20 type=vxlan options:remote_ip=10.0.0.4 options:key=20')

    s2.cmd('ovs-vsctl add-port s2 vxlan10 -- set interface vxlan10 type=vxlan options:remote_ip=10.0.0.1 options:key=10')
    s2.cmd('ovs-vsctl add-port s2 vxlan20 -- set interface vxlan20 type=vxlan options:remote_ip=10.0.0.2 options:key=20')

    net.startTerms()
    print("*** Running CLI")
    CLI(net)

    net.stop()

if __name__ == '__main__':
    customTopo()
