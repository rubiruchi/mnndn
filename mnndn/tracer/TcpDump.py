import atexit

class TcpDump:
    """Capture packets on a link."""
    def __init__(self, link, filt=''):
        self.link = link
        self.host = link.intf1.node
        self.filt = filt
        self.isStarted = False
        atexit.register(self.stop)

    def start(self, logFile=None):
        if self.isStarted:
            raise RuntimeError('tcpdump is already started')
        self.isStarted = True

        if logFile is None:
            logFile = '/tmp/mnndn/%s-%s.pcap' % (self.link.intf1.node.name, self.link.intf2.node.name)
        from subprocess import STDOUT
        self.process = self.host.popen('tcpdump', '-i', self.link.intf1.name, '-w', logFile, self.filt,
                                       stdout=None, stderr=STDOUT)

    def stop(self):
        if not self.isStarted:
            return
        self.process.kill()
        self.process.wait()
        self.process = None
        self.isStarted = False
