class Face:
    def __init__(self, faceId):
        self.id = faceId

class Forwarder:
    "NDN forwarder."
    def __init__(self, host):
        self.host = host

    def start(self):
        "Start the forwarder."
        raise NotImplementedError

    def stop(self):
        "Stop the forwarder."
        raise NotImplementedError

    def addFace(self, localIntf, remoteIntf):
        """Add a face.
           returns Face"""
        raise NotImplementedError

    def addRoute(self, face, name):
        "Add a route."
        raise NotImplementedError
