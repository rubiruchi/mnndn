from Forwarder import Face, Forwarder
import atexit
import re

NFD_CONF = """
general
{
}

log
{
  default_level INFO
}

tables
{
  cs_max_packets 4096

  strategy_choice
  {
    /               /localhost/nfd/strategy/best-route
    /localhost      /localhost/nfd/strategy/broadcast
    /localhost/nfd  /localhost/nfd/strategy/best-route
    /ndn/broadcast  /localhost/nfd/strategy/broadcast
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

    keep_alive_interval 25

    mcast yes
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
        Forwarder.__init__(self, host)
        self.isStarted = False
        atexit.register(self.stop)

    def start(self):
        if self.isStarted:
            raise RuntimeError('NFD is already started')
        self.isStarted = True

        configFile = self.host.openFile('/etc/ndn/nfd.conf', 'w')
        configFile.write(NFD_CONF)
        configFile.close()

        self.log = self.host.openFile('/var/log/ndn/nfd.log', 'w')
        from subprocess import STDOUT
        self.process = self.host.popen('nfd', '--config', '/etc/ndn/nfd.conf',
                                       stderr=STDOUT, stdout=self.log)

    def stop(self):
        if not self.isStarted:
            return
        self.process.kill()
        self.process.wait()
        self.process = None
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
        out, _, _ = self.nfdc('create', '-P', remoteUri)
        match = re.search('FaceId:\s(\d+),', out)
        if not match:
            raise RuntimeError('cannot parse nfdc output: ' + out)
        faceId = int(match.group(1))
        return Face(faceId, localIntf, remoteIntf)

    def addRoute(self, face, name):
        self.nfdc('register', name, str(face.id))

    def setStrategy(self, prefix, strategy):
        self.nfdc('set-strategy', prefix, strategy)
