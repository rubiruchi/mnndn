from Routing import Routing
import atexit

NLSR_CONF = """
general {
  network /net
  site site
  router %(name)s
  log-level DEBUG
  log-dir /var/log/ndn/
  seq-dir /var/log/ndn/
}

neighbors {
  %(neighbors)s
}

fib {
  max-faces-per-prefix 1
}

advertising {
  %(advertising)s
}

security {
  validator {
    trust-anchor {
      type any
    }
  }
}
"""

NLSR_CONF_NEIGHBOR = """
  neighbor {
    name /net/site/%(name)s
    face-uri %(faceuri)s
  }
"""

NLSR_CONF_ADVERTISING = """
  prefix %(prefix)s
"""

ROUTE_ORIGIN_NLSR = 128

class NlsrRouting(Routing):
    "NLSR routing daemon."
    def __init__(self, host):
        """initialize NLSR
           advertised: [prefix]"""
        Routing.__init__(self, host)
        self.isStarted = False
        atexit.register(self.stop)

    def makeConfig(self):
        neighbors = ''.join([
          NLSR_CONF_NEIGHBOR % dict(
            name=peerIntf.node.name,
            faceuri='udp4://%s:6363' % peerIntf.node.IP(str(peerIntf))
          ) for (myIntf, peerIntf) in self.host.getPeers()
        ])
        advertising = ''.join([
          NLSR_CONF_ADVERTISING % dict(
            prefix=prefix
          ) for prefix in self.advertised
        ])
        return NLSR_CONF % dict(
            name=self.host.name,
            neighbors=neighbors,
            advertising=advertising
          )

    def start(self):
        if self.isStarted:
            raise "NLSR is already started"
        self.isStarted = True

        configFile = self.host.openFile('/etc/ndn/nlsr.conf', 'w')
        configFile.write(self.makeConfig())
        configFile.close()

        self.log = self.host.openFile('/var/log/ndn/nlsr.out', 'w')
        from subprocess import STDOUT
        self.process = self.host.popen('nlsr', '-f', '/etc/ndn/nlsr.conf',
                                       stderr=STDOUT, stdout=self.log)

    def stop(self):
        if not self.isStarted:
            return
        self.process.kill()
        self.process.wait()
        self.process = None
        self.log.close()
        self.isStarted = False

    def doAdvertise(self, prefix):
        if self.isStarted:
            raise NotImplementedError('runtime advertise is not supported')

    def doWithdraw(self, prefix):
        if self.isStarted:
            raise NotImplementedError('runtime withdraw is not supported')

    def beginGetRoutes(self):
        return self.host.popen('nfd-status', '-x')

    def endGetRoutes(self, wh):
        wh.wait()
        xml, _ = wh.communicate()

        import xml.etree.ElementTree as ET
        try:
           x = ET.fromstring(xml)
        except ET.ParseError:
           return []

        ns = {'nfdstatus': 'ndn:/localhost/nfd/status/1'}
        return [
          ET.tostring(entry.find('nfdstatus:prefix', ns), method='text')
          for entry in x.iterfind('.//nfdstatus:ribEntry', ns)
          if entry.find("nfdstatus:routes/nfdstatus:route[nfdstatus:origin='%d']" % ROUTE_ORIGIN_NLSR, ns) is not None
        ]
