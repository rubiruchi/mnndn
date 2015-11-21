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
  prefix-update-validator {
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
    """NLSR routing daemon."""
    def __init__(self, host):
        Routing.__init__(self, host)
        self.isStarted = False
        atexit.register(self.stop)

    def __makeConfig(self):
        neighbors = []
        for (myIntf, peerIntf, ndnPeerIntfs) in self.host.getPeers():
            for ndnPeerIntf in ndnPeerIntfs:
                peerIp = ndnPeerIntf.node.IP(ndnPeerIntf)
                if peerIp is None:
                    continue
                neighbors.append(
                  NLSR_CONF_NEIGHBOR % dict(
                    name=ndnPeerIntf.node.name,
                    faceuri='udp4://%s:6363' % peerIp
                  ))
        advertising = [
          NLSR_CONF_ADVERTISING % dict(
            prefix=prefix
          ) for prefix in self.advertised
        ]
        return NLSR_CONF % dict(
            name=self.host.name,
            neighbors=''.join(neighbors),
            advertising=''.join(advertising)
          )

    def start(self):
        if self.isStarted:
            raise RuntimeError('NLSR is already started')
        self.isStarted = True

        configFile = self.host.openFile('/etc/ndn/nlsr.conf', 'w')
        configFile.write(self.__makeConfig())
        configFile.close()

        # clear logFile
        logFile = self.host.openFile('/var/log/ndn/nlsr.log', 'w')
        logFile.close()

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
            out, err, exitcode = self.host.pexec('nlsrc', 'advertise', prefix)
            if exitcode > 0:
                raise RuntimeError('nlsrc error: ' + err)

    def doWithdraw(self, prefix):
        if self.isStarted:
            out, err, exitcode = self.host.pexec('nlsrc', 'withdraw', prefix)
            if exitcode > 0:
                raise RuntimeError('nlsrc error: ' + err)

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
