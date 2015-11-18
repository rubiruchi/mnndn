from mininet.node import Host

def __collectPeers(nodeIntf):
    if isinstance(nodeIntf.node, Host):
        return [ nodeIntf ]
    peerIntfs = []
    for intf in nodeIntf.node.intfList():
        link = intf.link
        if not link:
            continue
        intf1, intf2 = link.intf1, link.intf2
        if intf1.node == nodeIntf.node and intf1 != nodeIntf:
            peerIntfs += __collectPeers(intf2)
        elif intf2.node == nodeIntf.node and intf2 != nodeIntf:
            peerIntfs += __collectPeers(intf1)
    return peerIntfs

def assignIps(net):
    """Assign IPv4 addresses to every host intf in the network,
       so that intfs on every L3 broadcast domain are in the same subnet."""
    seenIntfs = set()
    l3Links = []

    for node in net.hosts:
        for intf in node.intfList():
            if intf in seenIntfs:
                continue

            link = intf.link
            if not link:
                continue

            l3Link = [ intf ]
            if link.intf1.node == node:
                l3Link += __collectPeers(link.intf2)
            elif link.intf2.node == node:
                l3Link += __collectPeers(link.intf1)

            seenIntfs.update(l3Link)
            l3Links.append(l3Link)

    x = 0
    for l3Link in l3Links:
        y = 0
        for intf in l3Link:
            ip = '10.%d.%d.%d' % (x / 100 + 1, x % 100 + 1, y + 1)
            intf.node.setIP(ip, 24, intf)
            y += 1
        x += 1
