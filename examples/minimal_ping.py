#!/usr/bin/python2

import time

from mininet.log import setLogLevel
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.cli import CLI

from ndn import NdnHost,Routing
from app import NdnPingServer
from tracer import NdnDump

class TwoNodeTopo(Topo):
    """Two node directly connected topology.
       This differs from mininet.topo.MinimalTopo in that there's no switch."""
    def build(self, **params):
        self.addHost('h1')
        self.addHost('h2')
        self.addLink('h1', 'h2')

def run():
    topo = TwoNodeTopo()
    net = Mininet(topo, host=NdnHost, controller=None)
    net.start()

    ndndumps = []
    print 'Start ndndump tracers.'
    ndndumps = [ NdnDump(link) for link in net.links ]
    for ndndump in ndndumps:
        ndndump.start()

    print 'Start forwarding.'
    fws = [ host.getFw() for host in net.hosts ]
    for fw in fws:
        fw.start()
    time.sleep(5)

    print 'Start routing.'
    routs = [ host.getRout() for host in net.hosts ]
    for rout in routs:
        rout.advertise('/%s' % rout.host.name)
        rout.start()

    convergeTime = Routing.waitForConverge(net)
    if convergeTime is False:
        print 'Routing is not converged'
        net.stop()
        exit(1)
    print 'Routing is converged in %d seconds.' % convergeTime

    print 'Start ping servers.'
    pingServers = [ NdnPingServer(host, '/%s' % host.name) for host in net.hosts ]
    for pingServer in pingServers:
        pingServer.start()

    CLI(net)

    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run()
