from Forwarder import Face, Forwarder
import atexit
import re

NFD_CONF = """
general
{
}

log
{
%(logging)s
}

tables
{
  cs_max_packets %(cscapacity)d

  strategy_choice
  {
%(strategy)s
  }
}

face_system
{
  unix
  {
    path /var/run/nfd.sock
  }

  tcp
  {
    listen no
    port 6363
    enable_v4 yes
    enable_v6 yes
  }

  udp
  {
    port 6363
    enable_v4 yes
    enable_v6 no

    idle_timeout 600

    mcast %(udpmcast)s
    mcast_port 56363
    mcast_group 224.0.23.170
  }

  ether
  {
    mcast no
    mcast_group 01:00:5E:00:17:AA
  }

  websocket
  {
    listen no
    port 9696
    enable_v4 yes
    enable_v6 yes
  }
}

authorizations
{
  authorize
  {
    certfile any
    privileges
    {
      faces
      fib
      strategy-choice
    }
  }
}

rib
{
  localhost_security
  {
    trust-anchor
    {
      type any
    }
  }
}
"""

class NfdForwarder(Forwarder):
    """NFD forwarder."""
    def __init__(self, host, **params):
        self.loglevels = dict(default_level='INFO')
        self.strategyChoices = {
          '/':'/localhost/nfd/strategy/best-route',
          '/localhost':'/localhost/nfd/strategy/multicast',
          '/localhost/nfd':'/localhost/nfd/strategy/best-route',
          '/ndn/broadcast':'/localhost/nfd/strategy/multicast'
        }
        self.hasUdpMcast = True
        self.csCapacity = 4096
        self.wantCompressLog = False

        for k, v in params.iteritems():
            if hasattr(self, k):
                setattr(self, k, v)
            else:
                raise KeyError('NfdForwarder does not recognize %s option' % k)

        Forwarder.__init__(self, host)
        self.isStarted = False
        atexit.register(self.stop)

    def setLog(self, level=None, *opts, **params):
        if level is not None:
            for module in opts:
                self.loglevels[module] = level
        self.loglevels.update(params)

    def __makeConfig(self):
        logging = [ '  %s %s' % tup for tup in self.loglevels.iteritems() ]

        strategy = [ '    %s %s' % tup for tup in self.strategyChoices.iteritems() ]

        return NFD_CONF % dict(
            logging='\n'.join(logging),
            strategy='\n'.join(strategy),
            cscapacity=self.csCapacity,
            udpmcast='yes' if self.hasUdpMcast else 'no'
          )

    def start(self):
        if self.isStarted:
            raise RuntimeError('NFD is already started')
        self.isStarted = True

        configFile = self.host.openFile('/etc/ndn/nfd.conf', 'w')
        configFile.write(self.__makeConfig())
        configFile.close()

        import subprocess

        logname = '/var/log/ndn/nfd.log'
        if self.wantCompressLog:
            logname += '.xz'
        log = self.log = self.host.openFile(logname, 'w')
        self.logProcess = None
        if self.wantCompressLog:
            self.logProcess = self.host.popen('xz', stdin=subprocess.PIPE,
                                              stdout=self.log, stderr=subprocess.STDOUT)
            log = self.logProcess.stdin

        self.process = self.host.popen('nfd', '--config', '/etc/ndn/nfd.conf',
                                       stderr=subprocess.STDOUT, stdout=log)

    def stop(self):
        if not self.isStarted:
            return
        self.process.kill()
        if self.logProcess is not None:
            self.logProcess.communicate()
            try:
                self.logProcess.kill()
            except OSError:
                pass
        self.process.wait()
        if self.logProcess is not None:
            self.logProcess.wait()
        self.process = self.logProcess = None
        self.log.close()
        self.isStarted = False

    def nfdc(self, *args):
        if not self.isStarted:
            raise RuntimeError('nfdc is unavailable before starting NFD')

        out, err, exitcode = self.host.pexec('nfdc', *args)
        if exitcode > 0:
            raise RuntimeError('nfdc error: ' + err)
        return out, err, exitcode

    def addFace(self, localIntf, remoteIntf):
        remoteUri = 'udp4://%s:%d' % (remoteIntf.node.IP(remoteIntf), 6363)
        out, _, _ = self.nfdc('face', 'create', remoteUri, 'permanent')
        match = re.search(' id=(\d+)', out)
        if not match:
            raise RuntimeError('cannot parse nfdc output: ' + out)
        faceId = int(match.group(1))
        return Face(faceId, localIntf, remoteIntf)

    def addRoute(self, face, name):
        self.nfdc('route', 'add', name, str(face.id))

    def setStrategy(self, prefix, strategy):
        """Set NFD forwarding strategy.
           prefix: the namespace, or None to clear strategy setting and choose default strategy."""
        if self.isStarted:
            if prefix is None:
                raise RuntimeError('cannot clear strategy choice after starting NFD')
            self.nfdc('strategy', 'set', prefix, strategy)
        else:
            if prefix is None:
                self.strategyChoices.clear()
                prefix = '/'
            self.strategyChoices[prefix] = strategy
