#!/usr/bin/python2

import time
from sched import scheduler

from mininet.log import setLogLevel
from mininet.net import Mininet
from mininet.link import TCLink

from topo import GridTopo
from ndn import NdnHost,Routing
from app import NdnPing,NdnPingServer
from tracer import NdnDump

def parseCommandLine():
    import argparse

    parser = argparse.ArgumentParser(description='Emulates grid topology with link failures.')
    parser.add_argument('--rows', type=int, default=2, choices=xrange(2, GridTopo.MAX_NROWS + 1),
                        help='number of grid rows')
    parser.add_argument('--cols', type=int, default=2, choices=xrange(2, GridTopo.MAX_NCOLS + 1),
                        help='number of grid columns')
    parser.add_argument('--linkfail', metavar='x1,y1,x2,y2,t1,t2', action='append',
                        help='fails the link between (x1,y1) and (x2-y2) during t1-t2 time')
    parser.add_argument('--duration', type=int, default=60,
                        help='duration of emulation after routing convergence')
    parser.add_argument('--no-ndndump', action='store_true',
                        help='disable ndndump')
    parser.add_argument('--no-ping', action='store_true',
                        help='disable ping')
    args = parser.parse_args()

    rowRange = range(args.rows)
    colRange = range(args.cols)
    args.linkFails = []
    if args.linkfail is not None:
        for linkfail in args.linkfail:
            try:
                x1, y1, x2, y2, t1, t2 = [ int(x) for x in linkfail.split(',') ]
            except ValueError:
                parser.error('Invalid --linkfail argument.')
            if x1 not in rowRange or \
               x2 not in rowRange or \
               y1 not in colRange or \
               y2 not in colRange:
                parser.error('--linkfail %s: index out of range.' % linkfail)
            if t1 < 0 or t2 < t1:
                parser.error('--linkfail %s: failure must occur before recovery.' % linkfail)
        args.linkFails.append((x1, y1, x2, y2, t1, t2))

    return args

def schedLinkFails(sched, net, linkFails):
    def fail(intf):
        intf.config(loss=100)
    def recover(intf):
        # loss=0 alone would be ignored, so we add bw=1000
        intf.config(bw=1000, loss=0)
    def do(t, h1, h2, act):
        print '%d %s %s-%s' % (t, act.func_name, h1.name, h2.name)
        connections = h1.connectionsTo(h2)
        for (intf1, intf2) in connections:
            act(intf1)
            act(intf2)

    for (x1, y1, x2, y2, t1, t2) in linkFails:
        h1 = net.get(GridTopo.makeHostName(x1, y1))
        h2 = net.get(GridTopo.makeHostName(x2, y2))
        sched.enter(t1, 0, do, (t1, h1, h2, fail))
        sched.enter(t2, 0, do, (t2, h1, h2, recover))

def run(args):
    topo = GridTopo(args.rows, args.cols)
    net = Mininet(topo, host=NdnHost, link=TCLink)
    topo.assignIps(net)
    net.start()

    ndndumps = []
    if not args.no_ndndump:
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
        print 'Routing is not converged.'
        net.stop()
        exit(1)
    print 'Routing is converged in %d seconds at %d.' % (convergeTime, time.time())

    pingServers = []
    pingClients = []
    if not args.no_ping:
        print 'Start ping servers and clients.'
        for host in net.hosts:
            pingServer = NdnPingServer(host, '/%s' % host.name)
            pingServer.start()
            pingServers.append(pingServer)
            for otherHost in net.hosts:
                pingClient = NdnPing(host, '/%s' % otherHost.name)
                pingClient.start('/var/log/ndn/ndnping_%s.log' % otherHost.name)
                pingClients.append(pingClient)

    sched = scheduler(time.time, time.sleep)
    schedLinkFails(sched, net, args.linkFails)
    sched.enter(args.duration, 0, lambda:0, ())
    sched.run()

    if not args.no_ping:
        print 'Stop ping clients.'
        for pingClient in pingClients:
            pingClient.stop()
        time.sleep(1)

    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    args = parseCommandLine()
    run(args)
