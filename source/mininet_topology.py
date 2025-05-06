#!/usr/bin/env python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink


class CustomTopo(Topo):

    def build(self):
        # Add switches
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')
        s4 = self.addSwitch('s4')

        # Helper function to generate MAC addresses
        def gen_mac(i):
            return f'00:00:00:00:00:{i:02x}'

        # Add hosts for s1
        for i in range(1, 5):
            ip = f'10.0.0.{i}/24'
            mac = gen_mac(i)
            host = self.addHost(f'h{i}', ip=ip, mac=mac)
            self.addLink(host, s1, bw=10, delay='1ms')

        # Add hosts for s2
        for i in range(5, 9):
            ip = f'10.0.0.{i}/24'
            mac = gen_mac(i)
            host = self.addHost(f'h{i}', ip=ip, mac=mac)
            self.addLink(host, s2, bw=10, delay='1ms')

        # Add hosts for s3
        for i in range(9, 13):
            ip = f'10.0.0.{i}/24'
            mac = gen_mac(i)
            host = self.addHost(f'h{i}', ip=ip, mac=mac)
            self.addLink(host, s3, bw=10, delay='1ms')

        # Add hosts for s4
        for i in range(13, 17):
            ip = f'10.0.0.{i}/24'
            mac = gen_mac(i)
            host = self.addHost(f'h{i}', ip=ip, mac=mac)
            self.addLink(host, s4, bw=10, delay='1ms')

        # Connect links between switches
        self.addLink(s1, s2, bw=20, delay='2ms')
        self.addLink(s2, s3, bw=20, delay='2ms')
        self.addLink(s3, s4, bw=20, delay='2ms')


def setup_network():
    net = Mininet(topo=CustomTopo(),
                  controller=RemoteController('c0', ip='127.0.0.1', port=6653),
                  link=TCLink,
                  autoSetMacs=False)  # IMPORTANT: disable auto MAC to keep custom MACs
    net.start()
    CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    setup_network()

