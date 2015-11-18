from Forwarder import Face,Forwarder
import atexit

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
    "NFD forwarder."
    def __init__(self, host, **params):
        Forwarder.__init__(self, host)
        self.isStarted = False
        atexit.register(self.stop)

    def start(self):
        if self.isStarted:
            raise "NFD is already started"
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

    def addFace(self, localIntf, remoteIntf):
        raise NotImplementedError

    def addRoute(self, face, name):
        raise NotImplementedError

    def setStrategy(self, prefix, strategy):
        if not self.isStarted:
            raise "setStrategy before starting: not implemented"

        out, err, exitcode = self.host.pexec('nfdc', 'set-strategy', prefix, strategy)
        if exitcode > 0:
            raise RuntimeError('nfdc error: ' + err)
