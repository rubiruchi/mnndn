from Routing import Routing
import atexit

NLSR_CONF = """
general {
  network /net
  site site
  router %(name)s
  log-level INFO
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

class NlsrRouting(Routing):
    "NLSR routing daemon."
    def __init__(self, host, **params):
        """initialize NLSR
           advertise: [prefix]"""
        Routing.__init__(self, host)
        self.isStarted = False
        atexit.register(self.stop)

        self.advertisePrefixes = params.get('advertise', [])

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
          ) for prefix in self.advertisePrefixes
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

    def advertise(self, prefix):
        raise "not supported"

    def withdraw(self, prefix):
        raise "not supported"
