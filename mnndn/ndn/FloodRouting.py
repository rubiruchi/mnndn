from Routing import Routing

class FloodRouting(Routing):
    """Setup default route toward every peer.
       If used with multicast strategy, this shall cause a flooding."""
    def __init__(self, host):
        Routing.__init__(self, host)

    def start(self):
        fw = self.host.fw
        for (myIntf, peerIntf, ndnPeerIntfs) in self.host.getPeers():
            for ndnPeerIntf in ndnPeerIntfs:
                peerIp = ndnPeerIntf.node.IP(ndnPeerIntf)
                if peerIp is None:
                    continue
                face = fw.addFace(myIntf, ndnPeerIntf)
                fw.addRoute(face, '/')

    def stop(self):
        pass

    def doAdvertise(self, prefix):
        pass

    def doWithdraw(self, prefix):
        pass

    def beginGetRoutes(self):
        return None

    def endGetRoutes(self, wh):
        return ['/']
