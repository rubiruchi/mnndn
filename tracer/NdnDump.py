import atexit

class NdnDump:
    "Capture NDN packets on a link."
    def __init__(self, link):
        self.link = link
        self.host = link.intf1.node
        self.isStarted = False
        atexit.register(self.stop)

    def start(self, logFile=None):
        if self.isStarted:
            raise "ndndump is already started"
        self.isStarted = True

        if logFile is None:
            logFile = '/tmp/mnndn/%s-%s.ndndump' % (self.link.intf1.node.name, self.link.intf2.node.name)
        self.log = open(logFile, 'w')
        from subprocess import STDOUT
        self.process = self.host.popen('ndndump', '-i', self.link.intf1.name,
                                       stderr=STDOUT, stdout=self.log)

    def stop(self):
        if not self.isStarted:
            return
        self.process.kill()
        self.process.wait()
        self.process = None
        self.log.close()
        self.isStarted = False
