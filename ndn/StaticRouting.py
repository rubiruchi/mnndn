from Routing import Routing
from topo import dijkstra

class StaticRouting(Routing):
    """Static routes setup."""
    def __init__(self, host):
        Routing.__init__(self, host)
        self.net = None

    def start(self, net):
        self.net = net
        self.routes = set() # routes in my RIB
        self.edges = set() # (downstream,upstream) pairs in order to reach me
        for _, (_, path) in dijkstra(net.topo, self.host.name).iteritems():
            path.reverse()
            for i in range(1, len(path)):
                self.edges.add((path[i-1], path[i]))

    def stop(self):
        self.net = None

    def doAdvertise(self, prefix):
        if self.net is None:
            raise RuntimeError("cannot advertise before starting")
        for dName, uName in self.edges:
            dHost, uHost = self.net[dName], self.net[uName]
            connections = dHost.connectionsTo(uHost)
            if len(connections) < 1:
                raise IndexError("no connection available from %s to %s" % (dName, uName))
            dFw, dRout = dHost.getFw(), dHost.getRout()
            if not isinstance(dRout, StaticRouting):
                continue
            dRout.routes.add(prefix)
            dFace = dFw.addFace(connections[0][0], connections[0][1])
            dFw.addRoute(dFace, prefix)

    def doWithdraw(self, prefix):
        raise NotImplementedError

    def beginGetRoutes(self):
        return None

    def endGetRoutes(self, wh):
        return self.routes
