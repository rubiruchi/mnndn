class Routing:
    "NDN routing protocol."
    def __init__(self, host):
        self.host = host
        self.advertised = set() # advertised prefixes

    def start(self):
        "Start the routing daemon."
        raise NotImplementedError

    def stop(self):
        "Stop the routing daemon."
        raise NotImplementedError

    def advertise(self, prefix):
        "Advertise a prefix."
        if prefix in self.advertised:
            return
        self.doAdvertise(prefix)
        self.advertised.add(prefix)

    def withdraw(self, prefix):
        "Withdraw a prefix."
        if prefix not in self.advertised:
            return
        self.doWithdraw(prefix)
        self.advertised.remove(prefix)

    def doAdvertise(self, prefix):
        raise NotImplementedError

    def doWithdraw(self, prefix):
        raise NotImplementedError

    def getRoutes(self):
        "Return list of installed routes."
        wh = self.beginGetRoutes()
        return self.endGetRoutes(wh)

    def beginGetRoutes(self):
        raise NotImplementedError

    def endGetRoutes(self):
        raise NotImplementedError

    @staticmethod
    def isConverged(net):
        waitHandles = {}
        for host in net.hosts:
            waitHandles[host.name] = host.getRout().beginGetRoutes()
        for host in net.hosts:
            routes = set(host.getRout().endGetRoutes(waitHandles[host.name]))
            for otherHost in [ h for h in net.hosts if h != host ]:
                if not otherHost.getRout().advertised.issubset(routes):
                    return False
        return True

    @staticmethod
    def waitForConverge(net, timeout=60, interval=5):
        from time import sleep,time
        t0 = time()
        while time() < t0 + timeout:
            sleep(interval)
            if Routing.isConverged(net):
                return time() - t0
        return False
