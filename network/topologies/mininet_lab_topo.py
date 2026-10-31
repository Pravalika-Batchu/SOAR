#!/usr/bin/env python3
"""
Academic Research Mininet Topology for Trust-Aware SOAR
Creates a dual-switch virtual SDN testbed with 5 hosts:
- h1: Critical Web Portal (10.0.0.10)
- h2: Critical DNS Resolver (10.0.0.53)
- h3: Database Server (10.0.0.20)
- h4: Legitimate Corporate Client (10.0.0.101)
- h5: Controlled Attacker Agent (10.0.0.99)
- Switches: s1 (Core Service Switch), s2 (Access Switch)
- Controller: Remote Ryu OpenFlow 1.3 Controller
"""

import sys
from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink

def build_trust_soar_topology():
    net = Mininet(
        controller=RemoteController,
        switch=OVSSwitch,
        link=TCLink,
        autoSetMacs=True,
        autoStaticArp=True
    )

    info("*** Adding Remote Ryu Controller at 127.0.0.1:6653\n")
    c0 = net.addController('c0', controller=RemoteController, ip='127.0.0.1', port=6653)

    info("*** Adding Open vSwitch Bridges s1 and s2\n")
    s1 = net.addSwitch('s1', protocols='OpenFlow13')
    s2 = net.addSwitch('s2', protocols='OpenFlow13')

    info("*** Adding Virtual Hosts with Lab Subnet 10.0.0.0/24\n")
    h1 = net.addHost('h1', ip='10.0.0.10/24', defaultRoute='via 10.0.0.200') # Web Portal
    h2 = net.addHost('h2', ip='10.0.0.53/24', defaultRoute='via 10.0.0.200') # DNS
    h3 = net.addHost('h3', ip='10.0.0.20/24', defaultRoute='via 10.0.0.200') # DB
    h4 = net.addHost('h4', ip='10.0.0.101/24', defaultRoute='via 10.0.0.200') # Client
    h5 = net.addHost('h5', ip='10.0.0.99/24', defaultRoute='via 10.0.0.200') # Attacker

    info("*** Wiring Inter-Switch Link (1 Gbps trunk)\n")
    net.addLink(s1, s2, bw=1000, delay='1ms')

    info("*** Wiring Server Hosts to Core Switch s1 (100 Mbps with SLA)\n")
    net.addLink(h1, s1, bw=100, delay='1ms')
    net.addLink(h2, s1, bw=100, delay='1ms')
    net.addLink(h3, s1, bw=100, delay='1ms')

    info("*** Wiring Client & Attacker Hosts to Access Switch s2\n")
    net.addLink(h4, s2, bw=50, delay='2ms')
    net.addLink(h5, s2, bw=50, delay='2ms')

    info("*** Starting Network\n")
    net.build()
    c0.start()
    s1.start([c0])
    s2.start([c0])

    info("*** Network operational. Ready for security orchestration experiments.\n")
    return net

if __name__ == '__main__':
    setLogLevel('info')
    net = build_trust_soar_topology()
    CLI(net)
    net.stop()

