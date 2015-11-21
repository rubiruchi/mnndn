#!/usr/bin/python2
"""Example with GridSpikeTopo and StaticRouting."""

import time
import functools

from mininet.log import setLogLevel
from mininet.net import Mininet
from mininet.cli import CLI

from mnndn.ndn import NdnHost,StaticRouting
from mnndn.topo import GridSpikeTopo,assignIps

def run():
    topo = GridSpikeTopo(3, 3, 1)
    net = Mininet(topo, controller=None,
                  host=functools.partial(NdnHost, rout=StaticRouting))
    net.start()
    assignIps(net)

    print 'Start forwarding.'
    fws = [ host.getFw() for host in net.hosts ]
    for fw in fws:
        fw.start()
    time.sleep(5)

    print 'Setup routes.'
    routs = [ host.getRout() for host in net.hosts ]
    for rout in routs:
        rout.start(net)

    for hostName in topo.spikeNodes():
        row, col, spike = GridSpikeTopo.parseHostName(hostName)
        net[hostName].getRout().advertise('/h%dx%d/s%d' % (row, col, spike))

    CLI(net)

    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run()
