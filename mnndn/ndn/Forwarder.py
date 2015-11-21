class Face:
    def __init__(self, faceId, localIntf, remoteIntf):
        self.id = faceId
        self.localIntf = localIntf
        self.remoteIntf = remoteIntf

class Forwarder:
    """NDN forwarder."""
    def __init__(self, host):
        self.host = host

    def start(self):
        """Start the forwarder."""
        raise NotImplementedError

    def stop(self):
        """Stop the forwarder."""
        raise NotImplementedError

    def addFace(self, localIntf, remoteIntf):
        """Add a face.
           returns Face"""
        raise NotImplementedError

    def addRoute(self, face, name):
        """Add a route."""
        raise NotImplementedError

    @staticmethod
    def connectPeers(net):
        """Create faces on every NdnHost toward each of its peers.
           return [ face ]"""
        from NdnHost import NdnHost

        faces = []
        for host in net.hosts:
            if not isinstance(host, NdnHost):
                continue
            for (myIntf, peerIntf, ndnPeerIntfs) in host.getPeers():
                for ndnPeerIntf in ndnPeerIntfs:
                    faces.append(host.getFw().addFace(myIntf, ndnPeerIntf))
        return faces
