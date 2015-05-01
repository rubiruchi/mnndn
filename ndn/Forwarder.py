class Face:
    def __init__(self, faceId):
        self.id = faceId

class Forwarder:
    "NDN forwarder."
    def __init__(self, host):
        self.host = host

    def start(self):
        "Start the forwarder."
        raise "not implemented"

    def stop(self):
        "Stop the forwarder."
        raise "not implemented"

    def addFace(self, localIntf, remoteIntf):
        """Add a face.
           returns Face"""
        raise "not implemented"

    def addRoute(self, face, name):
        "Add a route."
        raise "not implemented"
