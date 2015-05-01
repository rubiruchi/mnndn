import atexit
import os

class NdnPing:
    "NDN reachability testing client."
    def __init__(self, host, prefix, interval=1000):
        self.host = host
        self.prefix = prefix
        self.interval = interval

        self.isStarted = False
        atexit.register(self.stop)

    def start(self, logFile = None):
        if self.isStarted:
            raise "ndnping is already started"
        self.isStarted = True

        if logFile is None:
            self.log = open(os.devnull, 'wb')
        else:
            self.log = self.host.openFile(logFile, 'w')

        from subprocess import STDOUT
        self.process = self.host.popen('ndnping', '-i', str(self.interval), self.prefix,
                                       stderr=STDOUT, stdout=self.log)

    def stop(self):
        if not self.isStarted:
            return
        self.process.kill()
        self.process.wait()
        self.process = None
        self.log.close()
        self.isStarted = False

class NdnPingServer:
    "NDN reachability testing server."
    def __init__(self, host, prefix):
        self.host = host
        self.prefix = prefix

        self.isStarted = False
        atexit.register(self.stop)

    def start(self):
        if self.isStarted:
            raise "ndnpingserver is already started"
        self.isStarted = True

        self.log = open(os.devnull, 'wb')
        from subprocess import STDOUT
        self.process = self.host.popen('ndnpingserver', self.prefix,
                                       stderr=STDOUT, stdout=self.log)

    def stop(self):
        if not self.isStarted:
            return
        self.process.kill()
        self.process.wait()
        self.process = None
        self.log.close()
        self.isStarted = False
